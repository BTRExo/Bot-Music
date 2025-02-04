import asyncio
from os import path

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto,
                            KeyboardButton, Message, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove, Voice)
from youtube_search import YoutubeSearch
from youtubesearchpython import VideosSearch

from Ayiin import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from Ayiin.Core.PyTgCalls.Converter import convert
from Ayiin.Core.PyTgCalls.Downloader import download
from Ayiin.Database import (get_active_video_chats, get_video_limit,
                            is_active_video_chat, is_on_off)
from Ayiin.Decorators.assistant import AssistantAdd
from Ayiin.Decorators.checker import checker
from Ayiin.Decorators.permission import PermissionCheck
from Ayiin.Inline import (choose_markup, livestream_markup, playlist_markup,
                          search_markup, search_markup2, stream_quality_markup,
                          url_markup, url_markup2)
from Ayiin.Utilities.changers import seconds_to_min, time_to_seconds
from Ayiin.Utilities.chat import specialfont_to_normal
from Ayiin.Utilities.theme import check_theme
from Ayiin.Utilities.thumbnails import gen_thumb
from Ayiin.Utilities.url import get_url
from Ayiin.Utilities.videostream import start_live_stream, start_video_stream
from Ayiin.Utilities.youtube import (get_m3u8, get_yt_info_id,
                                     get_yt_info_query,
                                     get_yt_info_query_slider)

loop = asyncio.get_event_loop()

__MODULE__ = "VideoCalls"
__HELP__ = f"""

/play [Balas ke Video mana pun] atau [Tautan YT] atau [Nama Musik]
- Streaming Video di Obrolan Suara

**Untuk Pengguna Sudo:-**

/set_video_limit [Jumlah Obrolan]
- Tetapkan Jumlah Obrolan maksimum yang diizinkan untuk Panggilan Video dalam satu waktu.


"""


@app.on_callback_query(filters.regex(pattern=r"Ayiin"))
async def choose_playmode(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, duration, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "This is not for you! Search You Own Song.", show_alert=True
        )
    buttons = choose_markup(videoid, duration, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"Choose"))
async def quality_markup(_, CallbackQuery):
    limit = await get_video_limit(141414)
    if not limit:
        await CallbackQuery.message.delete()
        return await CallbackQuery.message.reply_text(
            "**Tidak Ada Batas yang Ditentukan untuk Panggilan Video**\n\nTetapkan Batas untuk Jumlah Panggilan Video Maksimum yang diizinkan di Bot /set_video_limit [Hanya Pengguna Sudo]"
        )
    count = len(await get_active_video_chats())
    if int(count) == int(limit):
        if await is_active_video_chat(CallbackQuery.message.chat.id):
            pass
        else:
            return await CallbackQuery.answer(
                "Maaf! Bot hanya mengizinkan panggilan video dalam jumlah terbatas karena masalah kelebihan CPU. Obrolan lain menggunakan panggilan video sekarang. Coba beralih ke audio atau coba lagi nanti",
                show_alert=True,
            )
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    try:
        read1 = db_mem[CallbackQuery.message.chat.id]["live_check"]
        if read1:
            return await CallbackQuery.answer(
                "Pemutaran Live Streaming... Hentikan untuk memutar musik",
                show_alert=True,
            )
        else:
            pass
    except:
        pass
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, duration, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Ini bukan untukmu! Cari Lagu Anda Sendiri.", show_alert=True
        )
    buttons = stream_quality_markup(videoid, duration, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"LiveStream"))
async def Live_Videos_Stream(_, CallbackQuery):
    limit = await get_video_limit(141414)
    if not limit:
        await CallbackQuery.message.delete()
        return await CallbackQuery.message.reply_text(
            "**Tidak Ada Batas yang Ditentukan untuk Panggilan Video**\n\nTetapkan Batas untuk Jumlah Panggilan Video Maksimum yang diizinkan di Bot /set_video_limit [Hanya Pengguna Sudo]"
        )
    count = len(await get_active_video_chats())
    if int(count) == int(limit):
        if await is_active_video_chat(CallbackQuery.message.chat.id):
            pass
        else:
            return await CallbackQuery.answer(
                "Maaf! Bot hanya mengizinkan panggilan video dalam jumlah terbatas karena masalah kelebihan CPU. Obrolan lain menggunakan panggilan video sekarang. Coba beralih ke audio atau coba lagi nanti",
                show_alert=True,
            )
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    quality, videoid, duration, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Ini bukan untukmu! Cari Lagu Anda Sendiri.", show_alert=True
        )
    await CallbackQuery.message.delete()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    await CallbackQuery.answer()
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(thumbnail, title, user_id, theme, chat_title)
    nrs, ytlink = await get_m3u8(videoid)
    if nrs == 0:
        return await CallbackQuery.message.reply_text(
            "Format Video tidak Ditemukan.."
        )
    await start_live_stream(
        CallbackQuery,
        quality,
        ytlink,
        thumb,
        title,
        duration_min,
        duration_sec,
        videoid,
    )


@app.on_callback_query(filters.regex(pattern=r"VideoStream"))
async def Videos_Stream(_, CallbackQuery):
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    quality, videoid, duration, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Ini bukan untukmu! Cari Lagu Anda Sendiri.", show_alert=True
        )
    if str(duration) == "None":
        buttons = livestream_markup(quality, videoid, duration, user_id)
        return await CallbackQuery.edit_message_text(
            "**Streaming Langsung Terdeteksi**\n\nIngin memutar streaming langsung? Ini akan menghentikan musik yang sedang diputar (jika ada) dan akan memulai streaming video langsung.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    await CallbackQuery.message.delete()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    if duration_sec > DURATION_LIMIT:
        return await CallbackQuery.message.reply_text(
            f"**Batas Durasi Terlampaui**\n\n**Durasi yang Diizinkan: **{DURATION_LIMIT_MIN} menit\n**Durasi yang Diterima:** {duration_min} minute(s)"
        )
    await CallbackQuery.answer()
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(thumbnail, title, user_id, theme, chat_title)
    nrs, ytlink = await get_m3u8(videoid)
    if nrs == 0:
        return await CallbackQuery.message.reply_text(
            "Format Video tidak Ditemukan.."
        )
    await start_video_stream(
        CallbackQuery,
        quality,
        ytlink,
        thumb,
        title,
        duration_min,
        duration_sec,
        videoid,
    )
