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
<b>Name :</b> <code>{name}</code>
<b>Description :</b> {description or 'N/A'}
<b>Link :</b> <a href="{url}">{url}</a>
<b>Stars :</b> {stargazers_count}"""
        else:
            result_str = "😿 No results found."

        return result_str
    except requests.exceptions.HTTPError as http_error:
        return f"<b>HTTP Error:</b> {http_error}"
    except requests.exceptions.RequestException as request_error:
        return f"<b>Request Error:</b> {request_error}"
    except KeyError:
        return "<b>Error:</b> Invalid API response."
    except Exception as error:
        return f"<b>Error:</b> {error}"

@Client.on_message(filters.command("git"))
async def reply_info(client, message):
    query = message.text.split(None, 1)[1]
    result_caption = result(query)
    await message.reply_text(
        result_caption,
        reply_markup=BUTTONS,
        quote=True,
        parse_mode="HTML"  # To render the text as HTML for bold and links
    )

    
@Client.on_callback_query(filters.regex('^close_data'))
async def close_data(client, callback_query):
    await callback_query.message.delete()

# Your bot initialization code and other parts of the script remain unchanged.
