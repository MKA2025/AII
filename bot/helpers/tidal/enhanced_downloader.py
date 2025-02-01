import asyncio
import aiofiles
import os
from typing import List, Dict, Optional
from datetime import datetime

from bot.helpers.tidal.enhanced_client import EnhancedTidalClient
from bot.helpers.tidal.config import TidalConfig
from bot.helpers.utils import sanitize_filepath
from bot.logger import LOGGER

class EnhancedDownloader:
    def __init__(
        self,
        client: EnhancedTidalClient,
        config: Optional[TidalConfig] = None
    ):
        self.client = client
        self.config = config or TidalConfig()
        self.download_semaphore = asyncio.Semaphore(
            self.config.MAX_CONCURRENT_DOWNLOADS
        )
        
    async def download_file(
        self,
        url: str,
        filepath: str,
        chunk_size: int = 8192
    ) -> bool:
        """Download a file with progress tracking"""
        try:
            async with self.client.session.get(url) as response:
                response.raise_for_status()
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Download file
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        
            return True
            
        except Exception as e:
            LOGGER.error(f"Download failed for {url}: {str(e)}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
            
    async def process_track(
        self,
        track_id: int,
        output_dir: str,
        quality: str = 'HI_RES'
    ) -> Optional[str]:
        """Process and download a single track"""
        try:
            async with self.download_semaphore:
                # Get track metadata
                track_data = await self.client.get_track(track_id)
                
                # Get download URL
                stream_url = await self.client.get_stream_url(
                    track_id,
                    quality
                )
                
                if not stream_url:
                    return None
                    
                # Prepare filepath
                filename = sanitize_filepath(
                    f"{track_data['title']}.{track_data['format']}"
                )
                filepath = os.path.join(output_dir, filename)
                
                # Download file
                success = await self.download_file(
                    stream_url,
                    filepath,
                    self.config.CHUNK_SIZE
                )
                
                if success:
                    return filepath
                return None
                
        except Exception as e:
            LOGGER.error(f"Failed to process track {track_id}: {str(e)}")
            return None
