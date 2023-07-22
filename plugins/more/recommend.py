import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# Replace 'YOUR_API_KEY' with your TMDb API key
TMDB_API_KEY = 'b3d10dab8e82525e3a2ed8ed8bc38874'
TMDB_API_URL = f'https://api.themoviedb.org/3'


# Function to search for movies or TV series using the TMDb API
def search_media(query):
    url = f"{TMDB_API_URL}/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    return []


# Function to get movie and TV series recommendations from TMDb API
def get_media_recommendations(media_id, media_type):
    url = f"{TMDB_API_URL}/{media_type}/{media_id}/recommendations"
    params = {
        "api_key": TMDB_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    return []


# Movie and TV series recommendation command handler
@Client.on_message(filters.command("recommend"))
@Client.on_message(filters.command("recommend"))
def media_recommendation(client, message):
    query = message.text.strip()[11:]  # Remove '/recommend' from the query
    if query:
        # Check if the query is a numeric media ID
        if query.isdigit():
            # Fetch recommendations directly with the provided media ID
            media_id = int(query)
            media_type = 'movie' if media_id < 200000 else 'tv'  # Assume media IDs < 200000 are for movies, otherwise TV series
            recommendations = get_media_recommendations(media_id, media_type)

            if recommendations:
                # Create a list of buttons with recommended movie/series names
                buttons = [
                    [
                        InlineKeyboardButton(
                            rec['title'] if rec['media_type'] == 'movie' else rec['name'],
                            callback_data=str(rec['id'])  # Correctly set the callback_data to the media ID as a string
                        )
                    ]
                    for rec in recommendations
                ]

                # Add a "Close" button to the list of buttons
                buttons.append([InlineKeyboardButton("Close", callback_data="close")])

                # Create an InlineKeyboardMarkup with the buttons
                keyboard = InlineKeyboardMarkup(buttons)

                message.reply_text("Choose a movie/series:", reply_markup=keyboard)
            else:
                message.reply_text("Sorry, I couldn't find any recommendations for that movie or TV series.")
        else:
            # Search for movies and TV series
            media_results = search_media(query)

            if media_results:
                # Filter only movies and TV series
                media_results = [media for media in media_results if media['media_type'] in ['movie', 'tv']]

                if media_results:
                    # Get the first media from the search results
                    media = media_results[0]
                    media_id = media['id']
                    media_type = media['media_type']

                    # Get movie and TV series recommendations from TMDb API
                    recommendations = get_media_recommendations(media_id, media_type)

                    if recommendations:
                        # Create a list of buttons with recommended movie/series names
                        buttons = [
                            [
                                InlineKeyboardButton(
                                    rec['title'] if rec['media_type'] == 'movie' else rec['name'],
                                    callback_data=str(rec['id'])  # Correctly set the callback_data to the media ID as a string
                                )
                            ]
                            for rec in recommendations
                        ]

                        # Add a "Close" button to the list of buttons
                        buttons.append([InlineKeyboardButton("Close", callback_data="close")])

                        # Create an InlineKeyboardMarkup with the buttons
                        keyboard = InlineKeyboardMarkup(buttons)

                        message.reply_text("Choose a movie/series:", reply_markup=keyboard)
                    else:
                        message.reply_text("Sorry, I couldn't find any recommendations for that movie or TV series.")
        else:
            # Search for movies and TV series
            media_results = search_media(query)

            if media_results:
                # Filter only movies and TV series
                media_results = [media for media in media_results if media['media_type'] in ['movie', 'tv']]

                if media_results:
                    # Get the first media from the search results
                    media = media_results[0]
                    media_id = media['id']
                    media_type = media['media_type']

                    # Get movie and TV series recommendations from TMDb API
                    recommendations = get_media_recommendations(media_id, media_type)

                    if recommendations:
                        # Create a list of buttons with recommended movie/series names
                        buttons = [
                            [
                                InlineKeyboardButton(
                                    rec['title'] if rec['media_type'] == 'movie' else rec['name'],
                                    callback_data=str(rec['id'])  # Correctly set the callback_data to the media ID as a string
                                )
                            ]
                            for rec in recommendations
                        ]

                        # Add a "Close" button to the list of buttons
                        buttons.append([InlineKeyboardButton("Close", callback_data="close")])

                        # Create an InlineKeyboardMarkup with the buttons
                        keyboard = InlineKeyboardMarkup(buttons)

                        message.reply_text("Choose a movie/series:", reply_markup=keyboard)
                    else:
                        message.reply_text("Sorry, I couldn't find any recommendations for that movie or TV series.")
                else:
                    message.reply_text("Sorry, I couldn't find any movie or TV series with that name.")
            else:
                message.reply_text("Sorry, I couldn't find any movie or TV series with that name.")
    else:
        message.reply_text("Please send the name of a movie or TV series along with the /recommend tag to get recommendations!")


# Callback handler for button clicks
@Client.on_callback_query()
def button_click(_, query):
    if query.data == "close":
        query.message.delete()
    else:
        media_id = int(query.data)  # Convert the correct media ID from string to integer
        url = f"{TMDB_API_URL}/movie/{media_id}"
        params = {
            "api_key": TMDB_API_KEY,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            title = data.get('title')
            overview = data.get('overview')
            poster_path = data.get('poster_path')

            if title and overview and poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

                try:
                    # Try to send the photo and caption as a document message to trigger auto-delete timer
                    query.message.reply_document(document=poster_url, caption=f"Title: {title}\n\n{overview}")
                except Exception as e:
                    # If there's an error sending the document, reply with the caption only
                    query.message.reply_text(f"Title: {title}\n\n{overview}")

                # Sleep for 2 minutes (Telegram auto-deletes the document after 2 minutes)
                time.sleep(120)

                # Delete the message to clean up the recommendation
                query.message.delete()
            else:
                query.message.reply_text("Sorry, couldn't fetch details for this movie/series.")
        else:
            query.message.reply_text("Sorry, an error occurred while fetching details for this movie/series.")

# ... (Rest of the code remains the same)
