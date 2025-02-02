import os
import logging
from os import getenv
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
LOGGER = logging.getLogger(__name__)

if not os.environ.get("ENV"):
    load_dotenv('.env', override=True)

class Config(object):
    # Existing configs...
    
    # Tidal Enhanced Settings
    TIDAL_ENHANCED = {
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
        'PUBLIC_ACCESS': True,
        'ALLOWED_SETTINGS': ['zip_enabled', 'max_zip_size']
    }

    # Your existing config settings...
    TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
    APP_ID = int(getenv("APP_ID"))
    API_HASH = getenv("API_HASH")
    DATABASE_URL = getenv("DATABASE_URL")
    BOT_USERNAME = getenv("BOT_USERNAME")
    ADMINS = set(int(x) for x in getenv("ADMINS").split())

    # Working directories
    WORK_DIR = getenv("WORK_DIR", "./bot/")
    DOWNLOADS_FOLDER = getenv("DOWNLOADS_FOLDER", "DOWNLOADS")
    DOWNLOAD_BASE_DIR = WORK_DIR + DOWNLOADS_FOLDER
    LOCAL_STORAGE = getenv("LOCAL_STORAGE", DOWNLOAD_BASE_DIR)

    # Naming formats
    PLAYLIST_NAME_FORMAT = getenv("PLAYLIST_NAME_FORMAT", "{title} - Playlist")
    TRACK_NAME_FORMAT = getenv("TRACK_NAME_FORMAT", "{title} - {artist}")

    # Tidal settings
    ENABLE_TIDAL = getenv("ENABLE_TIDAL", None)
    TIDAL_MOBILE = getenv("TIDAL_MOBILE", None)
    TIDAL_MOBILE_TOKEN = getenv("TIDAL_MOBILE_TOKEN", None)
    TIDAL_ATMOS_MOBILE_TOKEN = getenv("TIDAL_ATMOS_MOBILE_TOKEN", None)
    TIDAL_TV_TOKEN = getenv("TIDAL_TV_TOKEN", None)
    TIDAL_TV_SECRET = getenv("TIDAL_TV_SECRET", None)
    TIDAL_CONVERT_M4A = getenv("TIDAL_CONVERT_M4A", False)

    # Concurrent settings
    MAX_WORKERS = int(getenv("MAX_WORKERS", 5))
