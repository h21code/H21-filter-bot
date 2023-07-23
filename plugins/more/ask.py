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
        answer = response_data.get('answer', "No Answer Found.")

        return answer
    except Exception as error:
        return "😿 No Answer Found."

@Client.on_message(filters.command("ask"))
async def reply_info(client, message):
    # Check if the user provided a query
    if len(message.text.split()) <= 1:
        await message.reply_text(
            text="Please provide a query along with the /ask command.",
            quote=True
        )
        return

    query = message.text.split(None, 1)[1]
    result_content = result(query)
    await message.reply_text(
        text=result_content,
        reply_markup=BUTTONS,
        quote=True
    )

    log_message = f"--𝗔𝘀𝗸𝗲𝗱--\n ᴜsᴇʀ : {message.from_user.mention} \n ǫᴜᴇsᴛɪᴏɴ : {query}"
    await client.send_message(LOG_CHANNEL, log_message)

@Client.on_callback_query(filters.regex('^close_data'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
