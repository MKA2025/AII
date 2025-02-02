import asyncio
import aiohttp
import os
import time
from typing import List, Optional
from pathlib import Path

from bot.config import Config
from bot.logger import LOGGER
from bot.helpers.utils.format import format_size, format_time
from bot.helpers.tidal.tidal_api import tidalapi
from bot.helpers.utils import format_string

class EnhancedDownloader:
    def __init__(self):
        self.config = Config.TIDAL_SETTINGS
        self._rate_limit = 50  # Requests per minute
        self._request_times = []
        self._download_semaphore = asyncio.Semaphore(
            Config.MAX_CONCURRENT_DOWNLOADS
        )
        self._progress_callback = None
        
    async def _check_rate_limit(self):
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        if len(self._request_times) >= self._rate_limit:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                
        self._request_times.append(now)

    async def set_progress_callback(self, callback):
        self._progress_callback = callback

    async def _report_progress(self, current: int, total: int, message=None):
        if self._progress_callback:
            progress = (current / total) * 100
            speed = current / (time.time() - self._start_time) if hasattr(self, '_start_time') else 0
            
            await self._progress_callback(
                current=current,
                total=total,
                speed=speed,
                progress=progress,
                message=message
            )

    async def download_track(
        self,
        track_id: int,
        output_dir: str,
        quality: str = None,
        message = None
    ) -> Optional[str]:
        """Download a single track with retry logic and progress reporting"""
        await self._check_rate_limit()
        quality = quality or self.config['QUALITY']
        self._start_time = time.time()
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                async with self._download_semaphore:
                    # Get track metadata
                    track_data = await tidalapi.get_track(track_id)
                    if not track_data:
                        raise Exception(f"Could not get metadata for track {track_id}")

                    # Get stream URL
                    stream_data = await tidalapi.get_stream_url(
                        track_id,
                        quality,
                        self.client.session
                    )
                    
                    if not stream_data:
                        raise Exception(f"No stream data for track {track_id}")

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
                            total_size = int(response.headers.get('content-length', 0))
                            current_size = 0

                            async with aiofiles.open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(Config.CHUNK_SIZE):
                                    await f.write(chunk)
                                    current_size += len(chunk)
                                    
                                    if message and (time.time() - self._last_progress_update) > Config.PROGRESS_UPDATE_DELAY:
                                        await self._report_progress(current_size, total_size, message)
                                        self._last_progress_update = time.time()

                    return filepath

            except Exception as e:
                LOGGER.error(f"Download attempt {attempt + 1} failed for track {track_id}: {str(e)}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    raise e

        return None

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
            
            for i, track in enumerate(tracks_data['items']):
                if message:
                    await message.edit_text(f"Downloading track {i+1}/{total_tracks}")
                
                task = self.download_track(
                    track['id'],
                    album_folder,
                    self.config['QUALITY'],
                    message
                )
                download_tasks.append(task)
                
            downloaded_files = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Handle failures
            failed_tracks = [i for i, result in enumerate(downloaded_files) if isinstance(result, Exception)]
            if failed_tracks:
                LOGGER.error(f"Failed to download tracks: {failed_tracks}")
                
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
            raise e
