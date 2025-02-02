class EN(object):
    DOWNLOAD_START = "Starting Download..."
    UPLOAD_START = "Starting Upload..."
    UPLOAD_SUCCESS = "Thanks for using bot"
    UPLOAD_FAILED = "Sorry ! something went wrong \n\nPress /clean to clean temporary files and folders"
    ERR_OPEN_LINK = "Sorry cannot directly access links. Please use /start with link only"
    PROGRESS_BAR = """**{1}%** | [{0}{2}]"""
    DOWNLOADING = """\n\n**↳ Speed**: `{}/s`
**↳ Done**: `{}`
**↳ Size**: `{}`
**↳ Time**: `{}`"""
    UPLOADING = """\n\n**↳ Speed**: `{}/s`
**↳ Done**: `{}`
**↳ Size**: `{}`
**↳ Time**: `{}`"""
    CLEANING = """🧹 Cleaning Temp Files and Folders"""
    FETCHING = 'Fetching Details...'
    DOWNLOADING_FILE = "Downloading File..."
    UPLOADING_FILE = "Uploading File..."
    ZIPPING = 'Zipping........'
    TASK_COMPLETED = "Download Finished"

#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_PANEL = '<b>Welcome to Bot Settings</b>'
    LANGUAGE_PANEL = 'Select bot language here'
    CORE_PANEL = 'Edit main settings here'
    PROVIDERS_PANEL = 'Configure each platform seperartelty'

    TIDAL_PANEL = "Configure Tidal settings here"
    TIDAL_AUTH_PANEL = """
Manage auth of Tidal Account here

<b>Account :</b> <code>{}</code>
<b>Mobile HiRes :</b> <code>{}</code>
<b>Mobile Atmos :</b> <code>{}</code>
<b>TV/Auto : </b> <code>{}</code>
"""
    TIDAL_AUTH_URL = "Go to the below link for loggin in\n{}"
    TIDAL_AUTH_SUCCESSFULL = 'Succesfully logged in Tidal'
    TIDAL_REMOVED_SESSION = 'Successfully removed all sessions for Tidal'

    TELEGRAM_PANEL = """
<b>Telegram Settings</b>

Admins : {2}
Auth Users : {3}
Auth Chats : {4}
"""
    BAN_AUTH_FORMAT = 'Use /command {userid}'
    BAN_ID = 'Removed {}'
    USER_DOEST_EXIST = "This ID doesn't exist"
    USER_EXIST = 'This ID already exist'
    AUTH_ID = 'Successfully Authed'

#----------------
#
# BUTTONS
#
#----------------
    MAIN_MENU_BUTTON = 'MAIN MENU'
    CLOSE_BUTTON = 'CLOSE'
    PROVIDERS = 'PROVIDERS'
    TELEGRAM = 'Telegram'
    CORE = 'CORE'
    
    QOBUZ = 'Qobuz'
    DEEZER = 'Deezer'
    TIDAL = 'Tidal'

    BOT_PUBLIC = 'Bot Public - {}'
    BOT_LANGUAGE = 'Language'
    ANTI_SPAM = 'Anti Spam - {}'
    LANGUAGE = 'Language'
    QUALITY = 'Quality'
    AUTHORIZATION = "Authorizations"

    POST_ART_BUT = "Art Poster : {}"
    SORT_PLAYLIST = 'Sort Playlist : {}'
    DISABLE_SORT_LINK = 'Disable Sort Link : {}'
    PLAYLIST_CONC_BUT = "Playlist Batch Download : {}"
    PLAYLIST_ZIP = 'Zip Playlist : {}'
    ARTIST_BATCH_BUT = 'Artist Batch Upload : {}'
    ARTIST_ZIP = 'Zip Artist : {}'
    ALBUM_ZIP = 'Zip Album : {}'

    QOBUZ_QUALITY_PANEL = '<b>Edit Qobuz Quality Here</b>'

    TIDAL_LOGIN_TV = 'Login TV'
    TIDAL_REMOVE_LOGIN = "Remove Login"
    TIDAL_REFRESH_SESSION = 'Refresh Auth'

    RCLONE_LINK = 'Direct Link'
    INDEX_LINK = 'Index Link'

