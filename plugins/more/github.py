import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/github?query="

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
            name = result_data['name']
            description = result_data['description']
            url = result_data['htmlUrl']
            stargazers_count = result_data['stargazersCount']

            result_str = f"""--**📦 Repository**--
 ✒️ 𝗡𝗮𝗺𝗲 : <code>{name}</code>
 
 🧾 𝗗𝗲𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 : `{description}`
 
 🔗 𝗟𝗶𝗻𝗸 : <a href={url}>{url}</a>
 
 ⭐️ 𝗦𝘁𝗮𝗿𝘀 : {stargazers_count}"""
        else:
            result_str = "No results found."

        return result_str
    except Exception as error:
        return str(error)

@Client.on_message(filters.command("git"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    result_caption = result(query)
    await message.reply_photo(
        photo="https://telegra.ph/file/a4545775e137feda80612.jpg",
        caption=result_caption,
        reply_markup=BUTTONS,
        quote=True
    )

    
@Client.on_callback_query(filters.regex('^close_data'))
async def close_data(client, callback_query):
    await callback_query.message.delete()

# Your bot initialization code and other parts of the script remain unchanged.
