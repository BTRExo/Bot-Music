import random

from pyrogram import filters
from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQueryResultArticle,
                            InlineQueryResultPhoto, InputTextMessageContent,
                            Message)

from Ayiin import ASSISTANT_PREFIX, SUDOERS, app, random_assistant
from Ayiin.Database import get_assistant, save_assistant
from Ayiin.Utilities.assistant import get_assistant_details

__MODULE__ = "Assistant"
__HELP__ = f"""


/checkassistant
- Periksa asisten yang dialokasikan untuk obrolan Anda


**Note:**
- Hanya untuk Pengguna Sudo

{ASSISTANT_PREFIX[0]}block [Membalas Pesan Pengguna] 
- Memblokir Pengguna dari Akun Asisten.

{ASSISTANT_PREFIX[0]}unblock [Membalas Pesan Pengguna] 
- Buka blokir Pengguna dari Akun Asisten.

{ASSISTANT_PREFIX[0]}approve [Membalas Pesan Pengguna] 
- Menyetujui Pengguna untuk PM.

{ASSISTANT_PREFIX[0]}disapprove [Membalas Pesan Pengguna] 
- Menolak Pengguna untuk PM.

{ASSISTANT_PREFIX[0]}pfp [Balas ke Foto] 
- Mengubah PFP akun Asisten.

{ASSISTANT_PREFIX[0]}bio [Bio text] 
- Mengubah Bio Akun Asisten.

/changeassistant [ASS NUMBER]
- Ubah asisten yang diberikan sebelumnya ke yang baru.

/setassistant [ASS NUMBER or Random]
- Setel akun asisten untuk mengobrol.
"""


ass_num_list = ["1", "2", "3", "4", "5"]


@app.on_message(filters.command("changeassistant") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**Usage:**\n/changeassistant [ASS_NO]\n\nPilih dari mereka\n{' | '.join(ass_num_list)}"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    num = message.text.split(None, 1)[1].strip()
    if num not in ass_num_list:
        return await message.reply_text(usage)
    ass_num = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Tidak Ada Asisten yang Disimpan Sebelumnya Ditemukan.\n\nAnda dapat menyetel Asisten Melalui /setassistant"
        )
    else:
        ass = _assistant["saveassistant"]
    assis = {
        "saveassistant": ass_num,
    }
    await save_assistant(message.chat.id, "assistant", assis)
    await message.reply_text(
        f"**Berubah Asisten**\n\nMengubah Akun Asisten dari **{ass}** ke Nomor Asisten **{ass_num}**"
    )


ass_num_list2 = ["1", "2", "3", "4", "5", "Random"]


@app.on_message(filters.command("setassistant") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**Usage:**\n/setassistant [ASS_NO or Random]\n\nPilih dari mereka\n{' | '.join(ass_num_list2)}\n\nGunakan 'Random' untuk mengatur Asisten acak"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    query = message.text.split(None, 1)[1].strip()
    if query not in ass_num_list2:
        return await message.reply_text(usage)
    if str(query) == "Random":
        ran_ass = random.choice(random_assistant)
    else:
        ran_ass = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        await message.reply_text(
            f"**__Asisten Bot Musik Diberikan__**\n\nAsisten No. **{ran_ass}**"
        )
        assis = {
            "saveassistant": ran_ass,
        }
        await save_assistant(message.chat.id, "assistant", assis)
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Nomor Asisten yang Disimpan Sebelumnya {ass} Ditemukan.\n\nAnda dapat mengubah Asisten Melalui /changeassistant"
        )


@app.on_message(filters.command("checkassistant") & filters.group)
async def check_ass(_, message: Message):
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Tidak Ada Asisten yang Disimpan Sebelumnya Ditemukan.\n\nAnda dapat menyetel Asisten Melalui /play"
        )
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Asisten yang Disimpan Sebelumnya Ditemukan\n\nNomor Asisten {ass} "
        )
