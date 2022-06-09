from typing import Dict, List, Union

from pyrogram import Client, filters

from Ayiin import BOT_USERNAME, MUSIC_BOT_NAME, app, db
from Ayiin.Database import _get_theme, get_theme, save_theme
from Ayiin.Decorators.permission import PermissionCheck

themes = [
    "blue",
    "black",
    "red",
    "green",
    "grey",
    "orange",
    "pink",
    "yellow",
    "Random",
]

themes2 = [
    "blue",
    "black",
    "red",
    "green",
    "grey",
    "orange",
    "pink",
    "yellow",
]

__MODULE__ = "Theme"
__HELP__ = """


/settheme
- Tetapkan tema untuk gambar mini.

/theme
- Periksa Tema untuk obrolan Anda.
"""


@app.on_message(
    filters.command(["settheme", f"settheme@{BOT_USERNAME}"]) & filters.group
)
async def settheme(_, message):
    usage = f"Ini bukan tema.\n\nPilih dari mereka\n{' | '.join(themes)}\n\nGunakan 'Random' untuk mendapatkan pilihan tema secara acak"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    theme = message.text.split(None, 1)[1].strip()
    if theme not in themes:
        return await message.reply_text(usage)
    note = {
        "theme": theme,
    }
    await save_theme(message.chat.id, "theme", note)
    await message.reply_text(f"Mengubah tema gambar mini menjadi {theme}")


@app.on_message(filters.command("theme"))
@PermissionCheck
async def theme_func(_, message):
    await message.delete()
    _note = await get_theme(message.chat.id, "theme")
    if not _note:
        theme = "Random"
    else:
        theme = _note["theme"]
    await message.reply_text(
        f"**{MUSIC_BOT_NAME} Tema Thumbnail**\n\n**Tema Saat Ini:-** {theme}\n\n**Tema yang Tersedia:-** {' | '.join(themes2)} \n\nGunakan /settheme untuk mengubah tema."
    )
