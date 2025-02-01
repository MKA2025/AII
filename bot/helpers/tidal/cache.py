import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import OrderedDict

class TidalCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.metadata_cache: OrderedDict = OrderedDict()
        self.session_cache: Dict = {}
        self.stream_cache: Dict = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the cache cleanup loop"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
    async def stop(self):
        """Stop the cache cleanup loop"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            
    async def _cleanup_loop(self):
        """Periodically clean expired cache entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
                
    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        
        # Clean metadata cache
        expired_keys = [
            k for k, v in self.metadata_cache.items()
            if now - v['timestamp'] > timedelta(hours=1)
        ]
        for k in expired_keys:
            del self.metadata_cache[k]
            
        # Clean session cache
        expired_keys = [
            k for k, v in self.session_cache.items()
            if now > v['expiry']
        ]
        for k in expired_keys:
            del self.session_cache[k]
            
    async def get_metadata(self, key: str) -> Optional[Dict]:
        """Get metadata from cache"""
        if key in self.metadata_cache:
            entry = self.metadata_cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(hours=1):
                return entry['data']
        return None
        
    async def set_metadata(self, key: str, data: Dict):
        """Set metadata in cache"""
        if len(self.metadata_cache) >= self.max_size:
            # Remove oldest entry
            self.metadata_cache.popitem(last=False)
            
        self.metadata_cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
