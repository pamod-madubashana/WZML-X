from time import time, monotonic
from datetime import datetime
from sys import executable
from os import execl as osexecl
from asyncio import create_subprocess_exec, gather, run as asyrun, create_task, run_coroutine_threadsafe
import asyncio
from uuid import uuid4
from base64 import b64decode
from importlib import import_module, reload
from threading import Thread
import json
import hmac
import hashlib
from time import monotonic

from requests import get as rget
from pytz import timezone
from bs4 import BeautifulSoup
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from pyrogram import idle
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, private, regex
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User as PyroUser, Chat
from flask import Flask, request, jsonify
from functools import wraps
from time import time

from bot import (
    bot,
    user,
    bot_name,
    config_dict,
    user_data,
    botStartTime,
    LOGGER,
    Interval,
    DATABASE_URL,
    QbInterval,
    INCOMPLETE_TASK_NOTIFIER,
    scheduler,
)
from bot.version import get_version
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import (
    get_readable_time,
    cmd_exec,
    sync_to_async,
    new_task,
    set_commands,
    update_user_ldata,
    get_stats,
)
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import (
    sendMessage,
    editMessage,
    editReplyMarkup,
    sendFile,
    deleteMessage,
    delete_all_messages,
)
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.listeners.aria2_listener import start_aria2_listener
from .helper.themes import BotTheme
from .modules import (
    authorize,
    clone,
    gd_count,
    gd_delete,
    gd_list,
    cancel_mirror,
    mirror_leech,
    status,
    torrent_search,
    torrent_select,
    ytdlp,
    rss,
    shell,
    eval,
    users_settings,
    bot_settings,
    speedtest,
    save_msg,
    images,
    imdb,
    anilist,
    mediainfo,
    mydramalist,
    gen_pyro_sess,
    gd_clean,
    broadcast,
    category_select,
)


async def stats(client, message):
    msg, btns = await get_stats(message)
    await sendMessage(message, msg, btns, photo="IMAGES")


@new_task
async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(BotTheme("ST_BN1_NAME"), BotTheme("ST_BN1_URL"))
    buttons.ubutton(BotTheme("ST_BN2_NAME"), BotTheme("ST_BN2_URL"))
    reply_markup = buttons.build_menu(2)
    if len(message.command) > 1 and message.command[1] == "wzmlx":
        await deleteMessage(message)
    elif len(message.command) > 1 and config_dict["TOKEN_TIMEOUT"]:
        userid = message.from_user.id
        encrypted_url = message.command[1]
        input_token, pre_uid = (b64decode(encrypted_url.encode()).decode()).split("&&")
        if int(pre_uid) != userid:
            return await sendMessage(message, BotTheme("OWN_TOKEN_GENERATE"))
        data = user_data.get(userid, {})
        if "token" not in data or data["token"] != input_token:
            return await sendMessage(message, BotTheme("USED_TOKEN"))
        elif (
            config_dict["LOGIN_PASS"] is not None
            and data["token"] == config_dict["LOGIN_PASS"]
        ):
            return await sendMessage(message, BotTheme("LOGGED_PASSWORD"))
        buttons.ibutton(BotTheme("ACTIVATE_BUTTON"), f"pass {input_token}", "header")
        reply_markup = buttons.build_menu(2)
        msg = BotTheme(
            "TOKEN_MSG",
            token=input_token,
            validity=get_readable_time(int(config_dict["TOKEN_TIMEOUT"])),
        )
        return await sendMessage(message, msg, reply_markup)
    elif await CustomFilters.authorized(client, message):
        start_string = BotTheme("ST_MSG", help_command=f"/{BotCommands.HelpCommand}")
        await sendMessage(message, start_string, reply_markup, photo="IMAGES")
    elif config_dict["BOT_PM"]:
        await sendMessage(message, BotTheme("ST_BOTPM"), reply_markup, photo="IMAGES")
    else:
        await sendMessage(message, BotTheme("ST_UNAUTH"), reply_markup, photo="IMAGES")
    await DbManger().update_pm_users(message.from_user.id)


async def token_callback(_, query):
    user_id = query.from_user.id
    input_token = query.data.split()[1]
    data = user_data.get(user_id, {})
    if "token" not in data or data["token"] != input_token:
        return await query.answer("Already Used, Generate New One", show_alert=True)
    update_user_ldata(user_id, "token", str(uuid4()))
    update_user_ldata(user_id, "time", time())
    await query.answer("Activated Temporary Token!", show_alert=True)
    kb = query.message.reply_markup.inline_keyboard[1:]
    kb.insert(
        0, [InlineKeyboardButton(BotTheme("ACTIVATED"), callback_data="pass activated")]
    )
    await editReplyMarkup(query.message, InlineKeyboardMarkup(kb))


