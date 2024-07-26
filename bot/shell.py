from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe
from asyncio.subprocess import PIPE
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import ReplyMarkupInvalid, FloodWait, PeerIdInvalid, ChannelInvalid, RPCError, UserNotParticipant, MessageNotModified, MessageEmpty, PhotoInvalidDimensions, WebpageCurlFailed, MediaEmpty


from traceback import format_exc
#from asyncio import sleep
from aiofiles.os import remove as aioremove
from random import choice as rchoice
from time import time
from re import match as re_match


async def sendFile(message, file, caption=None, buttons=None):
    try:
        return await message.reply_document(document=file, quote=True, caption=caption, disable_notification=True, reply_markup=buttons)

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

async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode

#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.filters import command
from io import BytesIO





async def shell(_, message):
    cmd = message.text.split(maxsplit=1)
    if len(cmd) == 1:
        await sendMessage(message, 'No command to execute was given.')
        return
    cmd = cmd[1]
    stdout, stderr, _ = await cmd_exec(cmd, shell=True)
    reply = ''
    if len(stdout) != 0:
        reply += f"*Stdout*\n{stdout}\n"
       # LOGGER.info(f"Shell - {cmd} - {stdout}")
    if len(stderr) != 0:
        reply += f"*Stderr*\n{stderr}"
       # LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with BytesIO(str.encode(reply)) as out_file:
            out_file.name = "shell_output.txt"
            await sendFile(message, out_file)
    elif len(reply) != 0:
        await sendMessage(message, reply)
    else:
        await sendMessage(message, 'No Reply')



