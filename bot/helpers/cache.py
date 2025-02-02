import time
import asyncio
from typing import Any, Optional
from bot.config import Config
from bot.logger import LOGGER

class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._cache = {}
        self._expire_times = {}
        self._max_size = Config.METADATA_CACHE_SIZE
        self._cleanup_task = None
        self._lock = asyncio.Lock()
        
    async def start(self):
        """Start cache cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
    async def stop(self):
        """Stop cache cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            
    async def _cleanup_loop(self):
        """Periodic cleanup of expired items"""
        while True:
            try:
                await asyncio.sleep(Config.CACHE_CLEANUP_INTERVAL)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                LOGGER.error(f"Cache cleanup error: {str(e)}")
                
    async def _cleanup_expired(self):
        """Remove expired items from cache"""
        now = time.time()
        async with self._lock:
            expired_keys = [
                key for key, expire_time in self._expire_times.items()
                if now >= expire_time
            ]
            for key in expired_keys:
                del self._cache[key]
                del self._expire_times[key]
                
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        async with self._lock:
            if key in self._cache:
                if time.time() < self._expire_times[key]:
                    return self._cache[key]
                else:
                    del self._cache[key]
                    del self._expire_times[key]
        return None
        
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = Config.SESSION_CACHE_DURATION
    ):
        """Set item in cache with TTL"""
        async with self._lock:
            if len(self._cache) >= self._max_size:
                oldest_key = min(self._expire_times, key=self._expire_times.get)
                del self._cache[oldest_key]
                del self._expire_times[oldest_key]
                
            self._cache[key] = value
            self._expire_times[key] = time.time() + ttl
            
    async def delete(self, key: str):
        """Delete item from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._expire_times[key]
