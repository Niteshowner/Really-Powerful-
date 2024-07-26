from bot.helper.ext_utils.bot_utils import get_readable_time, get_stats, checking_access, update_user_ldata
from bot import user_data
from base64 import b64decode
from uuid import uuid4
from aiofiles import open as aiopen
from aiohttp import web
from bot import web_server
from base64 import b64encode
from bot.helper.button_build import ButtonMaker
from bot.helper.ext_utils.db import DbManager
from bot.helper.themes import BotTheme
import os
import time
import sys
#import logging
#,
#logger = logging.getLogger(__name__)

from bot.shell import shell

from os import execl
from asyncio import create_subprocess_exec, gather, run as asyrun
from sys import executable
from time import sleep, time, monotonic
from bot import app
from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait, RPCError, MessageNotModified
from pyrogram import filters, idle, Client
from pyrogram.filters import command, private, regex
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, EditedMessageHandler
from pyrogram import filters, idle, Client
from bot.config import TG_CONFIG
from bot.config import token_file, client_secrets_json
from bot.helpers.utils import find_auth_code
from bot.config import gauth
from bot.config import START_MSG
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydrive2 import auth
from bot.services.tplay.api import TPLAY_API
from bot.helpers.utils import post_to_telegraph
import datetime
import logging

LOGGER = logging.getLogger(__name__)
async def verify(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(BotTheme('ST_BN1_NAME'), BotTheme('ST_BN1_URL'))
    buttons.ubutton(BotTheme('ST_BN2_NAME'), BotTheme('ST_BN2_URL'))
    reply_markup = buttons.build_menu(2)
    if TG_CONFIG.token_timeout:
        replyhi = message.reply_to_message
        userid = replyhi.from_user.id
    #    encrypted_url = message.command[1]
      #  input_token, pre_uid = (b64decode(encrypted_url.encode()).decode()).split('&&')
    #    if int(pre_uid) != userid:
    #        return await sendMessage(message, BotTheme('OWN_TOKEN_GENERATE'))
        data = user_data.get(userid, {})
      #  input_token=data['token']
     #   if 'token' not in data or data['token'] != input_token:
      #      return await sendMessage(message, BotTheme('USED_TOKEN'))
     #   elif config_dict['LOGIN_PASS'] is not None and data['token'] == config_dict['LOGIN_PASS']:
       #     return await sendMessage(message, BotTheme('LOGGED_PASSWORD'))
        buttons.ibutton(BotTheme('ACTIVATE_BUTTON'), f'vpass {input_token}', 'header')
        reply_markup = buttons.build_menu(2)
        msg = BotTheme('TOKEN_MSG', token=input_token, validity=get_readable_time(int(TG_CONFIG.token_timeout)))
        return await sendMessage(message, msg, reply_markup)


async def tokenverify(client, message):
    user_id = message.from_user.id
    button = None
    token_msg, btn = await checking_access(user_id, button)
    if token_msg is not None:
        return await sendMessage(message, token_msg, btn.build_menu(1))
        
    if token_msg is None:
        msg2 = "You Are Verified Don't Worry✨"
        return await sendMessage(message, msg2)
        

async def token_callbackverify(_, query):
    user_id = query.from_user.id
    input_token = query.data.split()[1]
    data = user_data.get(user_id, {})
 #   if 'token' not in data or data['token'] != input_token:
  #      return await query.answer('Already Used, Generate New One', show_alert=True)
    update_user_ldata(user_id, 'token', str(uuid4()))
    update_user_ldata(user_id, 'time', time())
    await query.answer('Activated Temporary Token!', show_alert=True)
    kb = query.message.reply_markup.inline_keyboard[1:]
    kb.insert(0, [InlineKeyboardButton(BotTheme('ACTIVATED'), callback_data='pass activated')])
    return await editReplyMarkup(query.message, InlineKeyboardMarkup(kb))
#botStartTime = time()
async def editReplyMarkup(message, reply_markup):
    try:
        return await message.edit_reply_markup(reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

async def deleteMessage(message):
    try:
        await message.delete()
    except Exception as e:
       # LOGGER.error(str(e))
        return str(e)
        
async def sendMessage(message, text, buttons=None, photo=None, **kwargs):
    try:
        return await message.reply(text=text, quote=True, disable_web_page_preview=True, disable_notification=True,
                                    reply_markup=buttons, reply_to_message_id=rply.id if (rply := message.reply_to_message) and not rply.text and not rply.caption else None,
                                    **kwargs)
    except Exception as e:
     #   LOGGER.error(format_exc())
        return str(e)

@app.on_message(filters.chat(TG_CONFIG.sudo_users) & filters.command('gdrive2'))
async def gdrive_helper(_, message):
    if len(message.text.split()) == 1:
        if not os.path.exists(client_secrets_json):
            await message.reply(
                "<b>No Client Secrets JSON File Found!</b>",
            )
            return
        
        if not os.path.exists(token_file):
            try:
                authurl = gauth.GetAuthUrl().replace("online", "offline")
            except auth.AuthenticationError:
                await message.reply(
                    '<b>Wrong Credentials!</b>',
                )
                return
            
            text = (
                '<b>Login In To Google Drive</b>\n<b>Send</b>`/gdrive [verification_code]`'
            )
            await message.reply(text, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔗 Log In URL", url=f"{authurl}")
                    ]
                ]
            ))
            return
        await message.reply(
            "<b>You're already logged in!\nTo logout type</b><code>/gdrive logout</code>",
        )
    #/gdrive logout
    elif len(message.text.split()) == 2 and message.text.split()[1] == 'logout':
        os.remove(token_file)
        await message.reply(
            '<b>You have logged out of your account!</b>',
        )
    #/gdrive [verification_code]
    elif len(message.text.split()) == 2:
        gauth.LoadCredentialsFile(token_file)
        try:
            if "localhost" in message.text.split()[1]:
                gauth.Auth(find_auth_code(message.text.split()[1]))
            else:
                gauth.Auth(message.text.split()[1])

        except auth.AuthenticationError:
            await message.reply('<b>Your Authentication code is Wrong!</b>')
            return
        gauth.SaveCredentialsFile(token_file)
        await message.reply(
            '<b>Authentication successful!</b>',
        )
    else:
        await message.reply('<b>Invaild args!</b>\nCheck <code>/gdrive</code> for usage guide')


