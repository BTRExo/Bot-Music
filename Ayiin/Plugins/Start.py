import asyncio
import random
import time
from sys import version as pyver
from typing import Dict, List, Union

import psutil
from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InputMediaPhoto, Message)

from Ayiin import ASSIDS, BOT_ID, MUSIC_BOT_NAME, OWNER_ID, SUDOERS, app
from Ayiin import boottime as bot_start_time
from Ayiin import db, random_assistant
from Ayiin.Core.PyTgCalls import Ayiin
from Ayiin.Database import (add_nonadmin_chat, add_served_chat,
                            blacklisted_chats, get_assistant, get_authuser,
                            get_authuser_names, get_start, is_nonadmin_chat,
                            is_served_chat, remove_active_chat,
                            remove_nonadmin_chat, save_assistant, save_start)
from Ayiin.Decorators.admins import ActualAdminCB
from Ayiin.Decorators.permission import PermissionCheck
from Ayiin.Inline import (custommarkup, dashmarkup, setting_markup,
                          setting_markup2, start_pannel, usermarkup, volmarkup)
from Ayiin.Utilities.assistant import get_assistant_details
from Ayiin.Utilities.ping import get_readable_time

welcome_group = 2

__MODULE__ = "Essentials"
__HELP__ = """


/start 
- Mulai Bot.


/help 
- Dapatkan Menu Pembantu Perintah.


/settings 
- Dapatkan tombol Pengaturan.
"""


@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(_, message: Message):
    chat_id = message.chat.id
    if await is_served_chat(chat_id):
        pass
    else:
        await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            if member.id == BOT_ID:
                if chat_id in await blacklisted_chats():
                    await message.reply_text(
                        f"Hushh, Grup obrolan Anda[{message.chat.title}] telah masuk daftar hitam!\n\nMinta Pengguna Sudo untuk memasukkan obrolan Anda ke daftar putih"
                    )
                    return await app.leave_chat(chat_id)
                _assistant = await get_assistant(message.chat.id, "assistant")
                if not _assistant:
                    ran_ass = random.choice(random_assistant)
                    assis = {
                        "saveassistant": ran_ass,
                    }
                    await save_assistant(message.chat.id, "assistant", assis)
                else:
                    ran_ass = _assistant["saveassistant"]
                (
                    ASS_ID,
                    ASS_NAME,
                    ASS_USERNAME,
                    ASS_ACC,
                ) = await get_assistant_details(ran_ass)
                out = start_pannel()
                await message.reply_text(
                    f"Welcome To {MUSIC_BOT_NAME}\n\nPromote me as administrator in your group otherwise I will not function properly.\n\nAssistant UsernameSelamat Datang Di {MUSIC_BOT_NAME}\n\nPromosikan saya sebagai administrator di grup Anda jika tidak, saya tidak akan berfungsi dengan baik.\n\nAsisten Username:- @{ASS_USERNAME}\nAsisten ID:- {ASS_ID}",
                    reply_markup=InlineKeyboardMarkup(out[1]),
                )
            if member.id in ASSIDS:
                return await remove_active_chat(chat_id)
            if member.id in OWNER_ID:
                return await message.reply_text(
                    f"{MUSIC_BOT_NAME}' Pemilik[{member.mention}] baru saja bergabung dengan obrolan Anda."
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    f"Seorang anggota Pengguna Sudo {MUSIC_BOT_NAME}[{member.mention}] baru saja bergabung dengan obrolan Anda."
                )
            return
        except:
            return


@app.on_message(filters.command(["help", "start"]) & filters.group)
@PermissionCheck
async def useradd(_, message: Message):
    out = start_pannel()
    await asyncio.gather(
        message.delete(),
        message.reply_text(
            f"Terima kasih telah menerima saya di {message.chat.title}.\n{MUSIC_BOT_NAME} Hidup.\n\nUntuk bantuan atau bantuan apa pun, periksa grup dan saluran dukungan kami.",
            reply_markup=InlineKeyboardMarkup(out[1]),
        ),
    )


