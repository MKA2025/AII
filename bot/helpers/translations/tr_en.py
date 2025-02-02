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
