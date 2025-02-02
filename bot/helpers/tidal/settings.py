from dataclasses import dataclass
from typing import Optional
from bot.config import Config

@dataclass
class TidalSettings:
    """Tidal specific settings"""
    download_quality: str = Config.TIDAL_ENHANCED['DOWNLOAD_QUALITY']
    max_concurrent: int = Config.TIDAL_ENHANCED['MAX_CONCURRENT_DOWNLOADS']
    retry_attempts: int = Config.TIDAL_ENHANCED['RETRY_ATTEMPTS']
    retry_delay: int = Config.TIDAL_ENHANCED['RETRY_DELAY']
    convert_to_flac: bool = Config.TIDAL_ENHANCED['CONVERT_TO_FLAC']
    
    @classmethod
    def from_config(cls):
        """Create settings from config"""
        return cls(
            download_quality=Config.TIDAL_ENHANCED['DOWNLOAD_QUALITY'],
            max_concurrent=Config.TIDAL_ENHANCED['MAX_CONCURRENT_DOWNLOADS'],
            retry_attempts=Config.TIDAL_ENHANCED['RETRY_ATTEMPTS'],
            retry_delay=Config.TIDAL_ENHANCED['RETRY_DELAY'],
            convert_to_flac=Config.TIDAL_ENHANCED['CONVERT_TO_FLAC']
        )