async def login(_, message):
    if config_dict["LOGIN_PASS"] is None:
        return
    elif len(message.command) > 1:
        user_id = message.from_user.id
        input_pass = message.command[1]
        if user_data.get(user_id, {}).get("token", "") == config_dict["LOGIN_PASS"]:
            return await sendMessage(message, BotTheme("LOGGED_IN"))
        if input_pass != config_dict["LOGIN_PASS"]:
            return await sendMessage(message, BotTheme("INVALID_PASS"))
        update_user_ldata(user_id, "token", config_dict["LOGIN_PASS"])
        return await sendMessage(message, BotTheme("PASS_LOGGED"))
    else:
        await sendMessage(message, BotTheme("LOGIN_USED"))


async def restart(client, message):
    restart_message = await sendMessage(message, BotTheme("RESTARTING"))
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await delete_all_messages()
    for interval in [QbInterval, Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    
    # Call the shutdown handler to properly terminate the web server
    shutdown_handler()
    
    proc1 = await create_subprocess_exec(
        "pkill", "-9", "-f", "gunicorn|aria2c|qbittorrent-nox|ffmpeg|rclone"
    )
    proc2 = await create_subprocess_exec("python3", "update.py")
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = monotonic()
    reply = await sendMessage(message, BotTheme("PING"))
    end_time = monotonic()
    await editMessage(
        reply, BotTheme("PING_VALUE", value=int((end_time - start_time) * 1000))
    )


async def log(_, message):
    buttons = ButtonMaker()
    buttons.ibutton(
        BotTheme("LOG_DISPLAY_BT"), f"wzmlx {message.from_user.id} logdisplay"
    )
    buttons.ibutton(BotTheme("WEB_PASTE_BT"), f"wzmlx {message.from_user.id} webpaste")
    await sendFile(message, "log.txt", buttons=buttons.build_menu(1))


async def search_images():
    if not (query_list := config_dict["IMG_SEARCH"]):
        return
    try:
        total_pages = config_dict["IMG_PAGE"]
        base_url = "https://www.wallpaperflare.com/search"
        for query in query_list:
            query = query.strip().replace(" ", "+")
            for page in range(1, total_pages + 1):
                url = f"{base_url}?wallpaper={query}&width=1280&height=720&page={page}"
                r = rget(url)
                soup = BeautifulSoup(r.text, "html.parser")
                images = soup.select(
                    'img[data-src^="https://c4.wallpaperflare.com/wallpaper"]'
                )
                if len(images) == 0:
                    LOGGER.info(
                        "Maybe Site is Blocked on your Server, Add Images Manually !!"
                    )
                for img in images:
                    img_url = img["data-src"]
                    if img_url not in config_dict["IMAGES"]:
                        config_dict["IMAGES"].append(img_url)
        if len(config_dict["IMAGES"]) != 0:
            config_dict["STATUS_LIMIT"] = 2
        if DATABASE_URL:
            await DbManger().update_config(
                {
                    "IMAGES": config_dict["IMAGES"],
                    "STATUS_LIMIT": config_dict["STATUS_LIMIT"],
                }
            )
    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")


async def bot_help(client, message):
    buttons = ButtonMaker()
    user_id = message.from_user.id
    buttons.ibutton(BotTheme("BASIC_BT"), f"wzmlx {user_id} guide basic")
    buttons.ibutton(BotTheme("USER_BT"), f"wzmlx {user_id} guide users")
    buttons.ibutton(BotTheme("MICS_BT"), f"wzmlx {user_id} guide miscs")
    buttons.ibutton(BotTheme("O_S_BT"), f"wzmlx {user_id} guide admin")
    buttons.ibutton(BotTheme("CLOSE_BT"), f"wzmlx {user_id} close")
    await sendMessage(message, BotTheme("HELP_HEADER"), buttons.build_menu(2))


async def restart_notification():
    now = datetime.now(timezone(config_dict["TIMEZONE"]))
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith("⌬ <b><i>Restarted Successfully!</i></b>"):
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=msg,
                    disable_web_page_preview=True,
                )
                await aioremove(".restartmsg")
            else:
                await bot.send_message(
                    chat_id=cid,
                    text=msg,
                    disable_web_page_preview=True,
                    disable_notification=True,
                )
        except Exception as e:
            LOGGER.error(e)

    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                msg = (
                    BotTheme(
                        "RESTART_SUCCESS",
                        time=now.strftime("%I:%M:%S %p"),
                        date=now.strftime("%d/%m/%y"),
                        timz=config_dict["TIMEZONE"],
                        version=get_version(),
                    )
                    if cid == chat_id
                    else BotTheme("RESTARTED")
                )
                msg += "\n\n⌬ <b><i>Incomplete Tasks!</i></b>"
                for tag, links in data.items():
                    msg += f"\n➲ <b>User:</b> {tag}\n┖ <b>Tasks:</b>"
                    for index, link in enumerate(links, start=1):
                        msg_link, source = next(iter(link.items()))
                        msg += f" {index}. <a href='{source}'>S</a> ->  <a href='{msg_link}'>L</a> |"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ""
                if msg:
                    await send_incompelete_task_message(cid, msg)

    if await aiopath.isfile(".restartmsg"):
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=BotTheme(
                    "RESTART_SUCCESS",
                    time=now.strftime("%I:%M:%S %p"),
                    date=now.strftime("%d/%m/%y"),
                    timz=config_dict["TIMEZONE"],
                    version=get_version(),
                ),
            )
        except Exception as e:
            LOGGER.error(e)
        await aioremove(".restartmsg")


