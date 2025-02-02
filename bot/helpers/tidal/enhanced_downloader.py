import asyncio
import aiohttp
import aiofiles
import os
import time
from typing import List, Optional
from pathlib import Path
from bot.config import Config
from bot.logger import LOGGER
from bot.helpers.cache import CacheManager
from bot.helpers.rate_limiter import RateLimiter
from bot.helpers.utils import format_size, format_time, format_string
from bot.helpers.tidal.tidal_api import tidalapi
from bot.helpers.translations import lang

class EnhancedDownloader:
    def __init__(self):
        self.config = Config.TIDAL_SETTINGS
        self.cache = CacheManager()
        self.rate_limiter = RateLimiter(
            max_requests=Config.SECURITY['RATE_LIMIT']['MAX_REQUESTS'],
            window=Config.SECURITY['RATE_LIMIT']['WINDOW'],
            burst=Config.SECURITY['RATE_LIMIT']['BURST']
        )
        self._download_semaphore = asyncio.Semaphore(
            Config.PERFORMANCE['MAX_CONCURRENT_DOWNLOADS']
        )
        self._progress_callback = None
        self._memory_pool = []
        self._max_memory = Config.PERFORMANCE['MEMORY_LIMIT']
        self.client = None
        self._last_progress_update = 0
        self._start_time = time.time()

    async def _check_memory(self, size: int) -> bool:
        """Check if enough memory available"""
        current_usage = sum(len(item) for item in self._memory_pool)
        return (current_usage + size) <= self._max_memory

    async def _clear_memory(self):
        """Clear memory pool"""
        while self._memory_pool:
            self._memory_pool.pop()

    async def _report_progress(self, current: int, total: int, message=None):
        """Report download progress"""
        now = time.time()
        if now - self._last_progress_update >= Config.PERFORMANCE['PROGRESS_UPDATE_DELAY']:
            progress = (current * 100) / total
            speed = current / (now - self._start_time)
            elapsed = now - self._start_time
            eta = (total - current) / speed if speed > 0 else 0

            status_text = lang.s.DOWNLOADING.format(
                format_size(speed),
                format_size(current),
                format_size(total),
                format_time(eta)
            )

            if message:
                await message.edit_text(
                    f"{lang.s.PROGRESS_BAR.format('█' * int(progress/5), progress, '░' * (20-int(progress/5)))}"
                    f"{status_text}"
                )

            self._last_progress_update = now

    async def download_track(
        self,
        track_id: int,
        output_dir: str,
        quality: str = None,
        message = None
    ) -> Optional[str]:
        """Download track with retries and error handling"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                # Rate limiting
                await self.rate_limiter.wait()

                async with self._download_semaphore:
                    # Get track metadata with caching
                    track_data = await self._get_track_metadata(track_id)
                    if not track_data:
                        raise ValueError(f"Could not get metadata for track {track_id}")

                    # Get stream URL with quality fallback
                    stream_data = await self._get_stream_url(track_id, quality or self.config['QUALITY'])
                    if not stream_data:
                        raise ValueError(f"No stream data for track {track_id}")

                    # Prepare filepath
                    filename = format_string(
                        Config.TRACK_NAME_FORMAT,
                        track_data,
                        extension='.flac' if self.config['CONVERT_M4A'] else '.m4a'
                    )
                    filepath = os.path.join(output_dir, filename)

                    # Download with progress
                    async with aiohttp.ClientSession() as session:
                        async with session.get(stream_data['url']) as response:
                            if not response.ok:
                                raise aiohttp.ClientError(
                                    f"Download failed with status {response.status}"
                                )

                            total_size = int(response.headers.get('content-length', 0))
                            if total_size > Config.SECURITY['MAX_FILE_SIZE']:
                                raise ValueError(f"File size exceeds limit: {format_size(total_size)}")

                            current_size = 0
                            self._start_time = time.time()
                            self._last_progress_update = 0

                            async with aiofiles.open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(Config.PERFORMANCE['CHUNK_SIZE']):
                                    if not chunk:
                                        break

                                    if not await self._check_memory(len(chunk)):
                                        await self._clear_memory()

                                    await f.write(chunk)
                                    current_size += len(chunk)
                                    self._memory_pool.append(chunk)

                                    if message:
                                        await self._report_progress(
                                            current_size,
                                            total_size,
                                            message
                                        )

                            # Clear memory after download
                            await self._clear_memory()

                    return filepath

            except Exception as e:
                LOGGER.error(f"Download attempt {attempt + 1} failed for track {track_id}: {str(e)}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    raise

    async def download_album(
        self,
        album_id: int,
        user_id: str,
        zip_enabled: bool = True,
        message = None
    ) -> List[str]:
        """Download full album with optional ZIP"""
        try:
            # Get album metadata
            album_data = await tidalapi.get_album(album_id)
            tracks_data = await tidalapi.get_album_tracks(album_id)

            # Prepare download location
            album_folder = os.path.join(
                Config.DOWNLOAD_BASE_DIR,
                user_id,
                'Tidal',
                format_string(album_data['artist']['name']),
                format_string(album_data['title'])
            )
            os.makedirs(album_folder, exist_ok=True)

            # Download all tracks
            download_tasks = []
            total_tracks = len(tracks_data['items'])

            for i, track in enumerate(tracks_data['items'], 1):
                if message:
                    await message.edit_text(
                        f"Downloading track {i}/{total_tracks}\n"
                        f"Title: {track.get('title', 'Unknown')}"
                    )

                task = self.download_track(
                    track['id'],
                    album_folder,
                    self.config['QUALITY'],
                    message
                )
                download_tasks.append(task)

            downloaded_files = await asyncio.gather(*download_tasks, return_exceptions=True)

            # Handle failures
            failed_tracks = [
                (i, result) for i, result in enumerate(downloaded_files)
                if isinstance(result, Exception)
            ]
            if failed_tracks:
                error_msg = "\n".join(
                    f"Track {i+1}: {str(error)}" for i, error in failed_tracks
                )
                LOGGER.error(f"Failed tracks:\n{error_msg}")

            # Handle ZIP if enabled
            if zip_enabled and Config.ZIP_SETTINGS['ENABLED']:
                if message:
                    await message.edit_text(lang.s.ZIPPING)

                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()

                zip_path = f"{album_folder}.zip"
                zip_files = await zipper.create_zip(
                    [f for f in downloaded_files if isinstance(f, str)],
                    zip_path,
                    split_size=Config.ZIP_SETTINGS['SPLIT_SIZE'],
                    message=message
                )

                # Clean up original files if zip successful
                if zip_files:
                    for file in downloaded_files:
                        if isinstance(file, str) and os.path.exists(file):
                            os.remove(file)

                    return zip_files

            return [f for f in downloaded_files if isinstance(f, str)]

        except Exception as e:
            LOGGER.error(f"Album download failed: {str(e)}")
            if message:
                await message.edit_text(f"❌ {str(e)}")
            raise

    async def _get_track_metadata(self, track_id: int):
        """Get track metadata with caching"""
        cache_key = f"metadata_{track_id}"
        metadata = await self.cache.get(cache_key)
        if metadata:
            return metadata

        metadata = await tidalapi.get_track(track_id)
        if metadata:
            await self.cache.set(cache_key, metadata)
        return metadata

    async def _get_stream_url(self, track_id: int, quality: str):
        """Get stream URL with quality fallback"""
        qualities = ['HI_RES', 'LOSSLESS', 'HIGH', 'LOW']
        if quality not in qualities:
            quality = qualities[0]

        for q in qualities[qualities.index(quality):]:
            try:
                stream_data = await tidalapi.get_stream_url(
                    track_id,
                    q,
                    self.client.session
                )
                if stream_data:
                    return stream_data
            except Exception as e:
                LOGGER.warning(f"Failed to get stream URL for quality {q}: {str(e)}")
                continue
        return None

    async def download_playlist(
        self,
        playlist_id: int,
        user_id: str,
        zip_enabled: bool = True,
        message = None
    ) -> List[str]:
        """Download playlist with optional ZIP"""
        try:
            # Get playlist metadata
            playlist_data = await tidalapi.get_playlist(playlist_id)
            tracks_data = await tidalapi.get_playlist_tracks(playlist_id)

            # Prepare download location
            playlist_folder = os.path.join(
                Config.DOWNLOAD_BASE_DIR,
                user_id,
                'Tidal',
                'Playlists',
                format_string(playlist_data['title'])
            )
            os.makedirs(playlist_folder, exist_ok=True)

            # Download all tracks
            download_tasks = []
            total_tracks = len(tracks_data['items'])

            for i, track in enumerate(tracks_data['items'], 1):
                if message:
                    await message.edit_text(
                        f"Downloading track {i}/{total_tracks}\n"
                        f"Title: {track.get('title', 'Unknown')}"
                    )

                task = self.download_track(
                    track['id'],
                    playlist_folder,
                    self.config['QUALITY'],
                    message
                )
                download_tasks.append(task)

            if Config.PERFORMANCE['MAX_CONCURRENT_DOWNLOADS'] > 1:
                downloaded_files = await asyncio.gather(*download_tasks, return_exceptions=True)
            else:
                # Sequential download if concurrent downloads not enabled
                downloaded_files = []
                for task in download_tasks:
                    try:
                        result = await task
                        downloaded_files.append(result)
                    except Exception as e:
                        downloaded_files.append(e)

            # Handle failures
            failed_tracks = [
                (i, result) for i, result in enumerate(downloaded_files)
                if isinstance(result, Exception)
            ]
            if failed_tracks:
                error_msg = "\n".join(
                    f"Track {i+1}: {str(error)}" for i, error in failed_tracks
                )
                LOGGER.error(f"Failed tracks:\n{error_msg}")

            # Handle ZIP if enabled
            if zip_enabled and Config.ZIP_SETTINGS['ENABLED']:
                if message:
                    await message.edit_text(lang.s.ZIPPING)

                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()

                zip_path = f"{playlist_folder}.zip"
                successful_files = [f for f in downloaded_files if isinstance(f, str)]

                if successful_files:
                    zip_files = await zipper.create_zip(
                        successful_files,
                        zip_path,
                        split_size=Config.ZIP_SETTINGS['SPLIT_SIZE'],
                        message=message
                    )

                    # Clean up original files if zip successful
                    if zip_files:
                        for file in successful_files:
                            try:
                                if os.path.exists(file):
                                    os.remove(file)
                            except Exception as e:
                                LOGGER.error(f"Failed to remove file {file}: {str(e)}")

                        return zip_files

            return [f for f in downloaded_files if isinstance(f, str)]

        except Exception as e:
            LOGGER.error(f"Playlist download failed: {str(e)}")
            if message:
                await message.edit_text(f"❌ {str(e)}")
            raise

    async def download_artist(
        self,
        artist_id: int,
        user_id: str,
        zip_enabled: bool = True,
        message = None
    ) -> List[str]:
        """Download artist's albums with optional ZIP"""
        try:
            # Get artist metadata
            artist_data = await tidalapi.get_artist(artist_id)
            albums_data = await tidalapi.get_artist_albums(artist_id)

            # Prepare download location
            artist_folder = os.path.join(
                Config.DOWNLOAD_BASE_DIR,
                user_id,
                'Tidal',
                'Artists',
                format_string(artist_data['name'])
            )
            os.makedirs(artist_folder, exist_ok=True)

            # Download all albums
            all_files = []
            total_albums = len(albums_data['items'])

            for i, album in enumerate(albums_data['items'], 1):
                if message:
                    await message.edit_text(
                        f"Downloading album {i}/{total_albums}\n"
                        f"Album: {album.get('title', 'Unknown')}"
                    )

                try:
                    album_files = await self.download_album(
                        album['id'],
                        user_id,
                        zip_enabled=False,  # Don't zip individual albums
                        message=message
                    )
                    all_files.extend(album_files)
                except Exception as e:
                    LOGGER.error(f"Failed to download album {album['id']}: {str(e)}")
                    continue

            # Handle ZIP if enabled
            if zip_enabled and Config.ZIP_SETTINGS['ENABLED'] and all_files:
                if message:
                    await message.edit_text(lang.s.ZIPPING)

                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()

                zip_path = f"{artist_folder}.zip"
                zip_files = await zipper.create_zip(
                    all_files,
                    zip_path,
                    split_size=Config.ZIP_SETTINGS['SPLIT_SIZE'],
                    message=message
                )

                # Clean up original files if zip successful
                if zip_files:
                    for file in all_files:
                        try:
                            if os.path.exists(file):
                                os.remove(file)
                        except Exception as e:
                            LOGGER.error(f"Failed to remove file {file}: {str(e)}")

                    return zip_files

            return all_files

        except Exception as e:
            LOGGER.error(f"Artist download failed: {str(e)}")
            if message:
                await message.edit_text(f"❌ {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        await self._clear_memory()
        await self.cache.cleanup()
