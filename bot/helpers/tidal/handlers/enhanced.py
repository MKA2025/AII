import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from bot.helpers.tidal.tidal_api import tidalapi
from bot.helpers.tidal.utils import get_stream_session, parse_mpd
from bot.helpers.tidal.metadata import get_track_metadata
from bot.helpers.utils import sanitize_filepath
from bot.helpers.message import send_message, edit_message
from bot.logger import LOGGER
from config import Config

class EnhancedTidalDownloader:
    def __init__(self):
        self.session_cache = {}
        self.metadata_cache = {}
        self.download_semaphore = asyncio.Semaphore(Config.TIDAL_MAX_CONCURRENT or 5)
        
    async def get_cached_session(self, track_data: dict) -> tuple:
        """Get cached session or create new one"""
        cache_key = f"{track_data['id']}_{track_data.get('quality', 'default')}"
        
        if cache_key in self.session_cache:
            session, expiry = self.session_cache[cache_key]
            if datetime.now() < expiry:
                return session
                
        session, quality = await get_stream_session(track_data)
        self.session_cache[cache_key] = (
            session, 
            datetime.now() + timedelta(minutes=30)
        )
        return session, quality

    async def download_track_with_retry(
        self, 
        track_id: int, 
        user: dict,
        max_retries: int = 3,
        retry_delay: int = 1
    ) -> bool:
        """Download track with retry logic"""
        for attempt in range(max_retries):
            try:
                track_data = await tidalapi.get_track(track_id)
                session, quality = await self.get_cached_session(track_data)
                
                stream_data = await tidalapi.get_stream_url(
                    track_id,
                    quality,
                    session
                )
                
                if stream_data:
                    track_meta = await get_track_metadata(
                        track_id, 
                        track_data,
                        user['r_id']
                    )
                    
                    filepath = (
                        f"{Config.DOWNLOAD_BASE_DIR}/{user['r_id']}/"
                        f"Tidal/{track_meta['albumartist']}/"
                        f"{track_meta['album']}/{track_meta['title']}"
                    )
                    filepath = sanitize_filepath(filepath)
                    
                    # Download logic here...
                    return True
                    
            except Exception as e:
                if 'Asset is not ready' in str(e) and attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                LOGGER.error(f"Download failed for track {track_id}: {str(e)}")
                raise e
                
        return False

    async def batch_download_album(
        self,
        album_id: int,
        user: dict,
        max_concurrent: int = 5
    ) -> List[bool]:
        """Download album tracks in batches"""
        try:
            album_data = await tidalapi.get_album(album_id)
            tracks_data = await tidalapi.get_album_tracks(album_id)
        except Exception as e:
            await send_message(user, f"Failed to fetch album data: {str(e)}")
            return []

        download_tasks = []
        results = []
        
        for track in tracks_data['items']:
            async with self.download_semaphore:
                task = asyncio.create_task(
                    self.download_track_with_retry(
                        track['id'],
                        user
                    )
                )
                download_tasks.append(task)
                
                # Process in smaller batches
                if len(download_tasks) >= max_concurrent:
                    batch_results = await asyncio.gather(
                        *download_tasks, 
                        return_exceptions=True
                    )
                    results.extend(batch_results)
                    download_tasks = []
                    
        # Process remaining tasks
        if download_tasks:
            batch_results = await asyncio.gather(
                *download_tasks,
                return_exceptions=True
            )
            results.extend(batch_results)
            
        return results
