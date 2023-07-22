# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
lock = asyncio.Lock()

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
 make_inactive
from info import LANGUAGES, ADMINS, AUTH_CHANNEL, AUTH_USERS, SUPPORT_CHAT_ID, CUSTOM_FILE_CAPTION, MSG_ALRT, PICS, AUTH_GROUPS, NOR_IMG, P_TTI_SHOW_OFF, GRP_LNK, CHNL_LNK, LOG_CHANNEL, MAX_B_TN, IMDB, \
 SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, NO_RESULTS_MSG, VERIFY, REQ_CHANNEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, send_all, check_verification, get_token
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
 del_all,
 find_filter,
 get_filters,
)
from database.gfilters_mdb import (
 find_gfilter,
 get_gfilters,
 del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group | filters.private & filters.text & filters.incoming)
async def give_filter(client, message):
 if message.chat.id != SUPPORT_CHAT_ID:
 glob = await global_filters(client, message)
 if glob == False:
 manual = await manual_filters(client, message)
 if manual == False:
 settings = await get_settings(message.chat.id)
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message) 
 
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
 content = message.text
 user = message.from_user.first_name
 user_id = message.from_user.id
 if content.startswith("/") or content.startswith("#"): return # ignore commands and hashtags
 if user_id in ADMINS: return # ignore admins
 await message.reply_text(
 text="<b>hey dude 😍 ,\n\nyou can't get movies from here. reouest on our <a href=https://t.me/filmy_fundas>movie group</a> or click reouest here button below​👇</b>", 
 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 reouest here​ ", url=f"t.me/Funda_More")]]))
 await bot.send_message(
 chat_id=LOG_CHANNEL,
 text=f"<b>👻 PM_MSG 👻\n\n📝message​:-{content}\n\n👶🏻reQueꜱted by:-{user}\n\n🃏uꜱer id:-{user_id}</b>"
 )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
 ident, req, key, offset = query.data.split("_")
 if int(req) not in [query.from_user.id, 0]:
 return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
 try:
 offset = int(offset)
 except:
 offset = 0
 search = BUTTONS.get(key)
 if not search:
 await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
 return

 files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
 try:
 n_offset = int(n_offset)
 except:
 n_offset = 0

 if not files:
 return
 settings = await get_settings(query.message.chat.id)
 temp.SEND_ALL_TEMP[query.from_user.id] = files
 if 'is_shortlink' in settings.keys():
 ENABLE_SHORTLINK = settings['is_shortlink']
 else:
 await save_group_settings(query.message.chat.id, 'is_shortlink', False)
 ENABLE_SHORTLINK = False
 if ENABLE_SHORTLINK == True:
 if settings['button']:
 btn = [
 [
 InlineKeyboardButton(
 text=f"📁 {get_size(file.file_size)} ⊳ {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 ]
 for file in files
 ]
 else:
 btn = [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 ]
 for file in files
 ]
 else:
 if settings['button']:
 btn = [
 [
 InlineKeyboardButton(
 text=f"📁 {get_size(file.file_size)} ⊳ {file.file_name}", callback_data=f'files#{file.file_id}'
 ),
 ]
 for file in files
 ]
 else:
 btn = [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 callback_data=f'files_#{file.file_id}',
 ),
 ]
 for file in files
 ]
 try:
 if settings['auto_delete']:
 btn.insert(0, 
 [
 InlineKeyboardButton("Send All​ !", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("Languages​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )

 else:
 btn.insert(0, 
 [
 InlineKeyboardButton("Send All!", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("Languages​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )
 
 except KeyError:
 grpid = await active_connection(str(query.message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(query.message.chat.id)
 if settings['auto_delete']:
 btn.insert(0, 
 [
 InlineKeyboardButton("send all​ !", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("languages​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )

 else:
 btn.insert(0, 
 [
 InlineKeyboardButton("send all​ !", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("languages​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )
 try:
 settings = await get_settings(query.message.chat.id)
 if settings['max_btn']:
 if 0 < offset <= 10:
 off_set = 0
 elif offset == 0:
 off_set = None
 else:
 off_set = offset - 10
 if n_offset == 0:
 btn.append(
 [InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
 )
 elif off_set is None:
 btn.append([InlineKeyboardButton("📚 page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("next ​⌦", callback_data=f"next_{req}_{key}_{n_offset}")])
 else:
 btn.append(
 [
 InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"),
 InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
 InlineKeyboardButton("next ​⌦", callback_data=f"next_{req}_{key}_{n_offset}")
 ],
 )
 else:
 if 0 < offset <= int(MAX_B_TN):
 off_set = 0
 elif offset == 0:
 off_set = None
 else:
 off_set = offset - int(MAX_B_TN)
 if n_offset == 0:
 btn.append(
 [InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
 )
 elif off_set is None:
 btn.append([InlineKeyboardButton("📚 page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("next ​⌦", callback_data=f"next_{req}_{key}_{n_offset}")])
 else:
 btn.append(
 [
 InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"),
 InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
 InlineKeyboardButton("next​ ⌦", callback_data=f"next_{req}_{key}_{n_offset}")
 ],
 )
 except KeyError:
 await save_group_settings(query.message.chat.id, 'max_btn', False)
 settings = await get_settings(query.message.chat.id)
 if settings['max_btn']:
 if 0 < offset <= 10:
 off_set = 0
 elif offset == 0:
 off_set = None
 else:
 off_set = offset - 10
 if n_offset == 0:
 btn.append(
 [InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
 )
 elif off_set is None:
 btn.append([InlineKeyboardButton("📚 page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("next ​⌦", callback_data=f"next_{req}_{key}_{n_offset}")])
 else:
 btn.append(
 [
 InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"),
 InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
 InlineKeyboardButton("next ⌦", callback_data=f"next_{req}_{key}_{n_offset}")
 ],
 )
 else:
 if 0 < offset <= int(MAX_B_TN):
 off_set = 0
 elif offset == 0:
 off_set = None
 else:
 off_set = offset - int(MAX_B_TN)
 if n_offset == 0:
 btn.append(
 [InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
 )
 elif off_set is None:
 btn.append([InlineKeyboardButton("📚 page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("next ​⌦", callback_data=f"next_{req}_{key}_{n_offset}")])
 else:
 btn.append(
 [
 InlineKeyboardButton("⌫ back​", callback_data=f"next_{req}_{key}_{off_set}"),
 InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
 InlineKeyboardButton("next​ ⌦", callback_data=f"next_{req}_{key}_{n_offset}")
 ],
 )
 btn.insert(0, [
 InlineKeyboardButton('how to download', url=f'https://t.me/+W5plh7_tP19lZjg1')
 ])
 try:
 await query.edit_message_reply_markup(
 reply_markup=InlineKeyboardMarkup(btn)
 )
 except MessageNotModified:
 pass
 await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
 _, user, movie_ = query.data.split('#')
 movies = SPELL_CHECK.get(query.message.reply_to_message.id)
 if not movies:
 return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
 if int(user) != 0 and query.from_user.id != int(user):
 return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
 if movie_ == "close_spellcheck":
 return await query.message.delete()
 movie = movies[(int(movie_))]
 await query.answer(script.TOP_ALRT_MSG)
 gl = await global_filters(bot, query.message, text=movie)
 if gl == False:
 k = await manual_filters(bot, query.message, text=movie)
 if k == False:
 files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
 if files:
 k = (movie, files, offset, total_results)
 await auto_filter(bot, query, k)
 else:
 reqstr1 = query.from_user.id if query.from_user else 0
 reqstr = await bot.get_users(reqstr1)
 if NO_RESULTS_MSG:
 await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
 k = await query.message.edit(script.MVE_NT_FND)
 await asyncio.sleep(10)
 await k.delete()
 
 #Language Code Temp 
 
 
@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
 if query.message.reply_to_message and int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
 return await query.answer(
 f"⚠️ hello{query.from_user.first_name},\nthiꜱ iꜱ not your movie reQueꜱt,\nreQueꜱt your'ꜱ...",
 show_alert=True,
 )
 
 _, search, key = query.data.split("#")

 btn = [
 [
 InlineKeyboardButton(
 text=lang.title(),
 callback_data=f"fl#{lang.lower()}#{search}#{key}"
 ),
 ]
 for lang in LANGUAGES
 ]

 btn.insert(
 0,
 [
 InlineKeyboardButton(
 text="☟ ꜱelect your languageꜱ ☟", callback_data="selectlang"
 )
 ],
 )
 req = query.from_user.id
 offset = 0
 btn.append([InlineKeyboardButton(text="↺ back to files ​↻", callback_data=f"next_{req}_{key}_{offset}")])

 await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
 _, lang, search, key = query.data.split("#")

 search = search.replace("_", " ")
 req = query.from_user.id
 chat_id = query.message.chat.id
 message = query.message
 if query.message.reply_to_message and int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
 return await query.answer(
 f"⚠️ hello{query.from_user.first_name},\nthiꜱ iꜱ not your movie reQueꜱt,\nreQueꜱt your'ꜱ...",
 show_alert=True,
 )

 search = f"{search} {lang}" 
 
 files, offset, total_results = await get_search_results(message.chat.id ,search.lower(), offset=0, filter=True)
 files = [file for file in files if re.search(lang, file.file_name, re.IGNORECASE)]
 if not files:
 await query.answer("🚫 No File Were Found 🚫", show_alert=1)
 return

 settings = await get_settings(message.chat.id)
 if 'is_shortlink' in settings.keys():
 ENABLE_SHORTLINK = settings['is_shortlink']
 else:
 await save_group_settings(message.chat.id, 'is_shortlink', False)
 ENABLE_SHORTLINK = False
 pre = 'filep' if settings['file_secure'] else 'file'
 if ENABLE_SHORTLINK == True:
 btn = (
 [
 [
 InlineKeyboardButton(
 text=f"▫️ {get_size(file.file_size)} ⊳ {file.file_name}",
 url=await get_shortlink(
 message.chat.id,
 f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
 ),
 ),
 ]
 for file in files
 ]
 if settings["button"]
 else [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}",
 url=await get_shortlink(
 message.chat.id,
 f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
 ),
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 url=await get_shortlink(
 message.chat.id,
 f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
 ),
 ),
 ]
 for file in files
 ]
 )
 elif settings["button"]:
 btn = [
 [
 InlineKeyboardButton(
 text=f"▫️ {get_size(file.file_size)} ⊳ {file.file_name}", callback_data=f'{pre}#{file.file_id}'
 ),
 ]
 for file in files
 ]
 else:
 btn = [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}",
 callback_data=f'{pre}#{file.file_id}',
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 callback_data=f'{pre}#{file.file_id}',
 ),
 ]
 for file in files
 ]
 try:
 if settings['auto_delete']:
 btn.insert(
 0,
 [
 InlineKeyboardButton(f'info', 'reqinfo'),
 InlineKeyboardButton(f'movie', 'minfo'),
 InlineKeyboardButton(f'ꜱerieꜱ', 'sinfo'),
 ],
 )

 else:
 btn.insert(
 0,
 [
 InlineKeyboardButton(f'info', 'reqinfo'),
 InlineKeyboardButton(f'movie', 'minfo'),
 InlineKeyboardButton(f'ꜱerieꜱ', 'sinfo'),
 ],
 )

 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 btn.insert(
 0,
 [
 InlineKeyboardButton(f'info', 'reqinfo'),
 InlineKeyboardButton(f'movie', 'minfo'),
 InlineKeyboardButton(f'ꜱerieꜱ', 'sinfo'),
 ],
 )

 else:
 btn.insert(
 0,
 [
 InlineKeyboardButton(f'info', 'reqinfo'),
 InlineKeyboardButton(f'movie', 'minfo'),
 InlineKeyboardButton(f'ꜱerieꜱ', 'sinfo'),
 ],
 )

 btn.insert(0, [
 InlineKeyboardButton("📮 SEND ALL FILES TO PM ", callback_data=f"send_fall#files#{offset}")
 ])
 if offset != "":
 key = f"{message.chat.id}-{message.id}"
 BUTTONS[key] = search
 try:
 settings = await get_settings(message.chat.id)
 if settings['max_btn']:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 except KeyError:
 await save_group_settings(message.chat.id, 'max_btn', False)
 settings = await get_settings(message.chat.id)
 if settings['max_btn']:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="NEXT ​⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton(text="♨️ NO MORE PAGES AVAILABLE ♨️",callback_data="pages")]
 )



 await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))




@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
 if query.data == "close_data":
 await query.message.delete()
 elif query.data == "gfiltersdeleteallconfirm":
 await del_allg(query.message, 'gfilters')
 await query.answer("Done !")
 return
 elif query.data == "gfiltersdeleteallcancel": 
 await query.message.reply_to_message.delete()
 await query.message.delete()
 await query.answer("Process Cancelled !")
 return
 elif query.data == "delallconfirm":
 userid = query.from_user.id
 chat_type = query.message.chat.type

 if chat_type == enums.ChatType.PRIVATE:
 grpid = await active_connection(str(userid))
 if grpid is not None:
 grp_id = grpid
 try:
 chat = await client.get_chat(grpid)
 title = chat.title
 except:
 await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
 return await query.answer(MSG_ALRT)
 else:
 await query.message.edit_text(
 "I'm not connected to any groups!\nCheck /connections or connect to any groups",
 quote=True
 )
 return await query.answer(MSG_ALRT)

 elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
 grp_id = query.message.chat.id
 title = query.message.chat.title

 else:
 return await query.answer(MSG_ALRT)

 st = await client.get_chat_member(grp_id, userid)
 if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
 await del_all(query.message, grp_id, title)
 else:
 await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
 elif query.data == "delallcancel":
 userid = query.from_user.id
 chat_type = query.message.chat.type

 if chat_type == enums.ChatType.PRIVATE:
 await query.message.reply_to_message.delete()
 await query.message.delete()

 elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
 grp_id = query.message.chat.id
 st = await client.get_chat_member(grp_id, userid)
 if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
 await query.message.delete()
 try:
 await query.message.reply_to_message.delete()
 except:
 pass
 else:
 await query.answer("That's not for you!!", show_alert=True)
 elif "groupcb" in query.data:
 await query.answer()

 group_id = query.data.split(":")[1]

 act = query.data.split(":")[2]
 hr = await client.get_chat(int(group_id))
 title = hr.title
 user_id = query.from_user.id

 if act == "":
 stat = "CONNECT"
 cb = "connectcb"
 else:
 stat = "DISCONNECT"
 cb = "disconnect"

 keyboard = InlineKeyboardMarkup([
 [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
 InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
 [InlineKeyboardButton("BACK", callback_data="backcb")]
 ])

 await query.message.edit_text(
 f"Group Name : **{title}**\nGroup ID : `{group_id}`",
 reply_markup=keyboard,
 parse_mode=enums.ParseMode.MARKDOWN
 )
 return await query.answer(MSG_ALRT)
 elif "connectcb" in query.data:
 await query.answer()

 group_id = query.data.split(":")[1]

 hr = await client.get_chat(int(group_id))

 title = hr.title

 user_id = query.from_user.id

 mkact = await make_active(str(user_id), str(group_id))

 if mkact:
 await query.message.edit_text(
 f"Connected to **{title}**",
 parse_mode=enums.ParseMode.MARKDOWN
 )
 else:
 await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
 return await query.answer(MSG_ALRT)
 elif "disconnect" in query.data:
 await query.answer()

 group_id = query.data.split(":")[1]

 hr = await client.get_chat(int(group_id))

 title = hr.title
 user_id = query.from_user.id

 mkinact = await make_inactive(str(user_id))

 if mkinact:
 await query.message.edit_text(
 f"Disconnected from **{title}**",
 parse_mode=enums.ParseMode.MARKDOWN
 )
 else:
 await query.message.edit_text(
 f"Some error occurred!!",
 parse_mode=enums.ParseMode.MARKDOWN
 )
 return await query.answer(MSG_ALRT)
 elif "deletecb" in query.data:
 await query.answer()

 user_id = query.from_user.id
 group_id = query.data.split(":")[1]

 delcon = await delete_connection(str(user_id), str(group_id))

 if delcon:
 await query.message.edit_text(
 "Successfully deleted connection !"
 )
 else:
 await query.message.edit_text(
 f"Some error occurred!!",
 parse_mode=enums.ParseMode.MARKDOWN
 )
 return await query.answer(MSG_ALRT)
 elif query.data == "backcb":
 await query.answer()

 userid = query.from_user.id

 groupids = await all_connections(str(userid))
 if groupids is None:
 await query.message.edit_text(
 "There are no active connections!! Connect to some groups first.",
 )
 return await query.answer(MSG_ALRT)
 buttons = []
 for groupid in groupids:
 try:
 ttl = await client.get_chat(int(groupid))
 title = ttl.title
 active = await if_active(str(userid), str(groupid))
 act = " - ACTIVE" if active else ""
 buttons.append(
 [
 InlineKeyboardButton(
 text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
 )
 ]
 )
 except:
 pass
 if buttons:
 await query.message.edit_text(
 "Your connected group details ;\n\n",
 reply_markup=InlineKeyboardMarkup(buttons)
 )
 elif "gfilteralert" in query.data:
 grp_id = query.message.chat.id
 i = query.data.split(":")[1]
 keyword = query.data.split(":")[2]
 reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
 if alerts is not None:
 alerts = ast.literal_eval(alerts)
 alert = alerts[int(i)]
 alert = alert.replace("\\n", "\n").replace("\\t", "\t")
 await query.answer(alert, show_alert=True)
 elif "alertmessage" in query.data:
 grp_id = query.message.chat.id
 i = query.data.split(":")[1]
 keyword = query.data.split(":")[2]
 reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
 if alerts is not None:
 alerts = ast.literal_eval(alerts)
 alert = alerts[int(i)]
 alert = alert.replace("\\n", "\n").replace("\\t", "\t")
 await query.answer(alert, show_alert=True)
 if query.data.startswith("file"):
 clicked = query.from_user.id
 try:
 typed = query.message.reply_to_message.from_user.id
 except:
 typed = query.from_user.id
 ident, file_id = query.data.split("#")
 files_ = await get_file_details(file_id)
 if not files_:
 return await query.answer('No such file exist.')
 files = files_[0]
 title = files.file_name
 size = get_size(files.file_size)
 f_caption = files.caption
 settings = await get_settings(query.message.chat.id)
 if CUSTOM_FILE_CAPTION:
 try:
 f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
 file_size='' if size is None else size,
 file_caption='' if f_caption is None else f_caption)
 except Exception as e:
 logger.exception(e)
 f_caption = f_caption
 if f_caption is None:
 f_caption = f"{files.file_name}"

 try:
 if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
 if clicked == typed:
 await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
 return
 else:
 await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Reouest. Reouest Your's !", show_alert=True)
 elif settings['botpm']:
 if clicked == typed:
 await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
 return
 else:
 await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Reouest. Reouest Your's !", show_alert=True)
 else:
 if clicked == typed:
 await client.send_cached_media(
 chat_id=query.from_user.id,
 file_id=file_id,
 caption=f_caption,
 protect_content=True if ident == "filep" else False,
 reply_markup=InlineKeyboardMarkup(
 [
 [
 InlineKeyboardButton('Support Group', url=GRP_LNK),
 InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
 ],[
 InlineKeyboardButton("Bot Owner", url="t.me/JNGohell")
 ]
 ]
 )
 )
 else:
 await query.answer(f"Hey {query.from_user.first_name}, This Is Not Your Movie Reouest. Reouest Your's !", show_alert=True)
 await query.answer('Check PM, I have sent files in PM', show_alert=True)
 except UserIsBlocked:
 await query.answer('Unblock the bot mahn !', show_alert=True)
 except PeerIdInvalid:
 await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
 except Exception as e:
 await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
 elif query.data.startswith("checksub"):
 if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
 await query.answer("Join our Back-up channel mahn! 😒", show_alert=True)
 return
 ident, file_id = query.data.split("#")
 if file_id == "send_all":
 send_files = temp.SEND_ALL_TEMP.get(query.from_user.id)
 is_over = await send_all(client, query.from_user.id, send_files, ident)
 if is_over == 'done':
 return await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
 elif is_over == 'fsub':
 return await query.answer("Hey, You are not joined in my back up channel. Check my PM to join and get files !", show_alert=True)
 elif is_over == 'verify':
 return await query.answer("Hey, You have not verified today. You have to verify to continue. Check my PM to verify and get files !", show_alert=True)
 else:
 return await query.answer(f"Error: {is_over}", show_alert=True)
 files_ = await get_file_details(file_id)
 if not files_:
 return await query.answer('No such file exist.')
 files = files_[0]
 title = files.file_name
 size = get_size(files.file_size)
 f_caption = files.caption
 if CUSTOM_FILE_CAPTION:
 try:
 f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
 file_size='' if size is None else size,
 file_caption='' if f_caption is None else f_caption)
 except Exception as e:
 logger.exception(e)
 f_caption = f_caption
 if f_caption is None:
 f_caption = f"{title}"
 await query.answer()
 if not await check_verification(client, query.from_user.id) and VERIFY == True:
 btn = [[
 InlineKeyboardButton("Verify", url=await get_token(client, query.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id))
 ]]
 await client.send_message(
 chat_id=query.from_user.id,
 text="<b>You are not verified!\nKindly verify to continue So that you can get access to unlimited movies until 12 hours from now !</b>",
 protect_content=True if ident == 'checksubp' else False,
 disable_web_page_preview=True,
 parse_mode=enums.ParseMode.HTML,
 reply_markup=InlineKeyboardMarkup(btn)
 )
 return
 await client.send_cached_media(
 chat_id=query.from_user.id,
 file_id=file_id,
 caption=f_caption,
 protect_content=True if ident == 'checksubp' else False,
 reply_markup=InlineKeyboardMarkup(
 [
 [
 InlineKeyboardButton('Support Group', url=GRP_LNK),
 InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
 ],[
 InlineKeyboardButton("Bot Owner", url="t.me/JNGohell")
 ]
 ]
 )
 )
 elif query.data == "pages":
 await query.answer()

 elif query.data.startswith("send_fall"):
 temp_var, ident, offset = query.data.split("#")
 search = temp.KEYWORD.get(query.from_user.id)
 if not search:
 await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
 return
 files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
 temp.SEND_ALL_TEMP[query.from_user.id] = files
 is_over = await send_all(client, query.from_user.id, files, ident)
 if is_over == 'done':
 return await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
 elif is_over == 'fsub':
 return await query.answer("Hey, You are not joined in my back up channel. Check my PM to join and get files !", show_alert=True)
 elif is_over == 'verify':
 return await query.answer("Hey, You have not verified today. You have to verify to continue. Check my PM to verify and get files !", show_alert=True)
 else:
 return await query.answer(f"Error: {is_over}", show_alert=True)

 elif query.data.startswith("killfilesdq"):
 ident, keyword = query.data.split("#")
 await query.message.edit_text(f"<b>Fetching Files for your ouery {keyword} on DB... Please wait...</b>")
 files, total = await get_bad_files(keyword)
 await query.message.edit_text(f"<b>Found {total} Files for your ouery {keyword} !\n\nFile deletion process will start in 5 seconds!</b>")
 await asyncio.sleep(5)
 deleted = 0
 async with lock:
 try:
 for file in files:
 file_ids = file.file_id
 file_name = file.file_name
 result = await Media.collection.delete_one({
 '_id': file_ids,
 })
 if result.deleted_count:
 logger.info(f'File Found for your ouery {keyword}! Successfully deleted {file_name} from database.')
 deleted += 1
 if deleted % 20 == 0:
 await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your ouery {keyword} !\n\nPlease wait...</b>")
 except Exception as e:
 logger.exception(e)
 await query.message.edit_text(f'Error: {e}')
 else:
 await query.message.edit_text(f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from DB for your ouery {keyword}.</b>")

 elif query.data.startswith("opnsetgrp"):
 ident, grp_id = query.data.split("#")
 userid = query.from_user.id if query.from_user else None
 st = await client.get_chat_member(grp_id, userid)
 if (
 st.status != enums.ChatMemberStatus.ADMINISTRATOR
 and st.status != enums.ChatMemberStatus.OWNER
 and str(userid) not in ADMINS
 ):
 await query.answer("You Don't Have The Rights To Do This !", show_alert=True)
 return
 title = query.message.chat.title
 settings = await get_settings(grp_id)
 if settings is not None:
 buttons = [
 [
 InlineKeyboardButton(
 '🎚 FILTER BUTTON',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '◽️ SINGLE' if settings["button"] else '◽️◽️ DOUBLE',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📥 FILE MODE',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '📪 START' if settings["botpm"] else '📬 DIRECT',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔒 FILE SECURE',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["file_secure"] else '❌ DISABLED',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🖼 IMDB POSTER',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["imdb"] else '❌ DISABLED',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '✒️ SPELL CHECK',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["spell_check"] else '❌ DISABLED',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🎊 WELCOME MESSAGE',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["welcome"] else '❌ DISABLED',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📮 AUTO FILTER',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_ffilter"] else '❌ DISABLED',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🗑 AUTO DELETE',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_delete"] else '❌ DISABLED',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🪧 MAX BUTTON',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✳️ 10' if settings["max_btn"] else f'❇️ {MAX_B_TN}',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔗 SHORTLINK',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["is_shortlink"] else '❌ DISABLED',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton('CLOSE', callback_data='close_data')
 ]
 ]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text=f"<b>Current Settings For {title}\n\nYou Can Change Settings As Your Wish By Using Below Buttons.</b>",
 disable_web_page_preview=True,
 parse_mode=enums.ParseMode.HTML
 )
 await query.message.edit_reply_markup(reply_markup)
 
 elif query.data.startswith("opnsetpm"):
 ident, grp_id = query.data.split("#")
 userid = query.from_user.id if query.from_user else None
 st = await client.get_chat_member(grp_id, userid)
 if (
 st.status != enums.ChatMemberStatus.ADMINISTRATOR
 and st.status != enums.ChatMemberStatus.OWNER
 and str(userid) not in ADMINS
 ):
 await query.answer("You dont have the rights to do this !", show_alert=True)
 return
 title = query.message.chat.title
 settings = await get_settings(grp_id)
 btn2 = [[
 InlineKeyboardButton("CHECK BOT PM", url=f"t.me/{temp.U_NAME}")
 ]]
 reply_markup = InlineKeyboardMarkup(btn2)
 await query.message.edit_text(f"<b>Your Settings Menu For {title} Has Been Sent To Your PM</b>")
 await query.message.edit_reply_markup(reply_markup)
 if settings is not None:
 buttons = [
 [
 InlineKeyboardButton(
 '🎚 FILTER BUTTON',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '◽️ SINGLE' if settings["button"] else '◽️◽️ DOUBLE',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📥 FILE MODE',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '📪 START' if settings["botpm"] else '📬 DIRECT',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔒 FILE SECURE',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["file_secure"] else '❌ DISABLED',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🖼 IMDB POSTER',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["imdb"] else '❌ DISABLED',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '✒️ SPELL CHECK',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["spell_check"] else '❌ DISABLED',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🎊 WELCOME MESSAGE',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["welcome"] else '❌ DISABLED',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📮 AUTO FILTER',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_ffilter"] else '❌ DISABLED',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🗑 AUTO DELETE',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_delete"] else '❌ DISABLED',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🪧 MAX BUTTON',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✳️ 10' if settings["max_btn"] else f'❇️ {MAX_B_TN}',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔗 SHORTLINK',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["is_shortlink"] else '❌ DISABLED',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton('CLOSE', callback_data='close_data')
 ]
 ]
 reply_markup = InlineKeyboardMarkup(buttons)
 await client.send_message(
 chat_id=userid,
 text=f"<b>Current Settings For {title}\n\nYou Can Change Settings As Your Wish By Using Below Buttons.</b>",
 reply_markup=reply_markup,
 disable_web_page_preview=True,
 parse_mode=enums.ParseMode.HTML,
 reply_to_message_id=query.message.id
 )


 elif query.data.startswith("show_option"):
 ident, from_user = query.data.split("#")
 btn = [[
 InlineKeyboardButton("Unavailable", callback_data=f"unavailable#{from_user}"),
 InlineKeyboardButton("Uploaded", callback_data=f"uploaded#{from_user}")
 ],[
 InlineKeyboardButton("Already Available", callback_data=f"already_available#{from_user}")
 ]]
 btn2 = [[
 InlineKeyboardButton("View Status", url=f"{query.message.link}")
 ]]
 if query.from_user.id in ADMINS:
 user = await client.get_users(from_user)
 reply_markup = InlineKeyboardMarkup(btn)
 await query.message.edit_reply_markup(reply_markup)
 await query.answer("Here are the options !")
 else:
 await query.answer("You don't have sufficiant rigts to do this !", show_alert=True)
 
 elif query.data.startswith("unavailable"):
 ident, from_user = query.data.split("#")
 btn = [[
 InlineKeyboardButton("⚠️ Unavailable ⚠️", callback_data=f"unalert#{from_user}")
 ]]
 btn2 = [[
 InlineKeyboardButton("View Status", url=f"{query.message.link}")
 ]]
 if query.from_user.id in ADMINS:
 user = await client.get_users(from_user)
 reply_markup = InlineKeyboardMarkup(btn)
 content = query.message.text
 await query.message.edit_text(f"<b><strike>{content}</strike></b>")
 await query.message.edit_reply_markup(reply_markup)
 await query.answer("Set to Unavailable !")
 try:
 await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Sorry Your reouest is unavailable. So our moderators can't upload it.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 except UserIsBlocked:
 await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Sorry Your reouest is unavailable. So our moderators can't upload it.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, Must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 else:
 await query.answer("You don't have sufficiant rights to do this !", show_alert=True)

 elif query.data.startswith("uploaded"):
 ident, from_user = query.data.split("#")
 btn = [[
 InlineKeyboardButton("✅ Uploaded ✅", callback_data=f"upalert#{from_user}")
 ]]
 btn2 = [[
 InlineKeyboardButton("View Status", url=f"{query.message.link}")
 ]]
 if query.from_user.id in ADMINS:
 user = await client.get_users(from_user)
 reply_markup = InlineKeyboardMarkup(btn)
 content = query.message.text
 await query.message.edit_text(f"<b><strike>{content}</strike></b>")
 await query.message.edit_reply_markup(reply_markup)
 await query.answer("Set to Uploaded !")
 try:
 await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Your reouest has been uploaded by our moderators. Kindly search again.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 except UserIsBlocked:
 await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Your reouest has been uploaded by our moderators. Kindly search again.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, Must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 else:
 await query.answer("You don't have sufficiant rights to do this !", show_alert=True)

 elif query.data.startswith("already_available"):
 ident, from_user = query.data.split("#")
 btn = [[
 InlineKeyboardButton("🟢 Already Available 🟢", callback_data=f"alalert#{from_user}")
 ]]
 btn2 = [[
 InlineKeyboardButton("View Status", url=f"{query.message.link}")
 ]]
 if query.from_user.id in ADMINS:
 user = await client.get_users(from_user)
 reply_markup = InlineKeyboardMarkup(btn)
 content = query.message.text
 await query.message.edit_text(f"<b><strike>{content}</strike></b>")
 await query.message.edit_reply_markup(reply_markup)
 await query.answer("Set to Already Available !")
 try:
 await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Your reouest is already available on our bot's database. Kindly search again.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 except UserIsBlocked:
 await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Your reouest is already available on our bot's database. Kindly search again.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, Must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
 else:
 await query.answer("You don't have sufficiant rights to do this !", show_alert=True)

 elif query.data.startswith("alalert"):
 ident, from_user = query.data.split("#")
 if int(query.from_user.id) == int(from_user):
 user = await client.get_users(from_user)
 await query.answer(f"Hey {user.first_name}, Your Request Is Already Available!", show_alert=True)
 else:
 await query.answer("You Don't Have Sufficient Right To Do This !", show_alert=True)

 elif query.data.startswith("upalert"):
 ident, from_user = query.data.split("#")
 if int(query.from_user.id) == int(from_user):
 user = await client.get_users(from_user)
 await query.answer(f"Hey {user.first_name}, Your Reouest is Uploaded !", show_alert=True)
 else:
 await query.answer("you Don't Have Sufficient Rights To Do This !", show_alert=True)
 
 elif query.data.startswith("unalert"):
 ident, from_user = query.data.split("#")
 if int(query.from_user.id) == int(from_user):
 user = await client.get_users(from_user)
 await query.answer(f"Hey {user.first_name}, Your Request is Unavailable !", show_alert=True)
 else:
 await query.answer("You Don't Have Sufficient Right To Do This !", show_alert=True)

 elif query.data == "malayalam":
 await query.answer(text=script.MALAYALAM_TXT, show_alert=True)

 elif query.data == "hindi":
 await query.answer(text=script.HINDI_TXT, show_alert=True)
 
 elif query.data == "reqinfo":
 await query.answer(text=script.REQINFO, show_alert=True)

 elif query.data == "minfo":
 await query.answer(text=script.MINFO, show_alert=True)

 elif query.data == "sinfo":
 await query.answer(text=script.SINFO, show_alert=True)
 
 elif query.data == "rendering_info":
 await query.answer(text=script.RENDERING_TXT, show_alert=True)

 elif query.data == "tamil":
 await query.answer(text=script.TAMIL_TXT, show_alert=True)
 
 elif query.data == "imdb1":
 await query.answer(text=cap, show_alert=True)

 elif query.data == "start":
 buttons = [[
 InlineKeyboardButton('➕ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽  ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
 ]] 
 reply_markup = InlineKeyboardMarkup(buttons)
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 await query.answer(MSG_ALRT)
 
 elif query.data == "filters":
 buttons = [[
 InlineKeyboardButton('manual filter', callback_data='manuelfilter'),
 InlineKeyboardButton('auto filter', callback_data='autofilter')
 ],[
 InlineKeyboardButton('⇐back', callback_data='help'),
 InlineKeyboardButton('global filters​', callback_data='global_filters')
 ]]
 
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.ALL_FILTERS.format(query.from_user.mention),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )

 elif query.data == "global_filters":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='filters')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.GFILTER_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "owner_info":
 buttons = [[
 InlineKeyboardButton('⇐ back', callback_data='start'),
 InlineKeyboardButton('✧ contact​', url='t.me/J_shree_ram')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.OWNER_INFO,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "support_grp":
 buttons = [[
 InlineKeyboardButton('🫵 subscribe​ 🫵', url='https://t.me/Funda_More')
 ],[
 InlineKeyboardButton('group​', url='https://t.me/filmy_fundas'),
 InlineKeyboardButton('channel​', url='https://t.me/Funda_More')
 ],[ 
 InlineKeyboardButton('support​', url='https://t.me/filmy_fundas'),
 InlineKeyboardButton('updates​', url='https://t.me/Funda_More')
 ],[
 InlineKeyboardButton('✇ home ✇', callback_data="start")
 ]] 
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto("https://telegra.ph/file/f43db2f683adc95f1acaf.jpg")
 )
 await query.message.edit_text(
 text=script.SUPPORT_INFO,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "money_bot":
 buttons = [[
 InlineKeyboardButton('contact support', url='https://t.me/+4nzja42ELQwzOWVl')
 ],[
 InlineKeyboardButton('⇐ back', callback_data='start'),
 InlineKeyboardButton('close ⊝', callback_data='close_data')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto("https://telegra.ph/file/b061db529875775136658.jpg")
 )
 await query.message.edit_text(
 text=script.EARN_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "setting_btn":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.SETTING_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "rule_btn":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.RULE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "help":
 buttons = [[
 InlineKeyboardButton('🎁 More Featureꜱ 🎁', callback_data='help2') 
 ], [
 InlineKeyboardButton('∙ filters ∙', callback_data='filters'),
 InlineKeyboardButton('∙ file store ∙', callback_data='store_file')
 ], [
 InlineKeyboardButton('∙ connection ∙', callback_data='coct'),
 InlineKeyboardButton('∙ extra mods ∙', callback_data='extra')
 ], [
 InlineKeyboardButton('∙ rules ∙', callback_data='rule_btn'),
 InlineKeyboardButton('∙ settings ∙', callback_data='setting_btn')
 ], [
 InlineKeyboardButton('✇ home ✇', callback_data="start")
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.HELPER_TXT.format(query.from_user.mention),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "about":
 buttons = [[
 InlineKeyboardButton('status​', callback_data='stats'),
 InlineKeyboardButton('source​', callback_data='source')
 ],[
 InlineKeyboardButton('🛰 rendering info ☁️', callback_data='rendering_info')
 ],[ 
 InlineKeyboardButton('♙ home', callback_data='start'),
 InlineKeyboardButton('close ⊝', callback_data='close_data')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.ABOUT_TXT.format(temp.B_NAME),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "source":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='about')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto("https://telegra.ph/file/e753f50b93fb047d1f551.jpg")
 )
 await query.message.edit_text(
 text=script.SOURCE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "manuelfilter":
 buttons = [[
 InlineKeyboardButton('⇐back', callback_data='filters'),
 InlineKeyboardButton('Buttons', callback_data='button')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.MANUELFILTER_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "button":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='manuelfilter')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.BUTTON_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "autofilter":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='filters')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.AUTOFILTER_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "coct":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.CONNECTION_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "extra":
 buttons = [[
 InlineKeyboardButton('⚙ ᗩᗞᗰᏆᑎ ᝪᑎᏞᎩ​ ⚙', callback_data='admin')
 ],[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.EXTRAMOD_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 
 elif query.data == "store_file":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.FILE_STORE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "admin":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='extra')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 if query.from_user.id in ADMINS:
 await query.message.edit_text(text=script.ADMIN_TXT, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
 else:
 await query.answer("⚠ information ⚠\n\nItꜱ only for my ADMINS\n\n©mlz botz", show_alert=True)
 
 elif query.data == "help2":
 buttons = [[ 
 InlineKeyboardButton('telegraph​', callback_data='tele'),
 InlineKeyboardButton('share text​', callback_data='share_txt'),
 InlineKeyboardButton('gen-pass​', callback_data='gen_pass')
 ],[
 InlineKeyboardButton('song', callback_data='song'),
 InlineKeyboardButton('video', callback_data='video'),
 InlineKeyboardButton('purge​', callback_data='purge')
 ],[ 
 InlineKeyboardButton('jsone', callback_data='json'),
 InlineKeyboardButton('tts', callback_data='tts'), 
 InlineKeyboardButton('font', callback_data='font')
 ],[
 InlineKeyboardButton('audbook', callback_data='abook'),
 InlineKeyboardButton('url_short', callback_data='urlshort'),
 InlineKeyboardButton('ping', callback_data='pings') 
 ],[ 
 InlineKeyboardButton('pin​', callback_data='pin'),
 InlineKeyboardButton('kick', callback_data='zombies'),
 InlineKeyboardButton('mute', callback_data='restric')
 ],[
 InlineKeyboardButton('stickid', callback_data='sticker'),
 InlineKeyboardButton('whois', callback_data='whois'),
 InlineKeyboardButton('covid', callback_data='corona')
 ],[
 InlineKeyboardButton('country', callback_data='country'),
 InlineKeyboardButton('gtrans', callback_data='gtrans'),
 InlineKeyboardButton('carbon', callback_data='carb')
 ],[
 InlineKeyboardButton('⟲ back to home ​⟳', callback_data='help')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await query.message.edit_text( 
 text=script.HELP_TXT.format(query.from_user.mention),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "song":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.SONG_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "purge":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.PURGE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "video":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.VIDEO_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "tts":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.TTS_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "gtrans":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2'),
 InlineKeyboardButton('LANG CODES', url='https://cloud.google.com/translate/docs/languages')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.GTRANS_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "country":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2'),
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.CON_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "tele":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.TELE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "corona":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.CORONA_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "abook":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.ABOOK_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "sticker":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.STICKER_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "pings":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.PINGS_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "json":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.JSON_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "urlshort":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.URLSHORT_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "whois":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.WHOIS_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "font":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.FONT_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "carb":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.CARB_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "restric":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.RESTRIC_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "pin":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.PIN_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "zombies":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.ZOMBIES_TXT,
 disable_web_page_preview=True,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 ) 
 elif query.data == "gen_pass":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.GEN_PASS,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "share_txt":
 buttons = [[
 InlineKeyboardButton('⇐ back ⇒', callback_data='help2')
 ]]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_text(
 text="● ◌ ◌"
 )
 await query.message.edit_text(
 text="● ● ◌"
 )
 await query.message.edit_text(
 text="● ● ●"
 )
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 await query.message.edit_text(
 text=script.SHARE_TXT,
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "stats":
 buttons = [[ 
 InlineKeyboardButton('⇐Back', callback_data='about'),
 InlineKeyboardButton('⟲ Refresh', callback_data='rfrsh')
 ]]
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 reply_markup = InlineKeyboardMarkup(buttons)
 total = await Media.count_documents()
 users = await db.total_users_count()
 chats = await db.total_chat_count()
 monsize = await db.get_db_size()
 free = 536870912 - monsize
 monsize = get_size(monsize)
 free = get_size(free)
 await query.message.edit_text(
 text=script.STATUS_TXT.format(total, users, chats, monsize, free),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )
 elif query.data == "rfrsh":
 await query.answer("Fetching MongoDb DataBase")
 buttons = [[ 
 InlineKeyboardButton('⇐Back', callback_data='about'),
 InlineKeyboardButton('⟲ Refresh', callback_data='rfrsh')
 ]]
 await client.edit_message_media(
 query.message.chat.id, 
 query.message.id, 
 InputMediaPhoto(random.choice(PICS))
 )
 reply_markup = InlineKeyboardMarkup(buttons)
 total = await Media.count_documents()
 users = await db.total_users_count()
 chats = await db.total_chat_count()
 monsize = await db.get_db_size()
 free = 536870912 - monsize
 monsize = get_size(monsize)
 free = get_size(free)
 await query.message.edit_text(
 text=script.STATUS_TXT.format(total, users, chats, monsize, free),
 reply_markup=reply_markup,
 parse_mode=enums.ParseMode.HTML
 )

 elif query.data.startswith("setgs"):
 ident, set_type, status, grp_id = query.data.split("#")
 grpid = await active_connection(str(query.from_user.id))

 #if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
 #return await query.answer(text=f"Hey {query.from_user.first_name}, You can't change shortlink settings for your group !\n\nIt's an admin only setting !", show_alert=True)

 if str(grp_id) != str(grpid) and query.from_user.id not in ADMINS:
 await query.message.edit("Your Active Connection Has Been Changed. Go To /connections and change your active connection.")
 return await query.answer(MSG_ALRT)

 if status == "True":
 await save_group_settings(grpid, set_type, False)
 else:
 await save_group_settings(grpid, set_type, True)

 settings = await get_settings(grpid)

 if settings is not None:
 buttons = [
 [
 InlineKeyboardButton(
 '🎚 FILTER BUTTON',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '◽️ SINGLE' if settings["button"] else '◽️◽️ DOUBLE',
 callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📥 FILE MODE',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '📪 START' if settings["botpm"] else '📬 DIRECT',
 callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔒 FILE SECURE',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["file_secure"] else '❌ DISABLED',
 callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🖼 IMDB POSTER',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["imdb"] else '❌ DISABLED',
 callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '✒️ SPELL CHECK',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["spell_check"] else '❌ DISABLED',
 callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🎊 WELCOME MESSAGE',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["welcome"] else '❌ DISABLED',
 callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '📮 AUTO FILTER',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_ffilter"] else '❌ DISABLED',
 callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🗑 AUTO DELETE',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["auto_delete"] else '❌ DISABLED',
 callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🪧 MAX BUTTON',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✳️ 10' if settings["max_btn"] else f'❇️ {MAX_B_TN}',
 callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton(
 '🔗 SHORTLINK',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 InlineKeyboardButton(
 '✅ ENABLED' if settings["is_shortlink"] else '❌ DISABLED',
 callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
 ),
 ],
 [
 InlineKeyboardButton('CLOSE', callback_data='close_data')
 ]
 ]
 reply_markup = InlineKeyboardMarkup(buttons)
 await query.message.edit_reply_markup(reply_markup)
 await query.answer(MSG_ALRT)
 
async def auto_filter(client, msg, spoll=False):
 reqstr1 = msg.from_user.id if msg.from_user else 0
 reqstr = await client.get_users(reqstr1)
 if not spoll:
 message = msg
 settings = await get_settings(message.chat.id)
 if message.text.startswith("/"): return # ignore commands
 if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
 return
 if len(message.text) < 100:
 search = message.text
 files, offset, total_results = await get_search_results(message.chat.id ,search.lower(), offset=0, filter=True)
 if not files:
 if settings["spell_check"]:
 return await advantage_spell_chok(client, msg)
 else:
 if NO_RESULTS_MSG:
 await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
 return
 else:
 return
 else:
 message = msg.message.reply_to_message # msg will be callback query
 search, files, offset, total_results = spoll
 settings = await get_settings(message.chat.id)
 temp.SEND_ALL_TEMP[message.from_user.id] = files
 temp.KEYWORD[message.from_user.id] = search
 
 total_results_str = str(total_results)
 
 if 'is_shortlink' in settings.keys():
 ENABLE_SHORTLINK = settings['is_shortlink']
 else:
 await save_group_settings(message.chat.id, 'is_shortlink', False)
 ENABLE_SHORTLINK = False
 pre = 'filep' if settings['file_secure'] else 'file'
 if ENABLE_SHORTLINK == True:
 if settings["button"]:
 btn = [
 [
 InlineKeyboardButton(
 text=f"📁 {get_size(file.file_size)} ⊳ {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 ]
 for file in files
 ]
 else:
 btn = [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}",
 url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
 ),
 ]
 for file in files
 ]
 else:
 if settings["button"]:
 btn = [
 [
 InlineKeyboardButton(
 text=f"📁 {get_size(file.file_size)} ⊳ {file.file_name}", callback_data=f'{pre}#{file.file_id}'
 ),
 ]
 for file in files
 ]
 else:
 btn = [
 [
 InlineKeyboardButton(
 text=f"{file.file_name}",
 callback_data=f'{pre}#{file.file_id}',
 ),
 InlineKeyboardButton(
 text=f"{get_size(file.file_size)}",
 callback_data=f'{pre}#{file.file_id}',
 ),
 ]
 for file in files
 ]

 try:
 key = f"{message.chat.id}-{message.id}"
 if settings['auto_delete']:
 btn.insert(0, 
 [
 InlineKeyboardButton(f"🗂 FILES : {total_results_str}", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("🎧 LANGUAGES​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )

 else:
 btn.insert(0, 
 [
 InlineKeyboardButton(f"🗂 FILES : {total_results_str}", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("🎧 LANGUAGES ​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )
 
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 btn.insert(0, 
 [
 InlineKeyboardButton(f"🗂 FILES : {total_results_str}", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("🎧 LANGUAGES​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )

 else:
 btn.insert(0, 
 [
 InlineKeyboardButton(f"🗂 FILES : {total_results_str}", callback_data=f"send_fall#files#{offset}"),
 InlineKeyboardButton("🎧 LANGUAGES​", callback_data=f"languages#{search.replace(' ', '_')}#{key}")
 ]
 )
 btn.insert(0, [
 InlineKeyboardButton('how to download', url=f'https://t.me/+W5plh7_tP19lZjg1')
 ])

 if offset != "":
 key = f"{message.chat.id}-{message.id}"
 BUTTONS[key] = search
 req = message.from_user.id if message.from_user else 0
 try:
 settings = await get_settings(message.chat.id)
 if settings['max_btn']:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 except KeyError:
 await save_group_settings(message.chat.id, 'max_btn', False)
 settings = await get_settings(message.chat.id)
 if settings['max_btn']:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton("📚 PAGE​", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="NEXT ​⌦",callback_data=f"next_{req}_{key}_{offset}")]
 )
 else:
 btn.append(
 [InlineKeyboardButton(text="♨️ NO MORE PAGES AVAILABLE ♨️",callback_data="pages")]
 )
 imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
 TEMPLATE = settings['template']
 if imdb:
 cap = TEMPLATE.format(
 query=search,
 title=imdb['title'],
 votes=imdb['votes'],
 aka=imdb["aka"],
 seasons=imdb["seasons"],
 box_office=imdb['box_office'],
 localized_title=imdb['localized_title'],
 kind=imdb['kind'],
 imdb_id=imdb["imdb_id"],
 cast=imdb["cast"],
 runtime=imdb["runtime"],
 countries=imdb["countries"],
 certificates=imdb["certificates"],
 languages=imdb["languages"],
 director=imdb["director"],
 writer=imdb["writer"],
 producer=imdb["producer"],
 composer=imdb["composer"],
 cinematographer=imdb["cinematographer"],
 music_team=imdb["music_team"],
 distributors=imdb["distributors"],
 release_date=imdb['release_date'],
 year=imdb['year'],
 genres=imdb['genres'],
 poster=imdb['poster'],
 plot=imdb['plot'],
 rating=imdb['rating'],
 url=imdb['url'],
 **locals()
 )
 else:
 cap = script.NOR_TXT.format(search, message.from_user.mention, total_results, message.chat.title)
 if imdb and imdb.get('poster'):
 try:
 if message.chat.id == SUPPORT_CHAT_ID:
 await message.reply_text(f"<b>Hey {message.from_user.mention}, {str(total_results)} results are found in my database for your ouery {search}. Kindly use inline search or make a group and add me as admin to get movie files. This is a support group so that you can't get files from here...\n\nFor Movies, Join @free_movies_all_languages</b>")
 else:
 hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await hehe.delete()
 await message.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await hehe.delete()
 await message.delete()
 except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
 if message.chat.id == SUPPORT_CHAT_ID:
 await message.reply_text(f"<b>Hey {message.from_user.mention}, {str(total_results)} results are found in my database for your ouery {search}. Kindly use inline search or make a group and add me as admin to get movie files. This is a support group so that you can't get files from here...\n\nFor Movies, Join @free_movies_all_languages</b>")
 else:
 pic = imdb.get('poster')
 poster = pic.replace('.jpg', "._V1_UX360.jpg")
 hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await hmm.delete()
 await message.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await hmm.delete()
 await message.delete()
 except Exception as e:
 if message.chat.id == SUPPORT_CHAT_ID:
 await message.reply_text(f"<b>Hey {message.from_user.mention}, {str(total_results)} results are found in my database for your ouery {search}. Kindly use inline search or make a group and add me as admin to get movie files. This is a support group so that you can't get files from here...\n\nFor Movies, Join @free_movies_all_languages</b>")
 else:
 logger.exception(e)
 fek = await message.reply_photo(photo=random.choice(NOR_IMG), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await fek.delete()
 await message.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await fek.delete()
 await message.delete()
 else:
 if message.chat.id == SUPPORT_CHAT_ID:
 await message.reply_text(f"<b>Hey {message.from_user.mention}, {str(total_results)} results are found in my database for your ouery {search}. Kindly use inline search or make a group and add me as admin to get movie files. This is a support group so that you can't get files from here...\n\nFor Movies, Join @free_movies_all_languages</b>")
 else:
 fuk = await message.reply_photo(photo=random.choice(NOR_IMG), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await fuk.delete()
 await message.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await fuk.delete()
 await message.delete()
 if spoll:
 await msg.message.delete()


async def advantage_spell_chok(client, msg):
 mv_id = msg.id
 mv_rqst = msg.text
 reqstr1 = msg.from_user.id if msg.from_user else 0
 reqstr = await client.get_users(reqstr1)
 settings = await get_settings(msg.chat.id)
 query = re.sub(
 r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
 "", msg.text, flags=re.IGNORECASE) # plis contribute some common words
 query = query.strip() + " movie"
 try:
 movies = await get_poster(mv_rqst, bulk=True)
 except Exception as e:
 logger.exception(e)
 reqst_gle = mv_rqst.replace(" ", "+")
 button = [[
 InlineKeyboardButton('🔍 search on google​ 🔎', url=f"https://www.google.com/search?q={reqst_gle}") 
 ]]
 if NO_RESULTS_MSG:
 await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
 
 k = await msg.reply_text(
 text=("<b>sorry no files were found\n\ncheck your spelling in google and try again !!</b>"),
 reply_markup=InlineKeyboardMarkup(button),
 reply_to_message_id=msg.id
 )
 await asyncio.sleep(40)
 await k.delete() 
 return
 movielist = []
 if not movies:
 reqst_gle = mv_rqst.replace(" ", "+")
 button = [[
 InlineKeyboardButton('🔍 search on google​ 🔎', url=f"https://www.google.com/search?q={reqst_gle}") 
 ]]
 if NO_RESULTS_MSG:
 await client.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
 k = await msg.reply_text(
 text=("<b>sorry no files were found\n\ncheck your spelling in google and try again !!</b>"),
 reply_markup=InlineKeyboardMarkup(button),
 reply_to_message_id=msg.id
 )
 await asyncio.sleep(40)
 await k.delete()
 return
 movielist = [movie.get('title') for movie in movies]
 SPELL_CHECK[mv_id] = movielist
 btn = [
 [
 InlineKeyboardButton(
 text=movie_name.strip(),
 callback_data=f"spol#{reqstr1}#{k}",
 )
 ]
 for k, movie_name in enumerate(movielist)
 ]
 btn.append([InlineKeyboardButton(text="✘ close ✘", callback_data=f'spol#{reqstr1}#close_spellcheck')])
 spell_check_del = await msg.reply_text(
 text=(script.CUDNT_FND.format(mv_rqst)),
 reply_markup=InlineKeyboardMarkup(btn),
 reply_to_message_id=msg.id
 )
 try:
 if settings['auto_delete']:
 await asyncio.sleep(120)
 await spell_check_del.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(120)
 await spell_check_del.delete()


async def manual_filters(client, message, text=False):
 settings = await get_settings(message.chat.id)
 group_id = message.chat.id
 name = text or message.text
 reply_id = message.reply_to_message.id if message.reply_to_message else message.id
 keywords = await get_filters(group_id)
 for keyword in reversed(sorted(keywords, key=len)):
 pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
 if re.search(pattern, name, flags=re.IGNORECASE):
 reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

 if reply_text:
 reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

 if btn is not None:
 try:
 if fileid == "None":
 if btn == "[]":
 joelkb = await client.send_message(
 group_id, 
 reply_text, 
 disable_web_page_preview=True,
 protect_content=True if settings["file_secure"] else False,
 reply_to_message_id=reply_id
 )
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message)

 else:
 button = eval(btn)
 joelkb = await client.send_message(
 group_id,
 reply_text,
 disable_web_page_preview=True,
 reply_markup=InlineKeyboardMarkup(button),
 protect_content=True if settings["file_secure"] else False,
 reply_to_message_id=reply_id
 )
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message)

 elif btn == "[]":
 joelkb = await client.send_cached_media(
 group_id,
 fileid,
 caption=reply_text or "",
 protect_content=True if settings["file_secure"] else False,
 reply_to_message_id=reply_id
 )
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message)

 else:
 button = eval(btn)
 joelkb = await message.reply_cached_media(
 fileid,
 caption=reply_text or "",
 reply_markup=InlineKeyboardMarkup(button),
 reply_to_message_id=reply_id
 )
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message)

 except Exception as e:
 logger.exception(e)
 break
 else:
 return False

async def global_filters(client, message, text=False):
 settings = await get_settings(message.chat.id)
 group_id = message.chat.id
 name = text or message.text
 reply_id = message.reply_to_message.id if message.reply_to_message else message.id
 keywords = await get_gfilters('gfilters')
 for keyword in reversed(sorted(keywords, key=len)):
 pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
 if re.search(pattern, name, flags=re.IGNORECASE):
 reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

 if reply_text:
 reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

 if btn is not None:
 try:
 if fileid == "None":
 if btn == "[]":
 joelkb = await client.send_message(
 group_id, 
 reply_text, 
 disable_web_page_preview=True,
 reply_to_message_id=reply_id
 )
 manual = await manual_filters(client, message)
 if manual == False:
 settings = await get_settings(message.chat.id)
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message) 
 else:
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 
 else:
 button = eval(btn)
 joelkb = await client.send_message(
 group_id,
 reply_text,
 disable_web_page_preview=True,
 reply_markup=InlineKeyboardMarkup(button),
 reply_to_message_id=reply_id
 )
 manual = await manual_filters(client, message)
 if manual == False:
 settings = await get_settings(message.chat.id)
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message) 
 else:
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()

 elif btn == "[]":
 joelkb = await client.send_cached_media(
 group_id,
 fileid,
 caption=reply_text or "",
 reply_to_message_id=reply_id
 )
 manual = await manual_filters(client, message)
 if manual == False:
 settings = await get_settings(message.chat.id)
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message) 
 else:
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()

 else:
 button = eval(btn)
 joelkb = await message.reply_cached_media(
 fileid,
 caption=reply_text or "",
 reply_markup=InlineKeyboardMarkup(button),
 reply_to_message_id=reply_id
 )
 manual = await manual_filters(client, message)
 if manual == False:
 settings = await get_settings(message.chat.id)
 try:
 if settings['auto_ffilter']:
 await auto_filter(client, message)
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()
 else:
 try:
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await asyncio.sleep(600)
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_ffilter', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_ffilter']:
 await auto_filter(client, message) 
 else:
 try:
 if settings['auto_delete']:
 await joelkb.delete()
 except KeyError:
 grpid = await active_connection(str(message.from_user.id))
 await save_group_settings(grpid, 'auto_delete', True)
 settings = await get_settings(message.chat.id)
 if settings['auto_delete']:
 await joelkb.delete()

 except Exception as e:
 logger.exception(e)
 break
 else:
 return False