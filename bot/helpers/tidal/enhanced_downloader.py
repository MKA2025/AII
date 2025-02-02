import asyncio
import aiofiles
import aiohttp
import os
import time
from typing import List, Optional
from pathlib import Path
from bot.config import Config
from bot.logger import LOGGER
from bot.helpers.cache import CacheManager
from bot.helpers.rate_limiter import RateLimiter
from bot.helpers.utils.format import format_size, format_time
from bot.helpers.tidal.tidal_api import tidalapi
from bot.helpers.utils import format_string

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
        self.client = None  # Will be set when needed
        self._last_progress_update = 0

    async def _check_memory(self, size: int) -> bool:
        """Check if enough memory available"""
        current_usage = sum(len(item) for item in self._memory_pool)
        return (current_usage + size) <= self._max_memory

    async def _clear_memory(self):
        """Clear memory pool"""
        while self._memory_pool:
            item = self._memory_pool.pop()
            del item

    async def set_progress_callback(self, callback):
        self._progress_callback = callback

    async def _report_progress(self, current: int, total: int, message=None):
        """Report download progress"""
        if self._progress_callback:
            now = time.time()
            if now - self._last_progress_update >= Config.PERFORMANCE['PROGRESS_UPDATE_DELAY']:
                progress = (current / total) * 100
                speed = current / (now - self._start_time) if hasattr(self, '_start_time') else 0
                
                await self._progress_callback(
                    current=current,
                    total=total,
                    speed=speed,
                    progress=progress,
                    message=message
                )
                self._last_progress_update = now

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

    async def download_track(
        self,
        track_id: int,
        output_dir: str,
        quality: str = None,
        message = None
    ) -> Optional[str]:
        """Download track with improved error handling and caching"""
        try:
            # Check cache first
            cache_key = f"track_{track_id}_{quality}"
            cached_path = await self.cache.get(cache_key)
            if cached_path and os.path.exists(cached_path):
                return cached_path

            # Rate limiting
            await self.rate_limiter.wait()

            async with self._download_semaphore:
                # Get track metadata
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

                        # Check memory availability
                        if not await self._check_memory(total_size):
                            await self._clear_memory()

                        current_size = 0
                        self._start_time = time.time()
                        self._last_progress_update = 0

                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(
                                Config.PERFORMANCE['CHUNK_SIZE']
                            ):
                                if not chunk:
                                    break

                                await f.write(chunk)
                                current_size += len(chunk)
                                self._memory_pool.append(chunk)

                                if message:
                                    await self._report_progress(
                                        current_size,
                                        total_size,
                                        message
                                    )

                # Cache successful download
                await self.cache.set(cache_key, filepath)
                return filepath

        except Exception as e:
            LOGGER.error(f"Download failed for track {track_id}: {str(e)}")
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
        """Download full album with optional ZIP and progress reporting"""
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
                    await message.edit_text("Creating ZIP file...")

                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()

                zip_path = f"{album_folder}.zip"
                zip_files = await zipper.create_zip(
                    [f for f in downloaded_files if isinstance(f, str)],
                    zip_path,
                    Config.ZIP_SETTINGS['MAX_SIZE']
                )

                # Clean up original files
                for file in downloaded_files:
                    if isinstance(file, str) and os.path.exists(file):
                        os.remove(file)

                return zip_files

            return [f for f in downloaded_files if isinstance(f, str)]

        except Exception as e:
            LOGGER.error(f"Album download failed: {str(e)}")
            if message:
                await message.edit_text(f"❌ Download failed: {str(e)}")
            raise
