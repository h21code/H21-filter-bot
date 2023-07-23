import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters
from info import LOG_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

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
            result_str = "😿 No results found."

        # Adding user and query information to the result
        result_str = f"👤 Requested by: {user}\n\n🔎 Query: {query}\n\n" + result_str

        # Limit the message length to avoid MessageTooLong error
        max_message_length = 4096  # Set the desired maximum length for the message
        if len(result_str) > max_message_length:
            messages = split_long_message(result_str, max_message_length)
        else:
            messages = [result_str]

        return messages
    except Exception as error:
        return ["😿 No results found."]

@Client.on_message(filters.command("ai"))
async def reply_info(client, message):
    try:
        query = message.text.split(None, 1)[1].strip()  
        if not query:
            await message.reply_text("Please provide a query along with the /ai command.")
            return

        user = message.from_user.username or message.from_user.first_name

        # Send the "Searching for: (searched query here)" message
        searching_message = await message.reply_text(f"✅ Searching for: {query}...")

        try:
            # Make the request to the API and get the JSON response
            url = API + requote_uri(query.lower())
            api_response = requests.get(url).json()

            # Send the "Generating answers for you..." message and wait for 1 second before proceeding
            await searching_message.edit_text("✅ Generating answers for you...")
            time.sleep(1)

            result_messages = result(api_response, user, query)
            for idx, result_content in enumerate(result_messages):
                # Send each part of the message as a separate message
                await message.reply_text(
                    text=result_content,
                    reply_markup=BUTTONS,
                    quote=True if idx == 0 else False  # Quote the first message only
                )
            log_message = f"--AI Chat--\n ᴜsᴇʀ : {message.from_user.mention} \n ǫᴜᴇʀʏ : {query}"
            await client.send_message(LOG_CHANNEL, log_message)

            # Delete the loading message after showing the results
            await searching_message.delete()

        except Exception as e:
            # If an error occurs, send a "No results found" message and delete the loading message
            await searching_message.delete()
            await message.reply_text("😿 No results found.")

    except IndexError:
        # If the user didn't provide a query, handle the IndexError and send an appropriate response
        await message.reply_text("Please provide a query along with the /ai command.")

    except Exception as e:
        pass


@Client.on_callback_query(filters.regex('^close_data$'))
async def close_data(client, callback_query):
    await callback_query.message.delete()
