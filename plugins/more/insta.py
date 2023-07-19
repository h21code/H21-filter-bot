import os
import requests
import instaloader
from pyrogram import Client, filters

DOWNLOAD_FOLDER = 'downloads/'  # Make sure the 'downloads' folder exists

def download_instagram_video(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            video_url = response.json().get('data', {}).get('shortcode_media', {}).get('video_url')
            if video_url:
                video_response = requests.get(video_url)
                if video_response.status_code == 200:
                    return video_response.content
    except Exception as e:
        print("Error while downloading the video:", e)
    return None

@Client.on_message(filters.command("insta", prefixes="/") & filters.regex(r'https?://(?:www\.)?instagram\.com/.*'))
async def reply_with_instagram_video(client, message):
    url = message.text.split(None, 1)[1]
    video_data = download_instagram_video(url)

    if video_data:
        video_file_path = os.path.join(DOWNLOAD_FOLDER, "instagram_video.mp4")
        with open(video_file_path, "wb") as video_file:
            video_file.write(video_data)
        
        await message.reply_video(video=video_file_path, quote=True)
        await message.reply_text("Video downloaded successfully!")

    else:
        await message.reply_text("Error while downloading the video.")

@Client.on_message(filters.command("insta1", prefixes="/"))
async def start_command(client, message):
    await message.reply_text("Send an Instagram post URL after /insta command to download the video.")


