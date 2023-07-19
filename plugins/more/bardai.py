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
    
    for idx, message_text in enumerate(messages):
        if idx == 0:
            # Send the first message with the 16:9 ratio photo
            photo_url = "https://telegra.ph/file/988ba355dd1e700a87e8b.jpg"  # Replace with your 16:9 ratio photo URL
            await message.reply_photo(
                photo=photo_url,
                caption=message_text,
                reply_markup=BUTTONS if idx == len(messages) - 1 else None,
                quote=True if idx == 0 else False
            )
        else:
            # Send subsequent messages as text messages
            await message.reply_text(
                text=message_text,
                reply_markup=BUTTONS if idx == len(messages) - 1 else None,
                quote=False
            )

@Client.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data.split('_')
    page_action = data[0]
    page_idx = int(data[1])

    # Fetch the original message
    original_message = callback_query.message

    # Delete the current (button-triggering) message
    await callback_query.message.delete()

    # Get the user's username or first name if no username is available
    user = callback_query.from_user.username or callback_query.from_user.first_name

    # Get the original query from the message caption
    query = original_message.caption.split('\n\n', 2)[1][9:]

    # Make the request to the new API and get the JSON response
    url = API + requote_uri(query.lower())
    api_response = requests.get(url).json()
    
    # Get the full result caption
    result_caption = result(api_response, user, query)

    # Split the caption into pages
    messages = split_long_message(result_caption, MAX_MESSAGE_LENGTH)
    
    # Get the target page index
    target_page_idx = None
    if page_action == 'next_page':
        target_page_idx = page_idx
    elif page_action == 'prev_page':
        target_page_idx = page_idx
    
    # Find the target page and send it as a new message
    if target_page_idx is not None and target_page_idx >= 0 and target_page_idx < len(messages):
        target_message_text = messages[target_page_idx]
        buttons = InlineKeyboardMarkup()
        if len(messages) > 1:
            if target_page_idx == 0:
                buttons.row(InlineKeyboardButton("Next Page", callback_data=f'next_page_{target_page_idx + 1}'))
            elif target_page_idx == len(messages) - 1:
                buttons.row(InlineKeyboardButton("Previous Page", callback_data=f'prev_page_{target_page_idx - 1}'))
            else:
                buttons.row(
                    InlineKeyboardButton("Previous Page", callback_data=f'prev_page_{target_page_idx - 1}'),
                    InlineKeyboardButton("Next Page", callback_data=f'next_page_{target_page_idx + 1}')
                )
        else:
            buttons = BUTTONS

        await original_message.reply_text(
            text=target_message_text,
            reply_markup=buttons,
            quote=True
        )

@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
