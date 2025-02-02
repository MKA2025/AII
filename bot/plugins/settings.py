from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Config
from bot.logger import LOGGER
from bot import bot_set
from bot.helpers.utils.format import format_size, format_time
from bot.helpers.translations import lang

async def update_progress_message(message: Message, current: int, total: int, start_time: float):
    """Update download progress message"""
    try:
        now = time.time()
        elapsed_time = now - start_time
        speed = current / elapsed_time if elapsed_time > 0 else 0
        
        progress = (current * 100) / total
        progress_bar = "█" * int(progress/5) + "░" * (20 - int(progress/5))
        
        text = f"""
📥 **Download Progress**
├ Progress: [{progress_bar}] {progress:.1f}%
├ Speed: {format_size(speed)}/s
├ Downloaded: {format_size(current)} / {format_size(total)}
├ Elapsed: {format_time(elapsed_time)}
└ ETA: {format_time((total - current) / speed if speed > 0 else 0)}
"""
        await message.edit(text)
        
    except Exception as e:
        LOGGER.error(f"Progress update failed: {str(e)}")

@Client.on_message(filters.command(['settings']))
async def settings_handler(client, message):
    """Handle settings commands and updates"""
    try:
        args = message.text.split()[1:]
        user_id = message.from_user.id
        
        if len(args) < 2:
            await message.reply(
                "ℹ️ Usage: /settings [setting_name] [value]\n\n" +
                "Available settings:\n" +
                "- zip_enabled [true/false]\n" +
                "- max_zip_size [size in MB]\n" +
                "- download_quality [normal/high/best]\n" +
                "- concurrent_downloads [1-10]"
            )
            return
            
        setting = args[0].lower()
        value = args[1].lower()
        
        # Validate user permissions
        if not (user_id in bot_set.admins or Config.ZIP_SETTINGS['PUBLIC_ACCESS']):
            await message.reply("⚠️ You don't have permission to change settings")
            return
            
        # Handle ZIP settings
        if setting.startswith('zip_'):
            if setting not in Config.ZIP_SETTINGS['ALLOWED_SETTINGS']:
                await message.reply(f"❌ Invalid ZIP setting: {setting}")
                return
                
            if setting == 'zip_enabled':
                enabled = value.lower() == 'true'
                bot_set.update_zip_settings('enabled', enabled)
                await message.reply(f"✅ ZIP feature is now {'enabled' if enabled else 'disabled'}")
                
            elif setting == 'max_zip_size':
                try:
                    size = int(value)
                    if not 1 <= size <= 2000:
                        raise ValueError("Size must be between 1-2000 MB")
                    bot_set.update_zip_settings('max_size', size * 1024 * 1024)
                    await message.reply(f"✅ Maximum ZIP size set to {size}MB")
                except ValueError as e:
                    await message.reply(f"❌ Invalid size value: {str(e)}")
                    
        # Handle download settings
        elif setting == 'download_quality':
            if value not in ['normal', 'high', 'best']:
                await message.reply("❌ Invalid quality setting. Use: normal/high/best")
                return
                
            quality_map = {
                'normal': 'NORMAL',
                'high': 'HIGH',
                'best': 'HI_RES'
            }
            
            bot_set.update_tidal_settings('quality', quality_map[value])
            await message.reply(f"✅ Download quality set to {value}")
            
        elif setting == 'concurrent_downloads':
            try:
                concurrent = int(value)
                if not 1 <= concurrent <= 10:
                    raise ValueError("Value must be between 1-10")
                    
                Config.MAX_CONCURRENT_DOWNLOADS = concurrent
                await message.reply(f"✅ Concurrent downloads set to {concurrent}")
            except ValueError:
                await message.reply("❌ Invalid value. Use a number between 1-10")
                
        else:
            await message.reply(f"❌ Unknown setting: {setting}")
            
    except Exception as e:
        LOGGER.error(f"Settings error: {str(e)}")
        await message.reply("❌ An error occurred while updating settings")

@Client.on_message(filters.command(['zip']))
async def zip_handler(client, message):
    """Handle ZIP related commands"""
    try:
        args = message.text.split()[1:]
        user_id = message.from_user.id
        
        if not args:
            await message.reply(
                "ℹ️ ZIP Commands:\n\n"
                "/zip create [folder] - Create ZIP from folder\n"
                "/zip split [file] [size_mb] - Split ZIP into parts\n"
                "/zip merge [part1] [part2] - Merge ZIP parts"
            )
            return
            
        command = args[0].lower()
        
        if command == 'create':
            if len(args) < 2:
                await message.reply("❌ Please specify folder path")
                return
                
            folder = args[1]
            if not os.path.exists(folder):
                await message.reply("❌ Folder not found")
                return
                
            progress_msg = await message.reply("📚 Creating ZIP file...")
            start_time = time.time()
            
            try:
                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()
                
                zip_path = await zipper.create_zip(
                    [os.path.join(folder, f) for f in os.listdir(folder)],
                    f"{folder}.zip"
                )
                
                await progress_msg.edit(f"✅ ZIP created: {zip_path}")
                
            except Exception as e:
                await progress_msg.edit(f"❌ ZIP creation failed: {str(e)}")
                
        elif command == 'split':
            if len(args) < 3:
                await message.reply("❌ Please specify file and split size")
                return
                
            file_path = args[1]
            try:
                split_size = int(args[2]) * 1024 * 1024 # Convert MB to bytes
            except ValueError:
                await message.reply("❌ Invalid split size")
                return
                
            if not os.path.exists(file_path):
                await message.reply("❌ File not found")
                return
                
            progress_msg = await message.reply("✂️ Splitting ZIP file...")
            
            try:
                from bot.helpers.zipper.async_zipper import AsyncZipper
                zipper = AsyncZipper()
                
                parts = await zipper.create_zip(
                    [file_path],
                    file_path,
                    split_size=split_size
                )
                
                await progress_msg.edit(f"✅ Split into {len(parts)} parts")
                
            except Exception as e:
                await progress_msg.edit(f"❌ Split failed: {str(e)}")
                
        elif command == 'merge':
            if len(args) < 3:
                await message.reply("❌ Please specify ZIP parts to merge")
                return
                
            parts = args[1:]
            for part in parts:
                if not os.path.exists(part):
                    await message.reply(f"❌ Part not found: {part}")
                    return
                    
            progress_msg = await message.reply("🔄 Merging ZIP parts...")
            
            try:
                output = parts[0].replace('.part1', '')
                with open(output, 'wb') as outfile:
                    for part in parts:
                        with open(part, 'rb') as infile:
                            outfile.write(infile.read())
                            
                await progress_msg.edit(f"✅ Merged into: {output}")
                
            except Exception as e:
                await progress_msg.edit(f"❌ Merge failed: {str(e)}")
                
        else:
            await message.reply("❌ Unknown ZIP command")
            
    except Exception as e:
        LOGGER.error(f"ZIP handler error: {str(e)}")
        await message.reply("❌ An error occurred")

# Register command handlers
HANDLERS = [
    settings_handler,
    zip_handler
            ]
