import os
import requests
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


# Common function to handle the close button
def handle_close_button(query):
    query.message.delete()


# Movie recommendation command handler
@Client.on_message(filters.command("mrecommend"))
def movie_recommendation(_, message):
    query = message.text.strip()[15:]  # Remove '/movie_recommend' from the query
    if query:
        # Assuming query is the movie name, first we need to search for the movie to get its ID
        url = f"{TMDB_API_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                movie_id = results[0]['id']  # Get the ID of the first movie in the search results
                recommendations = get_movie_recommendations(movie_id)

                # Create a list of buttons with recommended movie names
                buttons = [
                    [
                        InlineKeyboardButton(movie['title'], callback_data=str(movie['id']))
                    ]
                    for movie in recommendations
                ]

                # Create an "Close" button
                close_button = InlineKeyboardButton("Close", callback_data="close")
                keyboard = InlineKeyboardMarkup(buttons + [[close_button]])

                if recommendations:
                    message.reply_text("Choose a movie:", reply_markup=keyboard)
                else:
                    message.reply_text("Sorry, I couldn't find any movie recommendations for that query.")
            else:
                message.reply_text("Sorry, I couldn't find any movies for that query.")
        else:
            message.reply_text("Sorry, an error occurred while fetching data.")
    else:
        message.reply_text("Please send the name of a movie along with the /movie_recommend tag to get recommendations!")


# TV series recommendation command handler
@Client.on_message(filters.command("srecommend"))
def series_recommendation(_, message):
    query = message.text.strip()[16:]  # Remove '/series_recommend' from the query
    if query:
        # Assuming query is the TV series name, first we need to search for the series to get its ID
        url = f"{TMDB_API_URL}/search/tv"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                series_id = results[0]['id']  # Get the ID of the first series in the search results
                recommendations = get_series_recommendations(series_id)

                # Create a list of buttons with recommended TV series names
                buttons = [
                    [
                        InlineKeyboardButton(series['name'], callback_data=str(series['id']))
                    ]
                    for series in recommendations
                ]

                # Create an "Close" button
                close_button = InlineKeyboardButton("Close", callback_data="close")
                keyboard = InlineKeyboardMarkup(buttons + [[close_button]])

                if recommendations:
                    message.reply_text("Choose a TV series:", reply_markup=keyboard)
                else:
                    message.reply_text("Sorry, I couldn't find any TV series recommendations for that query.")
            else:
                message.reply_text("Sorry, I couldn't find any TV series for that query.")
        else:
            message.reply_text("Sorry, an error occurred while fetching data.")
    else:
        message.reply_text("Please send the name of a TV series along with the /series_recommend tag to get recommendations!")


# Callback handler for button clicks
@Client.on_callback_query()
def button_click(_, query):
    if query.data == "close":
        handle_close_button(query)
    else:
        media_id = int(query.data)
        


