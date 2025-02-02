import time
import asyncio
from typing import Optional
from bot.config import Config
from bot.logger import LOGGER

class RateLimiter:
    def __init__(
        self,
        max_requests: int = 50,
        window: int = 60,
        burst: int = 10
    ):
        self.max_requests = max_requests
        self.window = window
        self.burst = burst
        self.requests = []
        self.burst_tokens = burst
        self.last_token_time = time.time()
        self._lock = asyncio.Lock()
        
    async def acquire(self, weight: int = 1) -> bool:
        """
        Acquire rate limit permission
        Args:
            weight: Request weight (default 1)
        Returns:
            bool: True if acquired, False if would exceed limit
        """
        async with self._lock:
            now = time.time()
            
            # Update burst tokens
            time_passed = now - self.last_token_time
            new_tokens = int(time_passed * (self.burst / self.window))
            self.burst_tokens = min(self.burst, self.burst_tokens + new_tokens)
            self.last_token_time = now
            
            # Clean old requests
            self.requests = [req for req in self.requests if now - req < self.window]
            
            # Check if would exceed limit
            if len(self.requests) + weight > self.max_requests:
                if self.burst_tokens >= weight:
                    self.burst_tokens -= weight
                else:
                    return False
                    
            # Add new request(s)
            self.requests.extend([now] * weight)
            return True
            
    async def wait(self, weight: int = 1):
        """
        Wait until rate limit allows request
        Args:
            weight: Request weight (default 1)
        """
        while True:
            if await self.acquire(weight):
                return
            await asyncio.sleep(0.1)