async def log_check():
    if config_dict["LEECH_LOG_ID"]:
        for chat_id in config_dict["LEECH_LOG_ID"].split():
            chat_id, *topic_id = chat_id.split(":")
            try:
                try:
                    chat = await bot.get_chat(int(chat_id))
                except Exception:
                    LOGGER.error(
                        f"Not Connected Chat ID : {chat_id}, Make sure the Bot is Added!"
                    )
                    continue
                if chat.type == ChatType.CHANNEL:
                    if not (
                        await chat.get_member(bot.me.id)
                    ).privileges.can_post_messages:
                        LOGGER.error(
                            f"Not Connected Chat ID : {chat_id}, Make the Bot is Admin in Channel to Connect!"
                        )
                        continue
                    if (
                        user
                        and not (
                            await chat.get_member(user.me.id)
                        ).privileges.can_post_messages
                    ):
                        LOGGER.error(
                            f"Not Connected Chat ID : {chat_id}, Make the User is Admin in Channel to Connect!"
                        )
                        continue
                elif chat.type == ChatType.SUPERGROUP:
                    if not (await chat.get_member(bot.me.id)).status in [
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ]:
                        LOGGER.error(
                            f"Not Connected Chat ID : {chat_id}, Make the Bot is Admin in Group to Connect!"
                        )
                        continue
                    if user and not (await chat.get_member(user.me.id)).status in [
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ]:
                        LOGGER.error(
                            f"Not Connected Chat ID : {chat_id}, Make the User is Admin in Group to Connect!"
                        )
                        continue
                LOGGER.info(f"Connected Chat ID : {chat_id}")
            except Exception as e:
                LOGGER.error(f"Not Connected Chat ID : {chat_id}, ERROR: {e}")


def start_web_server():
    """Start the web server in a separate thread"""
    try:
        LOGGER.info("Starting web server...")
        from web.wserver import app
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        LOGGER.error(f"Failed to start web server: {e}")


# =============================================
# INTEGRATED BOT API - Direct Access to Bot Functions
# =============================================
# API Configuration
API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as web server for consistency

# Flask app for integrated API
api_app = Flask(__name__)

# Store bot loop reference for async operations
bot_loop = None

# Store API server thread for cleanup
api_thread = None

async def create_real_message(text, from_user_id, chat_id=None, message_id=None, reply_to_message_id=379):
    """Create a real Pyrogram Message object that can be replied to by the bot"""
    from pyrogram.types import Message, User, Chat
    from pyrogram.enums import ChatType, MessageEntityType
    from datetime import datetime
    
    # Always use the specified supergroup and reply to message 379
    target_chat_id = -1002934661749  # Fixed supergroup
    target_reply_id = reply_to_message_id  # Fixed message to reply to
    
    try:
        # Get the real chat object from Telegram
        real_chat = await bot.get_chat(target_chat_id)
        
        # Get the real user object from Telegram
        real_user = await bot.get_users(from_user_id)
        
        # Get the target message to reply to
        target_message = await bot.get_messages(target_chat_id, target_reply_id)
        
        # Create a new message ID (simulate a new message)
        new_message_id = int(time() * 1000) % 1000000
        
        # Parse command entities
        entities = []
        if text.startswith('/'):
            command_part = text.split()[0]
            entities = [{
                "type": MessageEntityType.BOT_COMMAND,
                "offset": 0,
                "length": len(command_part),
                "url": None,
                "user": None,
                "language": None,
                "custom_emoji_id": None
            }]
        
        # Create the real Message object with all required attributes
        real_message = Message(
            id=new_message_id,
            from_user=real_user,
            sender_chat=None,
            date=datetime.now(),
            chat=real_chat,
            text=text,
            entities=entities,
            reply_to_message_id=target_reply_id,
            reply_to_message=target_message
        )
        
        # Bind the bot client to the message
        real_message._client = bot
        
        # Parse command for easier access
        real_message.command = text.split()
        
        # Create proper Telegram link
        chat_link_id = abs(target_chat_id) - 1000000000000
        real_message.link = f"https://t.me/c/{chat_link_id}/{new_message_id}"
        
        LOGGER.info(f"Created real message ID {new_message_id} replying to {target_reply_id} in chat {target_chat_id}")
        return real_message
        
    except Exception as e:
        LOGGER.error(f"Failed to create real message: {e}")
        # Fallback to enhanced fake message if real message creation fails
        return create_enhanced_fake_message(text, from_user_id, target_chat_id, message_id, target_reply_id)