@app.on_message(filters.command("settings") & filters.group)
@PermissionCheck
async def settings(_, message: Message):
    c_id = message.chat.id
    _check = await get_start(c_id, "assistant")
    if not _check:
        assis = {
            "volume": 100,
        }
        await save_start(c_id, "assistant", assis)
        volume = 100
    else:
        volume = _check["volume"]
    text, buttons = setting_markup2()
    await asyncio.gather(
        message.delete(),
        message.reply_text(
            f"{text}\n\n**Group:** {message.chat.title}\n**Group ID:** {message.chat.id}\n**Volume Level:** {volume}%",
            reply_markup=InlineKeyboardMarkup(buttons),
        ),
    )


@app.on_callback_query(filters.regex("okaybhai"))
async def okaybhai(_, CallbackQuery):
    await CallbackQuery.answer("Going Back ...")
    out = start_pannel()
    await CallbackQuery.edit_message_text(
        text=f"Terima kasih telah menerima saya di {CallbackQuery.message.chat.title}.\n{MUSIC_BOT_NAME} Hidup.\n\nUntuk bantuan atau bantuan apa pun, periksa grup dan saluran dukungan kami.",
        reply_markup=InlineKeyboardMarkup(out[1]),
    )


@app.on_callback_query(filters.regex("settingm"))
async def settingm(_, CallbackQuery):
    await CallbackQuery.answer("Bot Settings ...")
    text, buttons = setting_markup()
    c_title = CallbackQuery.message.chat.title
    c_id = CallbackQuery.message.chat.id
    chat_id = CallbackQuery.message.chat.id
    _check = await get_start(c_id, "assistant")
    if not _check:
        assis = {
            "volume": 100,
        }
        await save_start(c_id, "assistant", assis)
        volume = 100
    else:
        volume = _check["volume"]
    await CallbackQuery.edit_message_text(
        text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex("EVE"))
@ActualAdminCB
async def EVE(_, CallbackQuery):
    checking = CallbackQuery.from_user.username
    text, buttons = usermarkup()
    chat_id = CallbackQuery.message.chat.id
    is_non_admin = await is_nonadmin_chat(chat_id)
    if not is_non_admin:
        await CallbackQuery.answer("Changes Saved")
        await add_nonadmin_chat(chat_id)
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\nMode Perintah Admin ke **Semua Orang**\n\nSekarang siapa pun yang ada di grup ini dapat skip, pause, resume, stop musik.\n\nPerubahan Selesai Oleh @{checking}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        await CallbackQuery.answer(
            "Mode Perintah Sudah Disetel Untuk SEMUA ORANG", show_alert=True
        )


