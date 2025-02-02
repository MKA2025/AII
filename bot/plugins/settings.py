from pyrogram import Client, filters
from bot.config import Config
from bot.logger import LOGGER
from bot import bot_set

@Client.on_message(filters.command(['settings']))
async def settings_handler(client, message):
    try:
        args = message.text.split()[1:]
        if len(args) < 2:
            await message.reply("Usage: /settings [setting_name] [value]")
            return
            
        setting = args[0].lower()
        value = args[1].lower()
        
        # Check if ZIP setting
        if setting.startswith('zip_'):
            # Check permissions
            if not (message.from_user.id in bot_set.admins or 
                   Config.ZIP_SETTINGS['PUBLIC_ACCESS']):
                await message.reply("⚠️ You don't have permission to change ZIP settings")
                return
                
            if bot_set.update_zip_settings(setting, value):
                await message.reply(f"✅ ZIP setting '{setting}' updated successfully")
            else:
                await message.reply("❌ Invalid setting or value")
                
    except Exception as e:
        LOGGER.error(f"Settings error: {str(e)}")
        await message.reply("❌ An error occurred")
