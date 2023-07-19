import os
import requests
from pyrogram import Client, filters
from info import LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/asq?query="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘", callback_data='close_data')]])

def result(query):
    try:
        url = API + query.lower()
        r = requests.get(url)
        response_data = r.json()

        # Extracting information from the JSON response
        answer = response_data.get('answer', "No results found.")

        return answer
    except Exception as error:
        return str(error)

@Client.on_message(filters.command("ask"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    result_content = result(query)
    await message.reply_text(
        text=result_content,
        reply_markup=BUTTONS,
        quote=True
    )

    log_message = f"--𝗦𝗲𝗮𝗿𝗰𝗵--\n ᴜsᴇʀ : {message.from_user.mention} \n ǫᴜᴇʀʏ : {query}"
    await client.send_message(LOG_CHANNEL, log_message)

@Client.on_callback_query(filters.regex('^close_data'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
