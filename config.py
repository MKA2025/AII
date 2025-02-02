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
    #--------------------
    # MAIN BOT VARIABLES
    #--------------------
    try:
        TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
        APP_ID = int(getenv("APP_ID"))
        API_HASH = getenv("API_HASH")
        DATABASE_URL = getenv("DATABASE_URL")
        BOT_USERNAME = getenv("BOT_USERNAME")
        ADMINS = set(int(x) for x in getenv("ADMINS").split())
    except:
        LOGGER.warning("BOT : Essential Configs are missing")
        exit(1)

    #--------------------
    # BOT WORKING DIRECTORY
    #--------------------
    WORK_DIR = getenv("WORK_DIR", "./bot/")
    DOWNLOADS_FOLDER = getenv("DOWNLOADS_FOLDER", "DOWNLOADS")
    DOWNLOAD_BASE_DIR = WORK_DIR + DOWNLOADS_FOLDER
    LOCAL_STORAGE = getenv("LOCAL_STORAGE", DOWNLOAD_BASE_DIR)

    #--------------------
    # PERFORMANCE SETTINGS
    #--------------------
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for downloads
    BUFFER_SIZE = 10  # Number of chunks to buffer
    PROGRESS_UPDATE_DELAY = 10  # Seconds between progress updates
    MAX_CONCURRENT_DOWNLOADS = 5

    #--------------------
    # CACHE SETTINGS
    #--------------------
    METADATA_CACHE_SIZE = 1000
    SESSION_CACHE_DURATION = 1800  # 30 minutes
    CACHE_CLEANUP_INTERVAL = 3600  # 1 hour

    #--------------------
    # ERROR HANDLING
    #--------------------
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    RETRY_BACKOFF = 2

    #--------------------
    # ZIP SETTINGS
    #--------------------
    ZIP_SETTINGS = {
        'ENABLED': True,
        'MAX_SIZE': 2000000000,  # 2GB default
        'CHUNK_SIZE': 8192,
        'PUBLIC_ACCESS': True,
        'ALLOWED_SETTINGS': ['zip_enabled', 'max_zip_size'],
        'COMPRESSION_LEVEL': 6,  # 0-9, higher is more compression
        'SPLIT_SIZE': 1900000000  # 1.9GB default split size
    }

    #--------------------
    # FILE/FOLDER NAMING
    #--------------------
    PLAYLIST_NAME_FORMAT = getenv("PLAYLIST_NAME_FORMAT", "{title} - Playlist")
    TRACK_NAME_FORMAT = getenv("TRACK_NAME_FORMAT", "{title} - {artist}")

    #--------------------
    # TIDAL SETTINGS
    #--------------------
    ENABLE_TIDAL = getenv("ENABLE_TIDAL", None)
    TIDAL_SETTINGS = {
        'MOBILE': getenv("TIDAL_MOBILE", None),
        'MOBILE_TOKEN': getenv("TIDAL_MOBILE_TOKEN", None),
        'ATMOS_TOKEN': getenv("TIDAL_ATMOS_MOBILE_TOKEN", None),
        'TV_TOKEN': getenv("TIDAL_TV_TOKEN", None),
        'TV_SECRET': getenv("TIDAL_TV_SECRET", None),
        'CONVERT_M4A': getenv("TIDAL_CONVERT_M4A", False),
        'QUALITY': 'HI_RES',
        'MAX_QUALITY': True,
        'DOWNLOAD_VIDEOS': False
    }
