import os
import requests
from pyrogram import Client, filters
import asyncio


@Client.on_message(filters.command("dev"))
async def dev_animation(client, message):
    animation_interval = 0.01
    animation_ttl = range(0, 288)
    animation_chars = [
        "M_ ____",
        "MA ____",
        "MALLU ___",
        "MALLUFILES",
        "MD NOOR MANJEET SINGH DIPESH THESE ARE MY PERU DEV",
    ]

    sent_message = await message.reply_text(animation_chars[0])
    for char in animation_chars[1:]:
        await sent_message.edit_text(char)
        await asyncio.sleep(animation_interval)
