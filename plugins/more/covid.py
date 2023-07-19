import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from info import LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/google?query="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘", callback_data='close_data')]])

def result(query):
    try:
        url = API + requote_uri(query.lower()) + "&limit=1"
        r = requests.get(url)
        response_data = r.json()

        # Extracting information from the API response
        results = response_data['results']
        if results:
            result_data = results[0]
            title = result_data['title']
            description = result_data['description']
            link = result_data['link']

            result_str = f"""--**🔍 Search Result**--
 𝗧𝗶𝘁𝗹𝗲 : `</b>{title}<\b>`
 𝗗𝗲𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 : `{description}`
 𝗟𝗶𝗻𝗸 : <a href='{link}'>{link}<\a>"""
        else:
            result_str = "No results found."

        return result_str
    except Exception as error:
        return str(error)

@Client.on_message(filters.command("search"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    result_caption = result(query)
    await message.reply_photo(
        photo="https://telegra.ph/file/a4545775e137feda80612.jpg",
        caption=result_caption,
        reply_markup=BUTTONS,
        quote=True
    )

    log_message = f"𝗦𝗲𝗮𝗿𝗰𝗵 : User {message.from_user.mention} searched: {query}"
    await client.send_message(LOG_CHANNEL, log_message)

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
