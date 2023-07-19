import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/bard?message="

BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘", callback_data='close_data')]])

def split_long_message(caption, max_length):
    messages = []
    while len(caption) > max_length:
        messages.append(caption[:max_length])
        caption = caption[max_length:]
    messages.append(caption)
    return messages

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

        # Limit the caption length to avoid MediaCaptionTooLong error
        max_caption_length = 1024  # Set the desired maximum length for the caption
        if len(result_str) > max_caption_length:
            messages = split_long_message(result_str, max_caption_length)
        else:
            messages = [result_str]

        return messages
    except Exception as error:
        return [str(error)]

@Client.on_message(filters.command("ai"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    
    # Make the request to the new API and get the JSON response
    url = API + requote_uri(query.lower())
    api_response = requests.get(url).json()
    
    # Get the user's username or first name if no username is available
    user = message.from_user.username or message.from_user.first_name
    
    result_messages = result(api_response, user, query)
    for idx, result_caption in enumerate(result_messages):
        # Send each part of the caption as a separate message
        await message.reply_photo(
            photo="https://telegra.ph/file/a4545775e137feda80612.jpg",
            caption=result_caption,
            reply_markup=BUTTONS if idx == len(result_messages) - 1 else None,
            quote=True if idx == 0 else False  # Quote the first message only
        )

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
