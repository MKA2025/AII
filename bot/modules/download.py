from pyrogram.types import Message
from pyrogram import Client, filters

from bot import CMD
from bot.logger import LOGGER

from ..helpers.utils import cleanup
from ..helpers.translations import lang
from ..helpers.qobuz.handler import start_qobuz
from ..helpers.message import send_message, antiSpam, check_user, fetch_user_details


@Client.on_message(filters.command(CMD.DOWNLOAD))
async def download_track(c, msg:Message):
    if await check_user(msg=msg):
        try:
            if msg.reply_to_message:
                link = msg.reply_to_message.text
                reply = True
            else:
                link = msg.text.split(" ", maxsplit=1)[1]
                reply = False
        except:
            return await send_message(msg, lang.ERR_NO_LINK)

        if not link:
            return await send_message(msg, lang.ERR_LINK_RECOGNITION)
        
        spam = await antiSpam(msg.from_user.id, msg.chat.id)
        if not spam:
            user = await fetch_user_details(msg, reply)
            user['link'] = link
            user['bot_msg'] = await send_message(msg, 'Downloading.......')
            try:
                await start_link(link, user)
                await send_message(user, lang.TASK_COMPLETED)
            except Exception as e:
                LOGGER.error(e)
            await c.delete_messages(msg.chat.id, user['bot_msg'].id)
            await cleanup(user) # deletes uploaded files
            await antiSpam(msg.from_user.id, msg.chat.id, True)

async def start_link(link:str, user:dict):
    tidal = ["https://tidal.com", "https://listen.tidal.com", "tidal.com", "listen.tidal.com"]
    deezer = ["https://deezer.page.link", "https://deezer.com", "deezer.com", "https://www.deezer.com"]
    qobuz = ["https://play.qobuz.com", "https://open.qobuz.com", "https://www.qobuz.com"]
    spotify = ["https://open.spotify.com"]
    if link.startswith(tuple(tidal)):
        return "tidal"
    elif link.startswith(tuple(deezer)):
        return "deezer"
    elif link.startswith(tuple(qobuz)):
        user['provider'] = 'Qobuz'
        await start_qobuz(link, user)
    elif link.startswith(tuple(spotify)):
        return 'spotify'
    else:
        return None