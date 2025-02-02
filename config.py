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
    # SECURITY SETTINGS
    #--------------------
    SECURITY = {
        'MAX_FILE_SIZE': 2 * 1024 * 1024 * 1024,  # 2GB
        'ALLOWED_EXTENSIONS': ['.mp3', '.flac', '.m4a', '.zip'],
        'RATE_LIMIT': {
            'WINDOW': 60,  # 1 minute
            'MAX_REQUESTS': 30,
            'BURST': 10
        },
        'IP_BLACKLIST': [],
        'REQUIRE_AUTH': True,
        'AUTH_TIMEOUT': 3600,  # 1 hour
        'MAX_LOGIN_ATTEMPTS': 3,
        'LOCKOUT_TIME': 300,  # 5 minutes
        'SECURE_HEADERS': {
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block'
        },
        'ALLOWED_HOSTS': ['*'],  # Restrict to specific hosts if needed
        'JWT_SECRET': getenv('JWT_SECRET', 'your-secret-key'),
        'JWT_ALGORITHM': 'HS256',
        'SESSION_TIMEOUT': 86400  # 24 hours
    }

    #--------------------
    # PERFORMANCE SETTINGS
    #--------------------
    PERFORMANCE = {
        'CHUNK_SIZE': 1024 * 1024,  # 1MB
        'BUFFER_SIZE': 10,
        'MAX_CONCURRENT_DOWNLOADS': 5,
        'PROGRESS_UPDATE_DELAY': 1.0,
        'CACHE_SETTINGS': {
            'MAX_SIZE': 1000,
            'TTL': 3600,
            'CLEANUP_INTERVAL': 300
        },
        'MEMORY_LIMIT': 512 * 1024 * 1024,  # 512MB
        'DB_POOL_SIZE': 5,
        'DB_MAX_OVERFLOW': 10,
        'WORKER_THREADS': 4
    }

    #--------------------
    # BOT WORKING DIRECTORY
    #--------------------
    WORK_DIR = getenv("WORK_DIR", "./bot/")
    DOWNLOADS_FOLDER = getenv("DOWNLOADS_FOLDER", "DOWNLOADS")
    DOWNLOAD_BASE_DIR = WORK_DIR + DOWNLOADS_FOLDER
    LOCAL_STORAGE = getenv("LOCAL_STORAGE", DOWNLOAD_BASE_DIR)
    
    #--------------------
    # FILE/FOLDER NAMING
    #--------------------
    PLAYLIST_NAME_FORMAT = getenv("PLAYLIST_NAME_FORMAT", "{title} - Playlist")
    TRACK_NAME_FORMAT = getenv("TRACK_NAME_FORMAT", "{title} - {artist}")
    
    #--------------------
    # ZIP SETTINGS
    #--------------------
    ZIP_SETTINGS = {
        'ENABLED': True,
        'MAX_SIZE': 2000000000,  # 2GB
        'CHUNK_SIZE': 8192,
        'COMPRESSION_LEVEL': 6,
        'ALLOWED_TYPES': ['.mp3', '.flac', '.m4a'],
        'SPLIT_SIZE': 1900000000  # 1.9GB
    }

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
        'DOWNLOAD_VIDEOS': False,
        'API_KEY': getenv("TIDAL_API_KEY", None),
        'API_SECRET': getenv("TIDAL_API_SECRET", None)
    }