#----------------
#
# ERRORS
#
#----------------
    ERR_NO_LINK = 'No link found :('
    ERR_LINK_RECOGNITION = "Sorry, couldn't recognise the given link."
    ERR_QOBUZ_NOT_STREAMABLE = "This track/album is not available to download."
    ERR_QOBUZ_NOT_AVAILABLE = "This track is not available in your region"
    ERR_LOGIN_TIDAL_TV_FAILED = "Login failed : {}"

#----------------
#
# WARNINGS
#
#----------------
    WARNING_NO_TIDAL_TOKEN = 'No TV/Auto token-secret added'

#----------------
#
# ZIP SETTINGS
#
#----------------
    ZIP_SETTINGS = {
        'ENABLED': 'ZIP feature is {}',
        'SIZE_UPDATED': 'Maximum ZIP size set to {}MB',
        'INVALID_SIZE': 'Please enter a valid size between 1-2000 MB',
        'NO_PERMISSION': "You don't have permission to change ZIP settings",
        'INVALID_SETTING': 'Invalid ZIP setting or value'
    }

#----------------
#
# TRACK & ALBUM POSTS
#
#----------------
    TRACK_POST = """
𝐓𝐢𝐭𝐥𝐞 : {}
𝐀𝐫𝐭𝐢𝐬𝐭 : {}
𝐀𝐥𝐛𝐮𝐦 : {}
𝐘𝐞𝐚𝐫 : {}
"""
    ALBUM_LINK = """
🎵 𝐀𝐥𝐛𝐮𝐦 : {}
👤 𝐀𝐫𝐭𝐢𝐬𝐭 : {}
📅 𝐑𝐞𝐥𝐞𝐚𝐬𝐞𝐝 : {}
"""
    QOBUZ_LINK = """
<b>🎵 𝐓𝐢𝐭𝐥𝐞 :</b> <code>{}</code>
<b>💽 𝐅𝐨𝐫𝐦𝐚𝐭 :</b> <code>{}bit / {}kHz</code> <code>{}</code>
<b>📊 𝐁𝐢𝐭 𝐑𝐚𝐭𝐞 :</b> <code>{}kbps</code>
"""
    TIDAL_ALBUM = """
🎵 𝐓𝐢𝐭𝐥𝐞 : {}
👤 𝐀𝐫𝐭𝐢𝐬𝐭 : {}
📅 𝐘𝐞𝐚𝐫 : {}
🎼 𝐓𝐫𝐚𝐜𝐤𝐬 𝐜𝐨𝐮𝐧𝐭 : {}
"""
    TIDAL_TRACK = """
🎵 𝐓𝐢𝐭𝐥𝐞 : {}
👤 𝐀𝐫𝐭𝐢𝐬𝐭 : {}
📅 𝐘𝐞𝐚𝐫 : {}
💽 𝐀𝐥𝐛𝐮𝐦 : {}
"""

