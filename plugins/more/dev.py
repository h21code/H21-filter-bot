from pyrogram import Client, filters
import asyncio

api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
app = Client("my_account", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("dev"))
async def dev_animation(client, message):
    animation_interval = 0.01
    animation_ttl = range(0, 288)
    animation_chars = [
        "M_ ____",
        "MD ____",
        "DIPES_",
        "DIPESH",
        "MD NOOR MANJEET SINGH DIPESH THESE ARE MY PERU DEV",
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await message.edit_text(animation_chars[i % 72])
