import os
from typing import Dict, Any

class Config:
    # Existing config...
    
    # Tidal Enhanced Settings
    TIDAL_ENHANCED: Dict[str, Any] = {
        'MAX_CONCURRENT_DOWNLOADS': 5,
        'RETRY_ATTEMPTS': 3,
        'RETRY_DELAY': 1,
        'SESSION_CACHE_TIME': 1800,  # 30 minutes
        'RATE_LIMIT_PER_MINUTE': 50,
        'DOWNLOAD_QUALITY': 'HI_RES',
        'CONVERT_TO_FLAC': True,
        'METADATA_CACHE_SIZE': 1000
    }

    # ZIP Feature Settings
    ZIP_SETTINGS = {
        'ENABLED': True,
        'MAX_SIZE': 2000000000,  # 2GB default
        'CHUNK_SIZE': 8192,
        'PUBLIC_ACCESS': True
    }

    # Base paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOWNLOAD_BASE_DIR = os.path.join(BASE_DIR, 'downloads')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')

    # Create required directories
    os.makedirs(DOWNLOAD_BASE_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
