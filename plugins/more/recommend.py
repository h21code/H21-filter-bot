import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Replace 'YOUR_API_KEY' with your TMDb API key
TMDB_API_KEY = 'b3d10dab8e82525e3a2ed8ed8bc38874'
TMDB_API_URL = f'https://api.themoviedb.org/3'




# Function to get movie and TV series recommendations from TMDb API
def get_media_recommendations(query):
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


# Movie and TV series recommendation command handler
@app.on_message(filters.command("recommend"))
def media_recommendation(_, message):
    query = message.text.strip()[10:]  # Remove '/recommend' from the query
    if query:
        # Get movie and TV series recommendations from TMDb API
        results = get_media_recommendations(query)

        # Filter only movies and TV series
        media_results = [media for media in results if media['media_type'] in ['movie', 'tv']]

        if media_results:
            # Create a list of buttons with recommended movie/series names
            buttons = [
                [
                    InlineKeyboardButton(media['title'] if media['media_type'] == 'movie' else media['name'], callback_data=str(media['id']))
                ]
                for media in media_results
            ]

            # Create an InlineKeyboardMarkup with the buttons
            keyboard = InlineKeyboardMarkup(buttons)

            message.reply_text("Choose a movie/series:", reply_markup=keyboard)
        else:
            message.reply_text("Sorry, I couldn't find any movie or TV series recommendations for that query.")
    else:
        message.reply_text("Please send the name of a movie or TV series along with the /recommend tag to get recommendations!")


# Callback handler for button clicks
@app.on_callback_query()
def button_click(_, query):
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
            response_text = f"Title: {title}\n\n{overview}"
            query.message.reply_photo(photo=poster_url, caption=response_text)
        else:
            query.message.reply_text("Sorry, couldn't fetch details for this movie/series.")
    else:
        query.message.reply_text("Sorry, an error occurred while fetching details for this movie/series.")

