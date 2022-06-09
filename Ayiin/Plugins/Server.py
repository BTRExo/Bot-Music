import asyncio
import math
import os
import dotenv
import random
import shutil
from datetime import datetime
from time import strftime, time

import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import Client, filters
from pyrogram.types import Message

from config import (HEROKU_API_KEY, HEROKU_APP_NAME, UPSTREAM_BRANCH,
                    UPSTREAM_REPO)
from Ayiin import LOG_GROUP_ID, MUSIC_BOT_NAME, SUDOERS, app
from Ayiin.Database import get_active_chats, remove_active_chat, remove_active_video_chat
from Ayiin.Utilities.heroku import is_heroku, user_input
from Ayiin.Utilities.paste import isPreviewUp, paste_queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__MODULE__ = "Server"
__HELP__ = f"""

**Note:**
**Hanya untuk Pengguna Sudo**

/get_log
- Dapatkan log 100 baris terakhir dari Heroku.

/get_var
- Dapatkan config var dari Heroku atau .env.

/del_var
- Hapus semua var di Heroku atau .env.

/set_var [Var Name] [Value]
- Setel Var atau Perbarui Var di heroku atau .env. Pisahkan Var dan Nilainya dengan spasi.

/usage
- Dapatkan Penggunaan Dyno.

/update
- Perbarui Bot Anda.

/restart 
- Mulai ulang Bot [Semua unduhan, cache, file mentah akan dihapus juga].
"""


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]


@app.on_message(filters.command("get_log") & filters.user(SUDOERS))
async def log_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
    else:
        return await message.reply_text("Only for Heroku Apps")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        happ = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            "Pastikan Kunci API Heroku Anda, Nama Aplikasi Anda dikonfigurasi dengan benar di heroku"
        )
    data = happ.get_log()
    if len(data) > 1024:
        link = await paste_queue(data)
        url = link + "/index.txt"
        return await message.reply_text(
            f"Ini Log Aplikasi Anda[{HEROKU_APP_NAME}]\n\n[Klik Di Sini untuk checkout Log]({url})"
        )
    else:
        return await message.reply_text(data)


@app.on_message(filters.command("get_var") & filters.user(SUDOERS))
async def varget_(client, message):
    usage = "**Usage:**\n/get_var [Var Name]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Pastikan Kunci API Heroku Anda, Nama Aplikasi Anda dikonfigurasi dengan benar di heroku"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"**Heroku Config:**\n\n**{check_var}:** `{heroku_config[check_var]}`"
            )
        else:
            return await message.reply_text("No such Var")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env tidak ditemukan.")
        output = dotenv.get_key(path, check_var)
        if not output:
            return await message.reply_text("Tidak seperti itu")
        else:
            return await message.reply_text(f".env:\n\n**{check_var}:** `{str(output)}`")


@app.on_message(filters.command("del_var") & filters.user(SUDOERS))
async def vardel_(client, message):
    usage = "**Usage:**\n/del_var [Var Name]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Pastikan Kunci API Heroku Anda, Nama Aplikasi Anda dikonfigurasi dengan benar di heroku"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            await message.reply_text(
                f"**Penghapusan Heroku Var:**\n\n`{check_var}` telah berhasil dihapus."
            )
            del heroku_config[check_var]
        else:
            return await message.reply_text(f"No such Var")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env tidak ditemukan.")
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text("Tidak seperti itu")
        else:
            return await message.reply_text(f".env Penghapusan Var:\n\n`{check_var}` telah berhasil dihapus. Untuk memulai ulang perintah bot ketik /restart.")


@app.on_message(filters.command("set_var") & filters.user(SUDOERS))
async def set_var(client, message):
    usage = "**Usage:**\n/set_var [Var Name] [Var Value]"
    if len(message.command) < 3:
        return await message.reply_text(usage)
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Pastikan Kunci API Heroku Anda, Nama Aplikasi Anda dikonfigurasi dengan benar di heroku"
            )
        heroku_config = happ.config()
        if to_set in heroku_config:
            await message.reply_text(
                f"**Pembaruan Heroku Var:**\n\n`{to_set}` telah berhasil diperbarui. Bot akan Mulai Ulang Sekarang."
            )
        else:
            await message.reply_text(
                f"Menambahkan Var Baru dengan nama `{to_set}`. Bot akan Mulai Ulang Sekarang."
            )
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env tidak ditemukan.")
        output = dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            return await message.reply_text(f"**.env Pembaruan Var:**\n\n`{to_set}`telah berhasil diperbarui. Untuk memulai ulang perintah bot /restart.")
        else:
            return await message.reply_text(f"**.env dəyişən əlavə edilməsi:**\n\n`{to_set}` telah berhasil diperbarui. Untuk memulai ulang perintah bot /restart.")