async def wzmlxcb(_, query):
    message = query.message
    user_id = query.from_user.id
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Not Yours Apna khud ka Generate kar stats se✨", show_alert=True)
    elif data[2] == "stats":
        msg, btn = await get_stats(query, data[3])
        await editMessage(message, msg, btn)
    else:
        await query.answer()
        await deleteMessage(message)
        if message.reply_to_message:
            await deleteMessage(message.reply_to_message)
            if message.reply_to_message.reply_to_message:
                await deleteMessage(message.reply_to_message.reply_to_message)
                




async def editMessage(message, text, buttons=None, photo=None):
    try:
        await message.edit(text=text, disable_web_page_preview=True, reply_markup=buttons)
    except Exception as e:
        #LOGGER.error(str(e))
        return str(e)
@app.on_message(filters.chat(TG_CONFIG.sudo_users) & filters.incoming & filters.command(['webdl2']) & filters.text)
async def webdl_cmd_handler(app, message):
    user_id = message.from_user.id
    button = None
    token_msg, btn = await checking_access(user_id, button)
    if token_msg is not None:
        return await sendMessage(message, token_msg, btn.build_menu(1))
    if len(message.text.split(" ")) <= 2:
        message.reply_text(
            "<b>Syntax: </b>`/webdl1 -c [CHANNEL SLUG] [OTHER ARGUMENTS]`")
        return
    
    command = message.text.replace("/webdl2", "").strip()
    if "-c" in command:
        from bot.services.tplay.main import TPLAY
        downloader = TPLAY(command, app, message)
        downloader.start_process()

async def ping(_, message):
    start_time = monotonic()
    reply = await sendMessage(message, BotTheme('PING'))
    end_time = monotonic()
    await editMessage(reply, BotTheme('PING_VALUE', value=int((end_time - start_time) * 1000)))
    


#@app.on_message(filters.command("trestart") & filters.private)
async def restart(client, message):
    # Check if the message is from the owner
    if message.from_user.id == TG_CONFIG.owner_id:
        restart_message = await sendMessage(message, BotTheme('RESTARTING'))
        # Send a confirmation message to the owner
        message.reply("Restarting bot...")
        proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'ffmpeg')
        proc2 = await create_subprocess_exec('python3', 'update.py')
        await gather(proc1.wait(), proc2.wait())
        async with aiopen(".restartmsg", "w") as f:
            await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
        # Restart the bot
        os.execl(sys.executable, sys.executable, "-m", "bot")
    else:
        message.reply("You're not authorized to restart the bot!")

