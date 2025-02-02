from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..config import Config
from ..helpers.database.admin_manager import AdminManager
from ..helpers.database.pg_impl import set_db
from ..helpers.message import send_message, edit_message, check_user, fetch_user_details
from ..helpers.utils import format_size, format_time
from ..helpers.translations import lang

class AdminPanel:
    def __init__(self):
        self.admin_db = AdminManager()
        self.stats = {
            'downloads': 0,
            'uploads': 0,
            'errors': 0
        }

    @Client.on_message(filters.command(["admin"]) & filters.user(Config.ADMINS))
    async def admin_panel(self, client, message):
        """Admin control panel"""
        if await check_user(message.from_user.id, restricted=True):
            user = await fetch_user_details(message)
            await send_message(
                user,
                "🔧 **Admin Control Panel**\n\n"
                f"📊 **Stats:**\n"
                f"Downloads: {self.stats['downloads']}\n"
                f"Uploads: {self.stats['uploads']}\n"
                f"Errors: {self.stats['errors']}\n\n"
                f"👥 **Users:** {await self.admin_db.get_user_count()}\n"
                f"💾 **Storage Used:** {format_size(await self.get_storage_used())}\n",
                markup=self.get_admin_markup()
            )

    def get_admin_markup(self):
        """Get admin control buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    lang.s.ADMIN_USER_MANAGEMENT,
                    callback_data="admin_users"
                ),
                InlineKeyboardButton(
                    lang.s.ADMIN_BOT_SETTINGS,
                    callback_data="admin_settings"
                )
            ],
            [
                InlineKeyboardButton(
                    lang.s.ADMIN_STORAGE,
                    callback_data="admin_storage"
                ),
                InlineKeyboardButton(
                    lang.s.ADMIN_LOGS,
                    callback_data="admin_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    lang.s.ADMIN_BACKUP,
                    callback_data="admin_backup"
                ),
                InlineKeyboardButton(
                    lang.s.ADMIN_SECURITY,
                    callback_data="admin_security"
                )
            ]
        ])

    @Client.on_callback_query(filters.regex(pattern=r"^admin_"))
    async def admin_callback(self, client, callback_query: CallbackQuery):
        if not await check_user(callback_query.from_user.id, restricted=True):
            return
            
        command = callback_query.data.split("_")[1]
        
        if command == "users":
            await self.show_user_management(client, callback_query)
        elif command == "settings":
            await self.show_bot_settings(client, callback_query)
        elif command == "storage":
            await self.show_storage_management(client, callback_query)
        elif command == "logs":
            await self.show_logs(client, callback_query)
        elif command == "backup":
            await self.show_backup_settings(client, callback_query)
        elif command == "security":
            await self.show_security_settings(client, callback_query)

    async def show_user_management(self, client, callback_query):
        users = await self.admin_db.get_all_users()
        text = "👥 **User Management**\n\n"
        text += f"Total Users: {len(users)}\n"
        text += f"Active Today: {await self.admin_db.get_active_users_count()}\n"
        text += f"Banned Users: {await self.admin_db.get_banned_users_count()}\n"
        
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Ban User",
                    callback_data="admin_ban_user"
                ),
                InlineKeyboardButton(
                    "Unban User",
                    callback_data="admin_unban_user"
                )
            ],
            [
                InlineKeyboardButton(
                    "Broadcast",
                    callback_data="admin_broadcast"
                ),
                InlineKeyboardButton(
                    "User List",
                    callback_data="admin_user_list"
                )
            ],
            [
                InlineKeyboardButton(
                    "« Back",
                    callback_data="admin_panel"
                )
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=markup)

    async def get_storage_used(self):
        """Get total storage used by bot"""
        total = 0
        for root, dirs, files in os.walk(Config.DOWNLOAD_BASE_DIR):
            total += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        return total