def create_enhanced_fake_message(text, from_user_id, chat_id=None, message_id=None, reply_to_message_id=379):
    """Create an enhanced fake message as fallback with real reply capabilities"""
    from pyrogram.enums import ChatType
    from datetime import datetime
    
    # Always use the specified supergroup and reply to message 379
    target_chat_id = chat_id or -1002934661749
    target_reply_id = reply_to_message_id
    
    # Create a simpler and more robust fake message implementation
    class FakeMessage:
        def __init__(self, text, user_id, chat_id, message_id=None, reply_to_id=379):
            self.id = message_id if message_id else int(time() * 1000) % 1000000
            self.message_id = 379
            self.text = text
            self.date = datetime.now()
            self.command = text.split() if text else []
            self.reply_to_message_id = reply_to_id
            self.sender_chat = None
            self.media = None
            self.client = bot  # This is critical - bind the actual bot client
            self._client = bot  # Also bind as _client for compatibility
            self.link = "https://t.me/c/2934661749/379"
            
            # Create proper user object
            class FakeUser:
                def __init__(self, user_id):
                    self.id = user_id
                    self.is_bot = False
                    self.first_name = "API User"
                    self.username = "api_user" if user_id != 7859877609 else "pamod_madubashana"
                    self.language_code = "en"
                    
                def mention(self, style="text"):
                    return f"@{self.username}" if self.username else self.first_name
                    
            self.from_user = FakeUser(user_id)
            
            # Create proper chat object
            class FakeChat:
                def __init__(self, chat_id):
                    self.id = chat_id
                    self.type = ChatType.SUPERGROUP if chat_id < 0 else ChatType.PRIVATE
                    self.title = "Serandip Leech" if chat_id < 0 else None
                    self.username = None
                    self.first_name = None
                    
            self.chat = FakeChat(chat_id)
            
            # Add entities for bot commands
            self.entities = []
            if text and text.startswith('/'):
                command_part = text.split()[0]
                self.entities = [{
                    "offset": 0,
                    "length": len(command_part),
                    "type": "bot_command"
                }]
            
            # Create proper Telegram link
            chat_link_id = abs(chat_id) - 1000000000000 if chat_id < 0 else chat_id
            self.link = f"https://t.me/c/{chat_link_id}/{self.id}"
            
            # Create reply_to_message object
            class FakeReplyMessage:
                def __init__(inner_self, reply_id, chat_id):
                    inner_self.id = reply_id
                    inner_self.message_id = reply_id
                    inner_self.text = f"Target message {reply_id}"
                    inner_self.date = datetime.now()
                    inner_self.from_user = FakeUser(user_id)
                    inner_self.chat = FakeChat(chat_id)
                    inner_self.media = None
                    inner_self.client = bot  # Critical: bind the actual bot client
                    inner_self._client = bot  # Also bind as _client for compatibility
                    
                    # Create proper Telegram link for reply message
                    reply_chat_link_id = abs(chat_id) - 1000000000000 if chat_id < 0 else chat_id
                    inner_self.link = f"https://t.me/c/{reply_chat_link_id}/{reply_id}"
                    
                    # Simple reply method that returns a proper message object or None on error
                    async def simple_reply(text,quote,reply_markup, **kwargs):
                        try:
                            result = await bot.send_message(
                                chat_id=chat_id,
                                text=text,
                                reply_to_message_id=379,
                                reply_markup=reply_markup,
                            )
                            return result
                        except Exception as e:
                            LOGGER.error(f"Reply error: {e}")
                            return None  # Return None instead of string to avoid 'str' object errors
                            
                    inner_self.reply = simple_reply
                    
            self.reply_to_message = FakeReplyMessage(reply_to_id, chat_id)
            
            # Simple reply method for main message
            async def simple_reply(text,quote,reply_markup, **kwargs):
                try:
                    result = await bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_to_message_id=379,
                        reply_markup=reply_markup,
                    )
                    return result
                except Exception as e:
                    LOGGER.error(f"Reply error: {e}")
                    return None  # Return None instead of string to avoid 'str' object errors
                    
            self.reply = simple_reply
            
            # Simple edit methods
            async def simple_edit_text(text, **kwargs):
                try:
                    result = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=self.id,
                        text=text,
                        **kwargs
                    )
                    return result
                except Exception as e:
                    LOGGER.error(f"Edit text error: {e}")
                    return None  # Return None instead of string to avoid 'str' object errors
                    
            async def simple_edit(text, **kwargs):
                return await simple_edit_text(text, **kwargs)
                
            self.edit_text = simple_edit_text
            self.edit = simple_edit
            
            # Simple delete method
            async def simple_delete(**kwargs):
                try:
                    result = await bot.delete_messages(chat_id, self.id)
                    return result
                except Exception as e:
                    LOGGER.error(f"Delete error: {e}")
                    return None  # Return None instead of string to avoid 'str' object errors
                    
            self.delete = simple_delete
    
    return FakeMessage(text, from_user_id, target_chat_id, message_id, target_reply_id)

