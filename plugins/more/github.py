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
        r.raise_for_status()  # Raise an exception for HTTP errors
        response_data = r.json()

        # Extracting information from the API response
        results = response_data['results']
        if results:
            result_data = results[0]
            name = result_data['name']
            description = result_data['description']
            url = result_data['htmlUrl']
            stargazers_count = result_data['stargazersCount']

            result_str = f"""
            
 𝗡𝗮𝗺𝗲 : <code>{name}</code>
 
 𝗗𝗲𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 : `{description}`
 
 𝗚𝗶𝘁𝗛𝘂𝗯 𝗨𝗥𝗟 : <a href={url}>{url}</a>
 
 𝗦𝘁𝗮𝗿𝘀 : {stargazers_count}"""
        else:
            result_str = "😿 No results found."

        return result_str
    except requests.exceptions.HTTPError as http_error:
        return f"HTTP Error: {http_error}"
    except requests.exceptions.RequestException as request_error:
        return f"Request Error: {request_error}"
    except KeyError:
        return "Error: Invalid API response."
    except Exception as error:
        return f"Error: {error}"

@Client.on_message(filters.command("git"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    result_caption = result(query)
    await message.reply_text(
        result_caption,
        reply_markup=BUTTONS,
        quote=True
    )



@Client.on_callback_query(filters.regex('^close_data'))
async def close_data(client, callback_query):
    await callback_query.message.delete()

# Your bot initialization code and other parts of the script remain unchanged.
