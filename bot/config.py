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
        APP_ID = int(getenv("APP_ID", ""))
        API_HASH = getenv("API_HASH")
        OWNER_ID = int(getenv("OWNER_ID", ""))
        DATABASE_URL = getenv("DATABASE_URL")
        BOT_USERNAME = getenv("BOT_USERNAME")
        ADMINS = set(int(x) for x in getenv("ADMINS", "").split())
        LOG_CHANNEL = int(getenv("LOG_CHANNEL", ""))
        AUTH_CHATS = set(int(x) for x in getenv("AUTH_CHATS", "").split())
        ENABLE_QOBUZ = getenv("ENABLE_QOBUZ", None)
        USER = getenv("USER", None)
        RCLONE = getenv("RCLONE", None)
    except Exception as e:
        LOGGER.error(f"Basic config error: {str(e)}")
        exit(1)

    #--------------------
    # BOT WORKING DIRECTORY
    #--------------------
    WORK_DIR = getenv("WORK_DIR", "./bot/")
    DOWNLOADS_FOLDER = getenv("DOWNLOADS_FOLDER", "DOWNLOADS")
    DOWNLOAD_BASE_DIR = WORK_DIR + DOWNLOADS_FOLDER
    LOCAL_STORAGE = getenv("LOCAL_STORAGE", DOWNLOAD_BASE_DIR)

    #--------------------
    # BOT CONSTANTS
    #--------------------
    CHUNK_SIZE = 1024 * 1024  # 1MB
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    TIMEOUT = 60  # seconds

    #--------------------
    # PERFORMANCE SETTINGS  
    #--------------------
    PERFORMANCE = {
        'CHUNK_SIZE': CHUNK_SIZE,
        'BUFFER_SIZE': 10,
        'MAX_CONCURRENT_DOWNLOADS': 5, 
        'PROGRESS_UPDATE_DELAY': 0.5,
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
    # ZIP SETTINGS
    #--------------------
    ZIP_SETTINGS = {
        'ENABLED': True,
        'MAX_SIZE': 2000000000,  # 2GB
        'CHUNK_SIZE': 8192,
        'COMPRESSION_LEVEL': 6,
        'ALLOWED_TYPES': ['.mp3', '.flac', '.m4a', '.wav', '.aac'],
        'SPLIT_SIZE': 1900000000,  # 1.9GB
        'MAX_RETRIES': MAX_RETRIES,
        'RETRY_DELAY': RETRY_DELAY,
        'CLEANUP_FAILED': True,
        'PROGRESS_UPDATE_INTERVAL': 0.5,
        'SHOW_SPEED': True,
        'SHOW_ETA': True,
        'TEMP_FOLDER': 'temp_downloads'
    }

    #--------------------
    # ADMIN SETTINGS
    #--------------------
    ADMIN_SETTINGS = {
        'PERMISSIONS': {
            'super_admin': [
                'can_manage_admins',
                'can_broadcast',
                'can_ban_users',
                'can_manage_settings',
                'can_view_logs',
                'can_backup',
                'can_manage_providers',
                'can_manage_downloads'
            ],
            'moderator': [
                'can_ban_users',
                'can_view_logs',
                'can_manage_downloads'
            ],
            'uploader': [
                'can_upload',
                'can_view_logs'
            ]
        },
        'SECURITY': {
            'SECRET_KEY': getenv('ADMIN_SECRET_KEY', 'your-secret-key'),
            'ALGORITHM': 'HS256',
            'SESSION_TIMEOUT': 3600,
            'REQUIRE_2FA': bool(getenv('ADMIN_2FA', False)),
            'IP_WHITELIST': getenv('ADMIN_IP_WHITELIST', '').split(','),
            'MAX_LOGIN_ATTEMPTS': 3,
            'LOCKOUT_TIME': 300,
            'ALLOW_BACKUP': bool(getenv('ALLOW_BACKUP', True))
        },
        'LOGGING': {
            'RETENTION_DAYS': 7,
            'MAX_LOG_SIZE': 5 * 1024 * 1024,
            'BACKUP_COUNT': 3,
            'LOG_LEVEL': getenv('ADMIN_LOG_LEVEL', 'INFO')
        },
        'BACKUP': {
            'INTERVAL': 24,
            'MAX_BACKUPS': 7,
            'INCLUDE_LOGS': True,
            'COMPRESS': True,
            'BACKUP_PATH': getenv('BACKUP_PATH', './backups')
        },
        'NOTIFICATIONS': {
            'ERROR_THRESHOLD': 10,
            'STORAGE_WARNING': 90,
            'USER_REPORTS': True,
            'ADMIN_CHAT_ID': getenv('ADMIN_CHAT_ID', ''),
            'NOTIFY_ON_ERROR': True,
            'NOTIFY_ON_BAN': True,
            'NOTIFY_ON_NEW_USER': True
        }
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
        'DOWNLOAD_VIDEOS': False,
        'API_KEY': getenv("TIDAL_API_KEY", None),
        'API_SECRET': getenv("TIDAL_API_SECRET", None)
    }