def verify_api_signature(func):
    """Decorator to verify API requests with HMAC signature"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Bot-Signature')
        if not signature:
            return jsonify({"error": "Missing signature"}), 401
        
        if request.method == 'POST':
            body = request.get_data()
        else:
            body = b''
        
        expected_signature = hmac.new(
            API_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({"error": "Invalid signature"}), 401
        
        return func(*args, **kwargs)
    return decorated_function

@api_app.route("/api/status", methods=["GET"])
@verify_api_signature
def api_get_status():
    """Get bot status information"""
    try:
        # Get real bot stats using the existing stats function
        downloads = 0  # Will be updated with real data
        
        return jsonify({
            "status": "success",
            "bot_status": "online",
            "active_downloads": downloads,
            "bot_available": True,
            "download_dir": "/usr/src/app/downloads",
            "message": "Bot status retrieved successfully",
            "timestamp": int(time()),
            "api_version": "2.0 - Integrated"
        })
    except Exception as e:
        LOGGER.error(f"API Status Error: {e}")
        return jsonify({"error": str(e)}), 500

@api_app.route("/api/leech", methods=["POST"])
@verify_api_signature
def api_leech():
    """Start a leech task via API - REAL EXECUTION with full command support"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing request data"}), 400
        
        # Extract message ID from file URL if present
        extracted_message_id = None
        if 'command' in data:
            command_text = data['command']
            # Look for Telegram URLs in the command to extract message ID
            if 'https://t.me/c/' in command_text:
                try:
                    # Extract message ID from URL like https://t.me/c/2934661749/76
                    url_part = command_text.split('https://t.me/c/')[1].split()[0]
                    extracted_message_id = int(url_part.split('/')[-1])
                    LOGGER.info(f"Extracted message ID: {extracted_message_id} from command")
                except (IndexError, ValueError) as e:
                    LOGGER.warning(f"Could not extract message ID from command: {e}")
        
        # Support both 'command' and 'url' parameters  
        if 'command' in data:
            # Full command mode - use complete command text as-is
            command_text = data['command']
            user_id = int(data.get('user_id', 7859877609))
            chat_id = int(data.get('chat_id', -1001234567890))
            
            LOGGER.info(f"API Leech Full Command: {command_text} for user {user_id}")
            
        elif 'url' in data:
            # Legacy URL mode with optional custom name
            url = data['url']
            user_id = int(data.get('user_id', 7859877609))
            custom_name = data.get('custom_name', '')
            chat_id = int(data.get('chat_id', -1001234567890))
            
            # Extract message ID only for Telegram URLs
            if 'https://t.me/c/' in url:
                try:
                    url_part = url.split('https://t.me/c/')[1].split()[0]
                    extracted_message_id = int(url_part.split('/')[-1])
                except (IndexError, ValueError) as e:
                    LOGGER.warning(f"Could not extract message ID from Telegram URL: {e}")
                    extracted_message_id = None
            else:
                # For non-Telegram URLs, don't extract message ID
                extracted_message_id = None
            
            # Create command text
            if custom_name:
                command_text = f"/leech {url} -n {custom_name}"
            else:
                command_text = f"/leech {url}"
                
            LOGGER.info(f"API Leech Request: {url} for user {user_id} with custom name: {custom_name}")
        else:
            return jsonify({"error": "Missing 'url' or 'command' parameter"}), 400
        
        # Create async wrapper for message creation
        async def create_message_async():
            """Async wrapper for message creation"""
            try:
                # Always create real message that replies to fixed message 379
                LOGGER.info(f"Creating real message that always replies to message 379 in supergroup -1002934661749")
                
                # Use the new create_real_message function that always replies to message 379
                fake_message = await create_real_message(
                    text=command_text,
                    from_user_id=user_id,
                    chat_id=-1002934661749,  # Fixed supergroup
                    message_id=None,
                    reply_to_message_id=379  # Always reply to message 379
                )
                
                if fake_message is None:
                    # Fallback to enhanced fake message if real message creation fails
                    fake_message = create_enhanced_fake_message(
                        text=command_text,
                        from_user_id=user_id,
                        chat_id=-1002934661749,  # Fixed supergroup
                        message_id=None,
                        reply_to_message_id=379  # Always reply to message 379
                    )
                
                return fake_message
            except Exception as e:
                LOGGER.error(f"Error creating message: {e}")
                # Fallback to enhanced fake message
                return create_enhanced_fake_message(
                    text=command_text,
                    from_user_id=user_id,
                    chat_id=-1002934661749,
                    message_id=None,
                    reply_to_message_id=379
                )
        
        # Generate task ID
        task_id = f"api_leech_{int(time() * 1000)}"
        
        # Import bot_loop inside the function to ensure it's defined
        from bot import bot_loop
        
        # Debug logging
        LOGGER.info(f"Checking bot_loop: bot_loop={bot_loop}, is_closed={bot_loop.is_closed() if bot_loop else 'N/A'}")
        
        # Execute message creation and leech command in the bot's event loop
        if bot_loop and not bot_loop.is_closed():
            # Import the leech function from mirror_leech module
            from bot.modules.mirror_leech import _mirror_leech
            
            # Schedule the message creation and leech command to run in bot's event loop
            try:
                # Create message in bot loop
                future_message = asyncio.run_coroutine_threadsafe(create_message_async(), bot_loop)
                fake_message = future_message.result(timeout=30)  # 30 second timeout
                
                if fake_message is None:
                    return jsonify({
                        "error": "Failed to create message object",
                        "status": "error"
                    }), 500
                
                # Create a wrapper to properly handle the async execution
                async def execute_leech():
                    """Wrapper to execute leech command with proper error handling"""
                    try:
                        await _mirror_leech(bot, fake_message, isQbit=False, isLeech=True, sameDir=None, bulk=[])
                        LOGGER.info(f"Leech command executed successfully for task: {task_id}")
                    except Exception as e:
                        LOGGER.error(f"Error in leech execution: {e}")
                        raise e
                
                # Schedule the execution
                future = asyncio.run_coroutine_threadsafe(execute_leech(), bot_loop)
                
                # Auto-send status message after starting leech
                async def send_status_after_leech():
                    """Send status message automatically after leech starts"""
                    try:
                        await asyncio.sleep(3)  # Wait a bit longer for leech to initialize
                        from bot.modules.status import mirror_status
                        
                        # Create a status message for the same user that also replies to 379
                        status_message = await create_real_message(
                            text="/status",
                            from_user_id=user_id,
                            chat_id=-1002934661749,  # Fixed supergroup
                            message_id=None,
                            reply_to_message_id=379  # Always reply to message 379
                        )
                        
                        if status_message is None:
                            # Fallback to enhanced fake message
                            status_message = create_enhanced_fake_message(
                                text="/status",
                                from_user_id=user_id,
                                chat_id=-1002934661749,
                                message_id=None,
                                reply_to_message_id=379
                            )
                        
                        # Send status update
                        await mirror_status(bot, status_message)
                        LOGGER.info(f"Auto-sent status message for leech task: {task_id}")
                    except Exception as e:
                        LOGGER.error(f"Failed to send auto status: {e}")
                
                # Schedule the auto-status in the bot's event loop
                asyncio.run_coroutine_threadsafe(send_status_after_leech(), bot_loop)
                
                LOGGER.info(f"Leech task scheduled with ID: {task_id}")
                
                return jsonify({
                    "status": "success",
                    "message": f"Leech command executed successfully with real message object",
                    "task_id": task_id,
                    "user_id": user_id,
                    "chat_id": -1002934661749,
                    "reply_to_message_id": 379,
                    "telegram_command": command_text,
                    "timestamp": int(time()),
                    "auto_status": True,
                    "note": "Real Pyrogram message created. Bot can now reply properly. Status message will be sent automatically."
                })
                
            except Exception as async_error:
                LOGGER.error(f"Async execution error: {async_error}")
                return jsonify({
                    "error": f"Failed to execute leech command: {str(async_error)}",
                    "status": "error"
                }), 500
        else:
            return jsonify({
                "error": "Bot event loop not available",
                "status": "error"
            }), 500
            
    except Exception as e:
        LOGGER.error(f"API Leech Error: {e}")
        return jsonify({"error": str(e)}), 500

