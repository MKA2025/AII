from dataclasses import dataclass
from typing import Optional

@dataclass
class TidalConfig:
    """Tidal specific configuration"""
    MAX_CONCURRENT_DOWNLOADS: int = 5
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 1
    SESSION_CACHE_TIME: int = 1800  # 30 minutes
    RATE_LIMIT_PER_MINUTE: int = 50
    DOWNLOAD_QUALITY: str = 'HI_RES'
    CONVERT_TO_FLAC: bool = True
    
    # Cache settings
    METADATA_CACHE_SIZE: int = 1000
    METADATA_CACHE_TTL: int = 3600  # 1 hour
    SESSION_CACHE_TTL: int = 1800   # 30 minutes
    
    # Download settings
    CHUNK_SIZE: int = 8192
    TIMEOUT: int = 30
    
    def __post_init__(self):
        """Validate configuration"""
        if self.MAX_CONCURRENT_DOWNLOADS < 1:
            raise ValueError("MAX_CONCURRENT_DOWNLOADS must be >= 1")
        if self.RATE_LIMIT_PER_MINUTE < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be >= 1")