@app.on_callback_query(filters.regex("AMS"))
@ActualAdminCB
async def AMS(_, CallbackQuery):
    checking = CallbackQuery.from_user.username
    text, buttons = usermarkup()
    chat_id = CallbackQuery.message.chat.id
    is_non_admin = await is_nonadmin_chat(chat_id)
    if not is_non_admin:
        await CallbackQuery.answer(
            "Mode Perintah Sudah Disetel Ke ADMIN SAJA", show_alert=True
        )
    else:
        await CallbackQuery.answer("Changes Saved")
        await remove_nonadmin_chat(chat_id)
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\nSetel Mode Perintah ke **Admin**\n\nSekarang hanya Admin yang ada di grup ini yang dapat skip, pause, resume, stop musik.\n\nPerubahan Selesai Oleh @{checking}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query(
    filters.regex(
        pattern=r"^(AQ|AV|AU|Dashboard|HV|LV|MV|HV|VAM|Custommarkup|PTEN|MTEN|PTF|MTF|PFZ|MFZ|USERLIST|UPT|CPT|RAT|DIT)$"
    )
)
async def start_markup_check(_, CallbackQuery):
    command = CallbackQuery.matches[0].group(1)
    c_title = CallbackQuery.message.chat.title
    c_id = CallbackQuery.message.chat.id
    chat_id = CallbackQuery.message.chat.id
    if command == "AQ":
        await CallbackQuery.answer("Already in Best Quality", show_alert=True)
    if command == "AV":
        await CallbackQuery.answer("Bot Settings ...")
        text, buttons = volmarkup()
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "AU":
        await CallbackQuery.answer("Bot Settings ...")
        text, buttons = usermarkup()
        is_non_admin = await is_nonadmin_chat(chat_id)
        if not is_non_admin:
            current = "Admins Only"
        else:
            current = "Everyone"
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n\nCurrently Who Can Use {MUSIC_BOT_NAME}:- **{current}**\n\n**⁉️ What is This?**\n\n**👥 Everyone :-**Anyone can use {MUSIC_BOT_NAME}'s commands(skip, pause, resume etc) present in this group.\n\n**🙍 Admin Only :-**  Only the admins and authorized users can use all commands of {MUSIC_BOT_NAME}.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "Dashboard":
        await CallbackQuery.answer("Dashboard...")
        text, buttons = dashmarkup()
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n\nCheck {MUSIC_BOT_NAME}'s System Stats In the DashBoard Here! More Functions adding very soon! Keep on Checking Support Channel.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "Custommarkup":
        await CallbackQuery.answer("Bot Settings ...")
        text, buttons = custommarkup()
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "LV":
        assis = {
            "volume": 25,
        }
        volume = 25
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = volmarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "MV":
        assis = {
            "volume": 50,
        }
        volume = 50
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = volmarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "HV":
        assis = {
            "volume": 100,
        }
        volume = 100
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = volmarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "VAM":
        assis = {
            "volume": 200,
        }
        volume = 200
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = volmarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "PTEN":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume + 10
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "MTEN":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume - 10
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "PTF":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume + 25
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "MTF":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume - 25
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "PFZ":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume + 50
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "MFZ":
        _check = await get_start(c_id, "assistant")
        volume = _check["volume"]
        volume = volume - 50
        if int(volume) > 200:
            volume = 200
        if int(volume) < 10:
            volume = 10
        assis = {
            "volume": volume,
        }
        try:
            await Ayiin.pytgcalls.change_volume_call(c_id, volume)
            await CallbackQuery.answer("Setting Audio Changes ...")
        except:
            return await CallbackQuery.answer("Tidak ada Panggilan Grup aktif...")
        await save_start(c_id, "assistant", assis)
        text, buttons = custommarkup()
        await CallbackQuery.edit_message_text(
            text=f"{text}\n\n**Group:** {c_title}\n**Group ID:** {c_id}\n**Volume Level:** {volume}%\n**Audio Quality:** Default Best",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if command == "USERLIST":
        await CallbackQuery.answer("Auth Users!")
        text, buttons = usermarkup()
        _playlist = await get_authuser_names(CallbackQuery.message.chat.id)
        if not _playlist:
            return await CallbackQuery.edit_message_text(
                text=f"{text}\n\nTidak Ada Pengguna Resmi yang Ditemukan\n\nAnda dapat mengizinkan non-admin menggunakan perintah admin saya dengan /auth dan menghapus dengan menggunakan /unauth",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            j = 0
            await CallbackQuery.edit_message_text(
                "Mengambil Pengguna Resmi... Harap Tunggu"
            )
            msg = f"**Daftar Pengguna Resmi[AUL]:**\n\n"
            for note in _playlist:
                _note = await get_authuser(
                    CallbackQuery.message.chat.id, note
                )
                user_id = _note["auth_user_id"]
                user_name = _note["auth_name"]
                admin_id = _note["admin_id"]
                admin_name = _note["admin_name"]
                try:
                    user = await app.get_users(user_id)
                    user = user.first_name
                    j += 1
                except Exception:
                    continue
                msg += f"{j}➤ {user}[`{user_id}`]\n"
                msg += f"    ┗ Added By:- {admin_name}[`{admin_id}`]\n\n"
            await CallbackQuery.edit_message_text(
                msg, reply_markup=InlineKeyboardMarkup(buttons)
            )
    if command == "UPT":
        bot_uptimee = int(time.time() - bot_start_time)
        Uptimeee = f"{get_readable_time((bot_uptimee))}"
        await CallbackQuery.answer(
            f"Bot's Uptime: {Uptimeee}", show_alert=True
        )
    if command == "CPT":
        cpue = psutil.cpu_percent(interval=0.5)
        await CallbackQuery.answer(
            f"Bot's Cpu Usage: {cpue}%", show_alert=True
        )
    if command == "RAT":
        meme = psutil.virtual_memory().percent
        await CallbackQuery.answer(
            f"Bot's Memory Usage: {meme}%", show_alert=True
        )
    if command == "DIT":
        diske = psutil.disk_usage("/").percent
        await CallbackQuery.answer(
            f"Ayiin Disk Usage: {diske}%", show_alert=True
        )