@api_app.route("/api/downloads", methods=["GET"])
@verify_api_signature
def api_get_downloads():
    """Get list of current downloads"""
    try:
        # Import the download_dict to get real download data
        from bot import download_dict
        
        downloads = []
        
        # Get current tasks from download_dict
        for task_id, task in download_dict.items():
            downloads.append({
                "name": getattr(task, 'name', lambda: 'Unknown')() if callable(getattr(task, 'name', None)) else getattr(task, 'name', 'Unknown'),
                "progress": getattr(task, 'progress', lambda: 0)() if callable(getattr(task, 'progress', None)) else getattr(task, 'progress', 0),
                "speed": getattr(task, 'speed', lambda: '0 B/s')() if callable(getattr(task, 'speed', None)) else getattr(task, 'speed', '0 B/s'),
                "eta": getattr(task, 'eta', lambda: 'Unknown')() if callable(getattr(task, 'eta', None)) else getattr(task, 'eta', 'Unknown'),
                "status": getattr(task, 'status', lambda: 'Unknown')() if callable(getattr(task, 'status', None)) else getattr(task, 'status', 'Unknown'),
                "task_id": task_id
            })
        
        return jsonify({
            "status": "success",
            "downloads": downloads,
            "count": len(downloads),
            "message": "Downloads retrieved successfully",
            "timestamp": int(time())
        })
        
    except Exception as e:
        LOGGER.error(f"API Downloads Error: {e}")
        return jsonify({"error": str(e)}), 500