#----------------
#
# ADMIN PANEL
#
#----------------
    ADMIN_PANEL_TITLE = "🔧 Admin Control Panel"
    ADMIN_USER_MANAGEMENT = "👥 User Management"
    ADMIN_BOT_SETTINGS = "⚙️ Bot Settings" 
    ADMIN_STORAGE = "💾 Storage Management"
    ADMIN_LOGS = "📋 Logs"
    ADMIN_BACKUP = "💿 Backup"
    ADMIN_SECURITY = "🔒 Security"
    ADMIN_PROVIDERS = "🔌 Providers"

    # User Management
    ADMIN_BAN_USER = "🚫 Ban User"
    ADMIN_UNBAN_USER = "✅ Unban User"
    ADMIN_BROADCAST = "📢 Broadcast"
    ADMIN_USER_LIST = "📋 User List"
    ADMIN_USER_BANNED = "User has been banned"
    ADMIN_USER_UNBANNED = "User has been unbanned" 
    ADMIN_USER_NOT_FOUND = "User not found"
    ADMIN_BROADCAST_STARTED = "Broadcasting message to all users..."
    ADMIN_BROADCAST_DONE = "Broadcast completed\n\nSuccess: {}\nFailed: {}"

    # Security  
    ADMIN_SESSION_EXPIRED = "⚠️ Admin session has expired"
    ADMIN_INVALID_TOKEN = "❌ Invalid admin token"
    ADMIN_PERMISSION_DENIED = "❌ Permission denied"
    ADMIN_2FA_REQUIRED = "🔐 2FA verification required"
    ADMIN_2FA_FAILED = "❌ 2FA verification failed"
    ADMIN_LOGIN_ATTEMPTS = "Too many login attempts. Try again in {} minutes"
    ADMIN_IP_BLOCKED = "⛔️ Your IP address is not whitelisted"

    # Storage
    ADMIN_STORAGE_STATS = """💾 Storage Statistics
    
Used Space: {}
Free Space: {}
Total Space: {}
Usage: {}%"""
    ADMIN_STORAGE_WARNING = "⚠️ Storage usage is above {}%"
    ADMIN_CLEANUP_START = "🧹 Starting storage cleanup..."
    ADMIN_CLEANUP_DONE = "✅ Storage cleanup completed\nFreed up: {}"

    # Logs
    ADMIN_LOG_DELETED = "Log file deleted"
    ADMIN_LOG_CLEARED = "Logs cleared"
    ADMIN_LOG_BACKUP = "Log backup created: {}"
    ADMIN_LOG_NOT_FOUND = "Log file not found"

    # Backup
    ADMIN_BACKUP_START = "💿 Creating backup..."
    ADMIN_BACKUP_DONE = "✅ Backup completed: {}"
    ADMIN_BACKUP_FAILED = "❌ Backup failed: {}"
    ADMIN_BACKUP_RESTORED = "✅ Backup restored successfully"
    ADMIN_BACKUP_RESTORE_FAILED = "❌ Backup restore failed: {}"

    # Providers
    ADMIN_PROVIDER_ENABLED = "✅ {} provider enabled"
    ADMIN_PROVIDER_DISABLED = "❌ {} provider disabled"
    ADMIN_PROVIDER_CONFIG = "⚙️ {} Provider Configuration"
    ADMIN_PROVIDER_UPDATED = "✅ Provider settings updated"
    ADMIN_PROVIDER_ERROR = "❌ Provider error: {}"

    # Settings
    ADMIN_SETTINGS_UPDATED = "✅ Settings updated successfully"
    ADMIN_SETTINGS_ERROR = "❌ Failed to update settings: {}"
    ADMIN_RESTART_REQUIRED = "⚠️ Bot restart required to apply changes"

    # Notifications 
    ADMIN_NOTIFICATION_NEW_USER = "👤 New user registered: {}"
    ADMIN_NOTIFICATION_ERROR = "⚠️ Error detected: {}"
    ADMIN_NOTIFICATION_BAN = "🚫 User banned: {}\nReason: {}"

    # Download Controls
    ADMIN_DOWNLOAD_PAUSE = "⏸ Downloads paused"
    ADMIN_DOWNLOAD_RESUME = "▶️ Downloads resumed"
    ADMIN_DOWNLOAD_CANCEL = "⚠️ Download cancelled: {}"
    ADMIN_DOWNLOAD_LIMIT = "📥 Download limit set to: {}/day"
    ADMIN_CONCURRENT_LIMIT = "⚡️ Concurrent downloads limit: {}"

    # Quality Controls
    ADMIN_QUALITY_UPDATED = "✨ Quality settings updated for {}"
    ADMIN_QUALITY_ERROR = "❌ Failed to update quality settings: {}"

    # API Stats
    ADMIN_API_STATS = """📊 API Statistics

Requests Today: {}
Success Rate: {}%
Error Rate: {}%
Average Response Time: {}ms"""

    # Database Stats
    ADMIN_DB_STATS = """🗄 Database Statistics

Total Records: {}
Active Users: {}
Storage Used: {}
Last Backup: {}"""