@app.on_message(filters.incoming & filters.command(['start']) & filters.text)
async def start_cmd_handler(app, message):
    code = "Access Denied" if message.from_user.id not in TG_CONFIG.sudo_users else "Welcome Admin Test Started"
    await message.reply_text(START_MSG.format(message.from_user.username, code))
    buttons = ButtonMaker()
    buttons.ubutton(BotTheme('ST_BN1_NAME'), BotTheme('ST_BN1_URL'))
    buttons.ubutton(BotTheme('ST_BN2_NAME'), BotTheme('ST_BN2_URL'))
    reply_markup = buttons.build_menu(2)
    if len(message.command) > 1:
        userid = message.from_user.id
        encrypted_url = message.command[1]
        input_token, pre_uid = (b64decode(encrypted_url.encode()).decode()).split('&&')
        if int(pre_uid) != userid:
            return await sendMessage(message, BotTheme('OWN_TOKEN_GENERATE'))
        data = user_data.get(userid, {})
        if 'token' not in data or data['token'] != input_token:
            return await sendMessage(message, BotTheme('USED_TOKEN'))
      #  elif config_dict['LOGIN_PASS'] is not None and data['token'] == config_dict['LOGIN_PASS']:
          #  return await sendMessage(message, BotTheme('LOGGED_PASSWORD'))
        buttons.ibutton(BotTheme('ACTIVATE_BUTTON'), f'pass {input_token}', 'header')
        reply_markup = buttons.build_menu(2)
        msg = BotTheme('TOKEN_MSG', token=input_token, validity=get_readable_time(int(TG_CONFIG.token_timeout)))
        return await sendMessage(message, msg, reply_markup)
 #   elif await CustomFilters.authorized(client, message):
     #   start_string = BotTheme('ST_MSG', help_command=f"/{BotCommands.HelpCommand}")
      #  await sendMessage(message, start_string, reply_markup, photo='IMAGES')
   # elif config_dict['BOT_PM']:
      #  await sendMessage(message, BotTheme('ST_BOTPM'), reply_markup, photo='IMAGES')
  #  else:
        #await sendMessage(message, BotTheme('ST_UNAUTH'), reply_markup, photo='IMAGES')
    await DbManager().update_pm_users(message.from_user.id)

async def token_callback(_, query):
    user_id = query.from_user.id
    input_token = query.data.split()[1]
    data = user_data.get(user_id, {})
    if 'token' not in data or data['token'] != input_token:
        return await query.answer('Already Used, Generate New One', show_alert=True)
    update_user_ldata(user_id, 'token', str(uuid4()))
    update_user_ldata(user_id, 'time', time())
    await query.answer('Activated Temporary Token!', show_alert=True)
    kb = query.message.reply_markup.inline_keyboard[1:]
    kb.insert(0, [InlineKeyboardButton(BotTheme('ACTIVATED'), callback_data='pass activated')])
    await editReplyMarkup(query.message, InlineKeyboardMarkup(kb))


async def sendFile(message, file):
    try:
        return await message.reply_document(document=file)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

#async def deploy(client, message):
  #  await app.start()
  #  app1 = web.AppRunner(await web_server())
 #   await app1.setup()
 #   bind_address = "0.0.0.0"
 #   await web.TCPSite(app1, bind_address, 80).start()
async def stats(client, message):
    msg, btns = await get_stats(message)
    await sendMessage(message, msg, btns)


async def log(_, message):
    await sendFile(message, 'log.txt')

async def main():
    await app.start()
    LOGGER.info("bot started")
    app.add_handler(MessageHandler(log, filters=command('log2')))
    app.add_handler(MessageHandler(tokenverify, filters=command('token')))
    app.add_handler(MessageHandler(verify, filters=command('verify')))
  #  app.add_handler(MessageHandler(unverify, filters=command('unverify') & CustomFilters.sudo))
  #  app.add_handler(MessageHandler(deploy, filters=command('deploy')))
    app.add_handler(MessageHandler(restart, filters=command('trestart2')))
    app.add_handler(MessageHandler(ping, filters=command('ping2')))
    app.add_handler(CallbackQueryHandler(wzmlxcb, filters=regex(r'^wzmlx')))
    app.add_handler(CallbackQueryHandler(token_callback, filters=regex(r'^pass')))
    app.add_handler(CallbackQueryHandler(token_callbackverify, filters=regex(r'^vpass')))
    app.add_handler(MessageHandler(stats, filters=command('stats2')))
    app.add_handler(MessageHandler(shell, filters=command('shell')))
    app.add_handler(EditedMessageHandler(shell, filters=command('shell')))
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.loop.run_until_complete(main())