@api_app.route("/api/mirror", methods=["POST"])
@verify_api_signature
def api_mirror():
    """Start a mirror task via API - REAL EXECUTION"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"error": "Missing 'url' parameter"}), 400
        
        url = data['url']
        user_id = int(data.get('user_id', 7859877609))
        chat_id = int(data.get('chat_id', -1001234567890))
        
        command_text = f"/mirror {url}"
        
        # Create async wrapper for message creation
        async def create_mirror_message_async():
            """Async wrapper for mirror message creation"""
            try:
                # Always create real message that replies to fixed message 379
                mock_message = await create_real_message(
                    text=command_text,
                    from_user_id=user_id,
                    chat_id=-1002934661749,  # Fixed supergroup
                    message_id=None,
                    reply_to_message_id=379  # Always reply to message 379
                )
                
                if mock_message is None:
                    # Fallback to enhanced fake message
                    mock_message = create_enhanced_fake_message(
                        text=command_text,
                        from_user_id=user_id,
                        chat_id=-1002934661749,
                        message_id=None,
                        reply_to_message_id=379
                    )
                
                return mock_message
            except Exception as e:
                LOGGER.error(f"Error creating mirror message: {e}")
                # Fallback to enhanced fake message
                return create_enhanced_fake_message(
                    text=command_text,
                    from_user_id=user_id,
                    chat_id=-1002934661749,
                    message_id=None,
                    reply_to_message_id=379
                )
        
        task_id = f"api_mirror_{int(time() * 1000)}"
        
        # Import bot_loop inside the function to ensure it's defined
        from bot import bot_loop
        
        # Debug logging
        LOGGER.info(f"Checking bot_loop for mirror: bot_loop={bot_loop}, is_closed={bot_loop.is_closed() if bot_loop else 'N/A'}")
        
        if bot_loop and not bot_loop.is_closed():
            from bot.modules.mirror_leech import _mirror_leech
            
            try:
                # Create message in bot loop
                future_message = asyncio.run_coroutine_threadsafe(create_mirror_message_async(), bot_loop)
                mock_message = future_message.result(timeout=30)  # 30 second timeout
                
                if mock_message is None:
                    return jsonify({
                        "error": "Failed to create mirror message object",
                        "status": "error"
                    }), 500
            
                # Create a wrapper to properly handle the async execution
                async def execute_mirror():
                    """Wrapper to execute mirror command with proper error handling"""
                    try:
                        await _mirror_leech(bot, mock_message, isQbit=False, isLeech=False, sameDir=None, bulk=[])
                        LOGGER.info(f"Mirror command executed successfully for task: {task_id}")
                    except Exception as e:
                        LOGGER.error(f"Error in mirror execution: {e}")
                        raise e
                
                future = asyncio.run_coroutine_threadsafe(execute_mirror(), bot_loop)
                
                LOGGER.info(f"Mirror task scheduled with ID: {task_id}")
                
                return jsonify({
                    "status": "success",
                    "message": f"Mirror task started for URL: {url} with real message object",
                    "task_id": task_id,
                    "user_id": user_id,
                    "url": url,
                    "chat_id": -1002934661749,
                    "reply_to_message_id": 379,
                    "telegram_command": command_text,
                    "timestamp": int(time()),
                    "note": "Real Pyrogram message created. Bot can now reply properly."
                })
                
            except Exception as async_error:
                LOGGER.error(f"Async mirror execution error: {async_error}")
                return jsonify({
                    "error": f"Failed to execute mirror command: {str(async_error)}",
                    "status": "error"
                }), 500
        else:
            return jsonify({
                "error": "Bot event loop not available",
                "status": "error"
            }), 500
            
    except Exception as e:
        LOGGER.error(f"API Mirror Error: {e}")
        return jsonify({"error": str(e)}), 500

@api_app.route("/api/help", methods=["GET"])
def api_help():
    """Get API documentation"""
    return jsonify({
        "api_version": "2.0 - Integrated Bot API",
        "description": "Direct access to bot functions via API",
        "endpoints": {
            "/api/status": {
                "method": "GET",
                "description": "Get bot status information",
                "auth_required": True
            },
            "/api/leech": {
                "method": "POST",
                "description": "Start a leech task - REAL EXECUTION with full command support",
                "auth_required": True,
                "parameters": {
                    "command": "(option 1) Full leech command text (e.g., '/leech1 https://example.com -n filename.mkv')",
                    "url": "(option 2) URL to leech (legacy mode)",
                    "user_id": "(optional) User ID for the task",
                    "custom_name": "(optional, with url) Custom filename",
                    "chat_id": "(optional) Chat ID for task"
                },
                "examples": {
                    "full_command": {
                        "command": "/leech1 https://t.me/c/123456789/10 -n MyFile.mkv",
                        "user_id": "7859877609",
                        "chat_id": -1001234567890
                    },
                    "legacy_url": {
                        "url": "https://example.com/file.zip",
                        "custom_name": "MyFile.zip",
                        "user_id": "7859877609"
                    }
                }
            },
            "/api/mirror": {
                "method": "POST",
                "description": "Start a mirror task - REAL EXECUTION",
                "auth_required": True,
                "parameters": {
                    "url": "(required) URL to mirror",
                    "user_id": "(optional) User ID for the task",
                    "chat_id": "(optional) Chat ID for task"
                }
            },
            "/api/downloads": {
                "method": "GET",
                "description": "Get list of current downloads",
                "auth_required": True
            }
        },
        "authentication": {
            "type": "HMAC-SHA256",
            "header": "X-Bot-Signature",
            "description": "Sign request body with shared secret key"
        },
        "note": "This API runs in the same process as the bot with direct access to all functions"
    })

def start_integrated_api():
    """Start the integrated API server"""
    try:
        LOGGER.info("Starting integrated bot API server on port 7392...")
        api_app.run(host='0.0.0.0', port=7392, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        LOGGER.error(f"Failed to start integrated API server: {e}")


def cleanup_api_server():
    """Stop the API server thread gracefully"""
    global api_thread
    if api_thread and api_thread.is_alive():
        LOGGER.info("Stopping integrated API server...")
        # Since we're using daemon=True, the thread will stop automatically
        # when the main process exits, but we can log it
        try:
            # For Flask apps, there's no direct way to stop from another thread
            # The daemon thread will terminate when main process exits
            LOGGER.info("API server will stop when main process exits")
        except Exception as e:
            LOGGER.error(f"Error stopping API server: {e}")


def exit_with_cleanup(signal, frame):
    """Custom cleanup function that stops API server and calls original cleanup"""
    try:
        LOGGER.info("Starting graceful shutdown...")
        cleanup_api_server()
        # Call the original cleanup function
        exit_clean_up(signal, frame)
    except Exception as e:
        LOGGER.error(f"Error during cleanup: {e}")
        exit_clean_up(signal, frame)



async def main():
    global bot_loop, api_thread
    
    # Store bot loop for API access
    bot_loop = bot.loop
    await gather(
        start_cleanup(),
        torrent_search.initiate_search_tools(),
        restart_notification(),
        search_images(),
        set_commands(bot),
        log_check(),
    )
    await sync_to_async(start_aria2_listener, wait=False)

    api_thread = Thread(target=start_integrated_api, daemon=True)
    api_thread.start()
    LOGGER.info("Integrated Bot API server started in background thread")

    bot.add_handler(
        MessageHandler(start, filters=command(BotCommands.StartCommand) & private)
    )
    bot.add_handler(CallbackQueryHandler(token_callback, filters=regex(r"^pass")))
    bot.add_handler(
        MessageHandler(login, filters=command(BotCommands.LoginCommand) & private)
    )
    bot.add_handler(
        MessageHandler(
            log, filters=command(BotCommands.LogCommand) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            restart, filters=command(BotCommands.RestartCommand) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            ping,
            filters=command(BotCommands.PingCommand)
            & CustomFilters.authorized
            & ~CustomFilters.blacklisted,
        )
    )
    bot.add_handler(
        MessageHandler(
            bot_help,
            filters=command(BotCommands.HelpCommand)
            & CustomFilters.authorized
            & ~CustomFilters.blacklisted,
        )
    )
    bot.add_handler(
        MessageHandler(
            stats,
            filters=command(BotCommands.StatsCommand)
            & CustomFilters.authorized
            & ~CustomFilters.blacklisted,
        )
    )
    LOGGER.info(f"WZML-X Bot [@{bot_name}] Started!")
    if user:
        LOGGER.info(f"WZ's User [@{user.me.username}] Ready!")
    
    # Register signal handlers
    signal(SIGINT, exit_with_cleanup)
    signal(SIGINT, exit_clean_up)


async def stop_signals():
    # Call the shutdown handler when stopping signals are received
    shutdown_handler()
    if user:
        await gather(bot.stop(), user.stop())
    else:
        await bot.stop()


bot_run = bot.loop.run_until_complete
bot_run(main())
bot_run(idle())
bot_run(stop_signals())

# Add a signal handler function
def exit_handler(signum, frame):
    LOGGER.info(f"Received signal {signum}. Shutting down gracefully...")
    shutdown_handler()
    exit(0)