@app.on_message(filters.command("usage") & filters.user(SUDOERS))
async def usage_dynos(client, message):
    ### Credits CatUserbot
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
    else:
        return await message.reply_text("Only for Heroku Apps")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        happ = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            " Pastikan Kunci API Heroku Anda, Nama Aplikasi Anda dikonfigurasi dengan benar di heroku"
        )
    dyno = await message.reply_text("Checking Heroku Usage. Please Wait")
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Unable to fetch.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**DYNO USAGE**

<u>Usage:</u>
Total Used: `{AppHours}`**h**  `{AppMinutes}`**m**  [`{AppPercentage}`**%**]

<u>Remaining Quota:</u>
Total Left: `{hours}`**h**  `{minutes}`**m**  [`{percentage}`**%**]"""
    return await dyno.edit(text)


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memperbarui aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memperbarui dari jarak jauh!</b>"
            )
    response = await message.reply_text("Memeriksa pembaruan yang tersedia...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Kesalahan Perintah")
    except InvalidGitRepositoryError:
        return await response.edit("Repositori Git Tidak Valid")
    to_exc = f"git fetch origin {UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[
            (format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4
        ],
    )
    for info in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>Pembaruan baru tersedia untuk Bot!</b>\n\n➣ Push Pembaruan Sekarang</code>\n\n**<u>Pembaruan:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        link = await paste_queue(updates)
        url = link + "/index.txt"
        nrs = await response.edit(
            f"<b>Pembaruan baru tersedia untuk Bot!</b>\n\n➣ Push Pembaruan Sekarang</code>\n\n**<u>Pembaruan:</u>**\n\n[Klik Di Sini untuk checkout Pembaruan]({url})"
        )
    else:
        nrs = await response.edit(
            _final_updates_, disable_web_page_preview=True
        )
    os.system("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text}\n\nBot berhasil diperbarui di Heroku! Sekarang, tunggu 2 - 3 menit sampai bot restart!"
            )
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nTerjadi masalah saat memulai boot ulang! Silakan coba lagi nanti atau periksa log untuk info lebih lanjut."
            )
            return await app.send_message(
                LOG_GROUP_ID,
                f"PENGECUALIAN TERJADI DI #UPDATER KARENA: <code>{err}</code>",
            )
    else:
        await response.edit(
            f"{nrs.text}\n\nBot berhasil diperbarui! Sekarang, tunggu 1 - 2 menit hingga bot reboot!"
        )
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()
    return


@app.on_message(filters.command("restart") & filters.user(SUDOERS))
async def restart_(_, message):
    response = await message.reply_text("Restarting....")
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\nUntuk memulai ulang aplikasi, Anda perlu menyiapkan var `HEROKU_API_KEY` dan `HEROKU_APP_NAME` masing-masing!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU APP DETECTED!</b>\n\n<b>Pastikan untuk menambahkan kedua var</b> `HEROKU_API_KEY` **dan** `HEROKU_APP_NAME` <b>dengan benar agar dapat memulai ulang dari jarak jauh!</b>"
            )
        try:
            served_chats = []
            try:
                chats = await get_active_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
            except Exception as e:
                pass
            for x in served_chats:
                try:
                    await app.send_message(
                        x,
                        f"{MUSIC_BOT_NAME} baru saja me-restart dirinya sendiri. Maaf atas masalah ini.\n\nMulai mainkan lagi setelah 10-15 detik.",
                    )
                    await remove_active_chat(x)
                    await remove_active_video_chat(x)
                except Exception:
                    pass
            heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME].restart()
            await response.edit(
                "**Heroku Restart**\n\nReboot telah berhasil dimulai! Tunggu selama 1 - 2 menit hingga bot restart."
            )
            return
        except Exception as err:
            await response.edit(
                "Terjadi masalah saat memulai boot ulang! Silakan coba lagi nanti atau periksa log untuk info lebih lanjut."
            )
            return
    else:
        served_chats = []
        try:
            chats = await get_active_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
        except Exception as e:
            pass
        for x in served_chats:
            try:
                await app.send_message(
                    x,
                    f"{MUSIC_BOT_NAME} baru saja me-restart dirinya sendiri. Maaf atas masalah ini.\n\nMulai bermain lagi setelah 10-15 detik.",
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except Exception:
                pass
        A = "downloads"
        B = "raw_files"
        C = "cache"
        D = "search"
        try:
            shutil.rmtree(A)
            shutil.rmtree(B)
            shutil.rmtree(C)
            shutil.rmtree(D)
        except:
            pass
        await asyncio.sleep(2)
        try:
            os.mkdir(A)
        except:
            pass
        try:
            os.mkdir(B)
        except:
            pass
        try:
            os.mkdir(C)
        except:
            pass
        try:
            os.mkdir(D)
        except:
            pass
        await response.edit(
            "Reboot telah berhasil dimulai! Tunggu selama 1 - 2 menit hingga bot restart."
        )
        os.system(f"kill -9 {os.getpid()} && bash start")
