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
        info = r.json()
        title = info['title']
        description = info['description']
        link = info['link']
        result = f"""--**Search Result**--
᚛› Title : `{title}`
᚛› Description : `{description}`
᚛› Link : `{link}`"""
        return result
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
