import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/google?query="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("𝙲𝙻𝙾𝚂𝙴", callback_data='close_data')]])

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

            result_str = f"""--**Search Result**--
᚛› Title : `{title}`
᚛› Description : `{description}`
᚛› Link : `{link}`"""
        else:
            result_str = "No results found."

        return result_str
    except Exception as error:
        return str(error)

@Client.on_message(filters.command("search"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    await message.reply_photo(
        photo="https://telegra.ph/file/51fdcccb41510ff8af8b1.jpg",
        caption=result(query),
        quote=True
    )
