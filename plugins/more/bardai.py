import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/bard?message="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘", callback_data='close_data')]])

def result(api_response, user, query):
    try:
        response_data = api_response['choices']
        if response_data:
            content = response_data[0]['content']
            result_str = "\n".join(content)
        else:
            result_str = "No results found."

        # Adding user and query information to the result
        result_str = f"👤 Requested by: {user}\n\n🔎 Query: {query}\n\n" + result_str

        return result_str
    except Exception as error:
        return str(error)

@Client.on_message(filters.command("ai"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    
    # Make the request to the new API and get the JSON response
    url = API + requote_uri(query.lower())
    api_response = requests.get(url).json()
    
    # Get the user's username or first name if no username is available
    user = message.from_user.username or message.from_user.first_name
    
    result_caption = result(api_response, user, query)
    await message.reply_photo(
        photo="https://telegra.ph/file/a4545775e137feda80612.jpg",
        caption=result_caption,
        reply_markup=BUTTONS,
        quote=True
    )

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
