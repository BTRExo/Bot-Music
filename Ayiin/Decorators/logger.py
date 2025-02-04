from config import LOG_GROUP_ID
from Ayiin.Core.Clients.cli import LOG_CLIENT
from Ayiin.Database import is_on_off


def logging(mystic):
    async def wrapper(_, message):
        if await is_on_off(5):
            if message.chat.username:
                chatusername = f"@{message.chat.username}"
            else:
                chatusername = "Private Group"
            try:
                query = message.text.split(None, 1)[1]
                what = "Kueri Diberikan"
            except:
                try:
                    if not message.reply_to_message:
                        what = "Perintah yang Diberikan Saja"
                    else:
                        what = "Membalas file apa pun."
                except:
                    what = "Command"
            logger_text = f"""
__**New {what}**__

**Chat:** {message.chat.title} [`{message.chat.id}`]
**User:** {message.from_user.mention}
**Username:** @{message.from_user.username}
**User ID:** `{message.from_user.id}`
**Chat Link:** {chatusername}
**Query:** {message.text}"""
            if LOG_CLIENT != "None":
                await LOG_CLIENT.send_message(
                    LOG_GROUP_ID,
                    f"{logger_text}",
                    disable_web_page_preview=True,
                )
        return await mystic(_, message)

    return wrapper
