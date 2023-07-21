import os
import requests
from requests.utils import requote_uri
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace 'YOUR_API_KEY' with your TMDb API key
TMDB_API_KEY = 'b3d10dab8e82525e3a2ed8ed8bc38874'
TMDB_API_URL = f'https://api.themoviedb.org/3'


# Function to get movie recommendations from TMDb API
def get_movie_recommendations(movie_id):
    url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations"
    params = {
        "api_key": TMDB_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    return []


# Function to get TV series recommendations from TMDb API
def get_series_recommendations(series_id):
    url = f"{TMDB_API_URL}/tv/{series_id}/recommendations"
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
def media_recommendation(_, message):
    query = message.text.strip()[10:]  # Remove '/recommend' from the query
    if query:
        # Get movie recommendations from TMDb API
        movie_results = get_movie_recommendations(query)

        # Get TV series recommendations from TMDb API
        series_results = get_series_recommendations(query)

        # Combine movie and TV series recommendations
        media_results = movie_results + series_results

        if media_results:
            # Create a list of buttons with recommended movie/series names
            buttons = [
                [
                    InlineKeyboardButton(media['title'] if 'title' in media else media['name'], callback_data=str(media['id']))
                ]
                for media in media_results
            ]

            # Add a "Close" button to the list of buttons
            buttons.append([InlineKeyboardButton("Close", callback_data="close")])

            # Create an InlineKeyboardMarkup with the buttons
            keyboard = InlineKeyboardMarkup(buttons)

            message.reply_text("Choose a movie/series:", reply_markup=keyboard)
        else:
            message.reply_text("Sorry, I couldn't find any movie or TV series recommendations for that query.")
    else:
        message.reply_text("Please send the name of a movie or TV series along with the /recommend tag to get recommendations!")


@Client.on_callback_query()
def button_click(_, query):
    if query.data == "close":
        query.message.delete()
    else:
        media_id = int(query.data)
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
                    # Try to send the photo and caption
                    query.message.reply_photo(photo=poster_url, caption=f"Title: {title}\n\n{overview}")
                except Exception as e:
                    # If there's an error sending the photo, reply with the caption only
                    query.message.reply_text(f"Title: {title}\n\n{overview}")
            else:
                query.message.reply_text("Sorry, couldn't fetch details for this movie/series.")
        else:
            query.message.reply_text("Sorry, an error occurred while fetching details for this movie/series.")

# ... (Rest of the code remains the same)
