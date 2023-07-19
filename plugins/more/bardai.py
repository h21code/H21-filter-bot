import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API = "https://api.safone.me/bard?message="
MAX_MESSAGE_LENGTH = 4096  # Telegram message length limit

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
    messages = split_long_message(result_caption, MAX_MESSAGE_LENGTH)
    
    if len(messages) > 1:
        await send_paginated_message(message, messages)
    else:
        await message.reply_photo(
            photo="https://telegra.ph/file/988ba355dd1e700a87e8b.jpg",  # Replace with your 16:9 ratio photo URL
            caption=messages[0],
            reply_markup=BUTTONS,
            quote=True
        )

async def send_paginated_message(message, messages):
    current_page = 0
    max_page = len(messages) - 1
    
    await message.reply_photo(
        photo="https://example.com/your_16_9_ratio_photo.jpg",  # Replace with your 16:9 ratio photo URL
        caption=messages[current_page],
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Previous Page", callback_data=f'prev_page'),
                    InlineKeyboardButton("Next Page", callback_data=f'next_page')
                ],
                [BUTTONS.inline_keyboard[0]]  # Close button
            ]
        ),
        quote=True
    )

@Client.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data
    original_message = callback_query.message

    if data == 'next_page' or data == 'prev_page':
        # Get the current page index from the caption
        current_page = int(original_message.caption.split('\n\n', 1)[0].split(': ')[1])
        new_page = current_page + 1 if data == 'next_page' else current_page - 1

        if 0 <= new_page < len(messages):
            # Update the caption with the new page content
            await original_message.edit_caption(
                caption=messages[new_page],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Previous Page", callback_data=f'prev_page'),
                            InlineKeyboardButton("Next Page", callback_data=f'next_page')
                        ],
                        [BUTTONS.inline_keyboard[0]]  # Close button
                    ]
                )
            )

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
