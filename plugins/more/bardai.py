import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

API = "https://api.safone.me/bard?message="
MAX_MESSAGE_LENGTH = 4096  # Telegram message length limit
BUTTONS_PER_PAGE = 2  # Number of pagination buttons per page

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
            photo="https://example.com/your_16_9_ratio_photo.jpg",  # Replace with your 16:9 ratio photo URL
            caption=messages[0],
            quote=True
        )

async def send_paginated_message(message, messages):
    current_page = 0
    max_page = len(messages) - 1
    buttons = None
    
    while True:
        if buttons is None:
            buttons = InlineKeyboardMarkup()
        else:
            buttons.inline_keyboard.clear()
        
        if current_page > 0:
            buttons.row(InlineKeyboardButton("Previous Page", callback_data='prev_page'))
        if current_page < max_page:
            buttons.row(InlineKeyboardButton("Next Page", callback_data='next_page'))
        
        # Add the close button to the last row
        buttons.row(BUTTONS.inline_keyboard[0])
        
        start_idx = current_page * BUTTONS_PER_PAGE
        end_idx = min((current_page + 1) * BUTTONS_PER_PAGE, len(messages))
        
        caption = "\n\n".join(messages[start_idx:end_idx])
        
        if current_page == 0:
            # Edit the original message
            await message.edit_caption(
                caption=caption,
                reply_markup=buttons
            )
        else:
            # Edit the existing message with the new content
            await message.reply_text(
                text=caption,
                reply_markup=buttons,
                quote=True
            )
        
        if current_page == max_page:
            break
        
        current_page += 1

@Client.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data
    original_message = callback_query.message

    if data == 'next_page':
        # Increment the page index and update the message
        await update_paginated_message(original_message, 1)
    elif data == 'prev_page':
        # Decrement the page index and update the message
        await update_paginated_message(original_message, -1)

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()

async def update_paginated_message(original_message, page_change):
    # Get the current page index from the caption
    current_page = int(original_message.caption.split('Page: ')[1].split('\n\n', 1)[0])
    new_page = current_page + page_change

    if new_page >= 0:
        # Make the request to the new API and get the JSON response
        query = original_message.caption.split('\n\n', 2)[1][9:]
        url = API + requote_uri(query.lower())
        api_response = requests.get(url).json()
        
        # Get the user's username or first name if no username is available
        user = original_message.from_user.username or original_message.from_user.first_name

        # Get the full result caption
        result_caption = result(api_response, user, query)

        # Split the caption into pages
        messages = split_long_message(result_caption, MAX_MESSAGE_LENGTH)

        # Get the target page index
        target_page_idx = None
        if new_page >= 0 and new_page < len(messages):
            target_page_idx = new_page

        # Find the target page and send it as a new message
        if target_page_idx is not None and target_page_idx >= 0 and target_page_idx < len(messages):
            target_message_text = messages[target_page_idx]
            await original_message.edit_caption(
                caption=f"Page: {target_page_idx + 1}\n\n{target_message_text}"
            )

app = Client("my_bot")
app.run()
