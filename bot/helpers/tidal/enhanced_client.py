from typing import Optional, Dict, Any
import aiohttp
import asyncio
from datetime import datetime

from bot.helpers.tidal.cache import TidalCache
from bot.helpers.tidal.config import TidalConfig
from bot.logger import LOGGER

class EnhancedTidalClient:
    def __init__(self, config: Optional[TidalConfig] = None):
        self.config = config or TidalConfig()
        self.cache = TidalCache(max_size=self.config.METADATA_CACHE_SIZE)
        self.rate_limiter = asyncio.Semaphore(self.config.RATE_LIMIT_PER_MINUTE)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """Initialize the client"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    limit=self.config.MAX_CONCURRENT_DOWNLOADS,
                    ttl_dns_cache=300
                )
            )
            await self.cache.start()
            
    async def stop(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
        await self.cache.stop()
        
    async def _make_request(
        self, 
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request with rate limiting"""
        async with self.rate_limiter:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
                
    async def get_track(self, track_id: int) -> Dict[str, Any]:
        """Get track metadata with caching"""
        cache_key = f"track_{track_id}"
        
        # Try cache first
        if cached := await self.cache.get_metadata(cache_key):
            return cached
            
        # Make API request
        data = await self._make_request(
            "GET",
            f"tracks/{track_id}"
        )
        
        # Cache result
        await self.cache.set_metadata(cache_key, data)
        return data
