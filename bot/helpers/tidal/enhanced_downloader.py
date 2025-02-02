import asyncio
import aiofiles
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from bot.config import Config
from bot.logger import LOGGER
from bot.helpers.utils import format_string
from bot.helpers.tidal.enhanced_client import EnhancedTidalClient
from bot.helpers.tidal.tidal_api import tidalapi

class EnhancedDownloader:
    def __init__(self, client: Optional[EnhancedTidalClient] = None):
        self.client = client or EnhancedTidalClient()
        self.config = Config.TIDAL_ENHANCED
        self.download_semaphore = asyncio.Semaphore(
            self.config['MAX_CONCURRENT_DOWNLOADS']
        )
        
    async def download_track(
        self,
        track_id: int,
        output_dir: str,
        quality: str = None
    ) -> Optional[str]:
        """Download a single track with retry logic"""
        quality = quality or self.config['DOWNLOAD_QUALITY']
        
        for attempt in range(self.config['RETRY_ATTEMPTS']):
            try:
                async with self.download_semaphore:
                    # Get track metadata
                    track_data = await tidalapi.get_track(track_id)
                    
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
                        extension='.flac' if self.config['CONVERT_TO_FLAC'] else '.m4a'
                    )
                    filepath = os.path.join(output_dir, filename)
                    
                    # Download file
                    async with aiofiles.open(filepath, 'wb') as f:
                        async with self.client.session.get(stream_data['url']) as response:
                            while chunk := await response.content.read(self.config['CHUNK_SIZE']):
                                await f.write(chunk)
                                
                    return filepath
                    
            except Exception as e:
                LOGGER.error(f"Download attempt {attempt + 1} failed for track {track_id}: {str(e)}")
                if attempt < self.config['RETRY_ATTEMPTS'] - 1:
                    await asyncio.sleep(self.config['RETRY_DELAY'] * (attempt + 1))
                else:
                    raise e
                    
        return None

    async def download_album(
        self,
        album_id: int,
        user_id: str,
        zip_enabled: bool = True
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
            for track in tracks_data['items']:
                task = self.download_track(
                    track['id'],
                    album_folder,
                    self.config['DOWNLOAD_QUALITY']
                )
                download_tasks.append(task)
                
            downloaded_files = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # Handle ZIP if enabled
            if zip_enabled and Config.ZIP_SETTINGS['ENABLED']:
                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()
                
                zip_path = f"{album_folder}.zip"
                await zipper.create_zip(
                    downloaded_files,
                    zip_path,
                    Config.ZIP_SETTINGS['MAX_SIZE']
                )
                
                # Clean up original files
                for file in downloaded_files:
                    if os.path.exists(file):
                        os.remove(file)
                        
                return [zip_path]
                
            return downloaded_files
            
        except Exception as e:
            LOGGER.error(f"Album download failed: {str(e)}")
            raise e
