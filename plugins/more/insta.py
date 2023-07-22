from pyrogram import Client, filters
from urllib.parse import urlparse


def is_valid_instagram_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc == 'www.instagram.com' and ('/reel/' in parsed_url.path or '/p/' in parsed_url.path)

@app.on_message(filters.command("insta"))
def insta(_, update):
    if len(update.command) != 2:
        update.reply_text("You need to provide an Instagram reel or image link along with the /insta command.")
        return

    message_text = update.command[1]
    if not is_valid_instagram_url(message_text):
        update.reply_text("Invalid Instagram reel or image link. Please provide a valid link to modify.")
        return

    modified_link = message_text.replace('https://www.instagram.com/', 'https://www.ddinstagram.com/', 1)
    update.reply_text(modified_link)

