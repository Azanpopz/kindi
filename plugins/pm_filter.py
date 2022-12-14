# Kanged From @TroJanZheX

import asyncio
import random
import re
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from myscript import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, DELETE_TIME, P_TTI_SHOW_OFF, IMDB, REDIRECT_TO, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, START_IMAGE_URL, UNAUTHORIZED_CALLBACK_TEXT, SP, redirected_env
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging



logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)



BUTTONS = {}

SPELL_CHECK = {}

FILTER_MOD = {}

BTN = InlineKeyboardMarkup([[InlineKeyboardButton('â¨JOINâ¨', url='https://t.me/nasrani_update')]])


A = """https://telegra.ph/file/3cc0e41bf1e1c00828e55.jpg"""
B = """https://telegra.ph/file/aa82c5a183a2b8822789e.jpg"""
C = """https://telegra.ph/file/abbb3c8d8fafe6cd4465f.jpg"""
D = """https://telegra.ph/file/9bb437585325db53be211.jpg"""
E = """https://telegra.ph/file/f24928ca9720ccb21b597.jpg"""



#@Client.on_message(filters.command('autofilter'))

#async def fil_mod(client, message): 

#      mode_on = ["yes", "on", "true"]

#      mode_of = ["no", "off", "false"]



#      try: 

#         args = message.text.split(None, 1)[1].lower() 

#      except: 

#         return await message.reply("**ð¸ð½ð²ð¾ð¼ð¿ð»ð´ðð´ ð²ð¾ð¼ð¼ð°ð½ð³...**")

      

#      m = await message.reply("**ðð´ððð¸ð½ð¶.../**")



#      if args in mode_on:

#          FILTER_MODE[str(message.chat.id)] = "True" 

#          await m.edit("**ð°ððð¾ðµð¸ð»ðð´ð ð´ð½ð°ð±ð»ð´ð³**")

      

#      elif args in mode_of:

#          FILTER_MODE[str(message.chat.id)] = "False"

#          await m.edit("**ð°ððð¾ðµð¸ð»ðð´ð ð³ð¸ðð°ð±ð»ð´ð³**")

#      else:

#          await m.edit("ððð´ :- /autofilter on ð¾ð /autofilter off")







@Client.on_message((filters.group | filters.private) & filters.text & ~filters.edited & filters.incoming)

async def give_filter(client, message):

    k = await manual_filters(client, message)

    if k == False:

        await auto_filter(client, message)



@Client.on_callback_query(filters.regex(r"^next"))

async def next_page(bot, query):

    ident, req, key, offset = query.data.split("_")

    if int(req) not in [query.from_user.id, 0]:

        return await query.answer(f"à´¹à´²àµ {query.from_user.first_name} à´®àµà´µà´¿ à´µàµà´£à´®àµà´àµà´à´¿àµ½ à´®àµà´µà´¿à´¯àµà´àµ à´ªàµà´°àµ à´à´¯à´àµà´àµà´ ", show_alert=True)

    try:

        offset = int(offset)

    except:

        offset = 0

    search = BUTTONS.get(key)

    if not search:

        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)

        return



    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)

    try:

        n_offset = int(n_offset)

    except:

        n_offset = 0



    if not files:

        return

    settings = await get_settings(query.message.chat.id)

    pre = 'Chat' if settings['redirect_to'] == 'Chat' else 'files'



    if settings['button']:

        btn = [

            [

                InlineKeyboardButton(

                        text=f"ð  [{get_size(file.file_size)}]ð {file.file_name}ð ", 

                        callback_data=f'{pre}_#{file.file_id}#{query.from_user.id}'

                )

            ] 

            for file in files

        ]

    else:

        btn = [

            [

                InlineKeyboardButton(

                    text=f"ð {file.file_name}ð ",

                    callback_data=f'{pre}_#{file.file_id}#{query.from_user.id}',

                ),

                InlineKeyboardButton(

                    text=f"ð {get_size(file.file_size)}ð ",

                    callback_data=f'{pre}_#{file.file_id}#{query.from_user.id}',

                )

            ] 

            for file in files

        ]



    btn.insert(0, 

        [

            InlineKeyboardButton(f'ð° {search} ð°', 'dupe')

        ]

    )

    btn.insert(1,

        [

            InlineKeyboardButton(f'ðï¸ ððððð: {len(files)}', 'dupe'),

            InlineKeyboardButton(f'ð ðððð', 'infoss')

        ]

    )

    



    if 0 < offset <= 10:

        off_set = 0

    elif offset == 0:

        off_set = None

    else:

        off_set = offset - 10

    if n_offset == 0:

        btn.append(

            [InlineKeyboardButton("â²ððððâ²", callback_data=f"next_{req}_{key}_{off_set}"),

             InlineKeyboardButton(f"ð Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",

                                  callback_data="pages")]

        )

    elif off_set is None:

        btn.append(

            [InlineKeyboardButton(f"ð {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),

             InlineKeyboardButton("â³ððððâ³", callback_data=f"next_{req}_{key}_{n_offset}")])

    else:

        btn.append(

            [

                InlineKeyboardButton("â²ððððâ²", callback_data=f"next_{req}_{key}_{off_set}"),

                InlineKeyboardButton(f"ð {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),

                InlineKeyboardButton("â³ððððâ³", callback_data=f"next_{req}_{key}_{n_offset}")

            ],

        )

    try:

        await query.edit_message_reply_markup(

            reply_markup=InlineKeyboardMarkup(btn)

        )



    except MessageNotModified:

        pass

    await query.answer()





@Client.on_callback_query(filters.regex(r"^spolling"))

async def advantage_spoll_choker(bot, query):

    _, user, movie_ = query.data.split('#')

    if int(user) != 0 and query.from_user.id != int(user):

        return await query.answer(f"à´¹à´²àµ {query.from_user.first_name} à´®àµà´µà´¿ à´µàµà´£à´®àµà´àµà´à´¿àµ½ à´®àµà´µà´¿à´¯àµà´àµ à´ªàµà´°àµ à´à´¯à´àµà´àµà´", show_alert=True)

    if movie_ == "close_spellcheck":

        return await query.message.delete()

    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)

    if not movies:

        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)

    movie = movies[(int(movie_))]

    await query.answer('ðà´¤à´¾à´àµà´à´³àµà´àµ à´¸à´¿à´¨à´¿à´® à´à´£àµà´àµà´¨àµà´¨àµ à´ªà´°à´¿à´¶àµà´§à´¿à´àµà´àµà´¨àµà´¨àµ... \n\n\n waiting.... \n\n\n')

    

    k = await manual_filters(bot, query.message, text=movie)

    if k == False:

        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)

        if files:

            k = (movie, files, offset, total_results)

            await auto_filter(bot, query, k)

        else:

            k = await query.message.edit_text(

            text="â­â­ â­â­ â­â­  â­â­ â­â­ â­â­\nSEARCHING...    ðð/ððð%\nâ­â­ â­â­ â­â­  â­â­ â­â­ â­â­"

        )

            k = await query.message.edit_text(

            text="â¬â¬ â¬â­ â­â­  â­â­ â­â­ â­â­\nSEARCHING...     ðð/ððð%\nâ¬â¬ â¬â­ â­â­  â­â­ â­â­ â­â­"

        )

            k = await query.message.edit_text(

            text="â¬â¬ â¬â¬ â¬â­  â­â­ â­â­ â­â­\nSEARCHING...     ðð/ððð%\nâ¬â¬ â¬â¬ â¬â­  â­â­ â­â­ â­â­"

        )

            k = await query.message.edit_text(

            text="â¬â¬ â¬â¬ â¬â¬  â­â­ â­â­ â­â­\nSEARCHING...     ðð/ððð%\nâ¬â¬ â¬â¬ â¬â¬  â­â­ â­â­ â­â­"

        )

            k = await query.message.edit_text(

            text="â¬â¬ â¬â¬ â¬â¬  â¬â¬ â¬â­  â­â­\nSEARCHING...     ðð/ððð%\nâ¬â¬ â¬â¬ â¬â¬  â¬â¬ â¬â­ â­â­"

        )

            k = await query.message.edit_text(

            text="â¬â¬ â¬â¬ â¬â¬  â¬â¬ â¬â¬ â¬â¬\nSEARCHING...    ððð/ððð%\nâ¬â¬ â¬â¬ â¬â¬  â¬â¬ â¬â¬ â¬â¬"

        )

            

            await query.message.reply_text(

            text=f"<b>ððð² ð {query.from_user.mention},,,DvD à´à´±à´àµà´à´¿à´¯ à´¸à´¿à´¨à´¿à´®à´¯à´¾à´£àµà´àµà´à´¿àµ½ 24 à´®à´£à´¿à´àµà´àµà´±à´¿à´¨àµà´³àµà´³à´¿àµ½ à´à´¡àµ à´àµà´¯àµà´¯àµà´¨àµà´¨à´¤à´¾à´¯à´¿à´°à´¿à´àµà´àµà´</b>",

            

            reply_markup=InlineKeyboardMarkup(

                            [

                                [

                                    InlineKeyboardButton('ðððð ðð ðð¨ ðð¨ð®ð« ðð«ð¨ð®ð©ð¬ð', url="http://t.me/nasrani_bot?startgroup=true")

                                ],

                                [

                                    InlineKeyboardButton('ð§©ðð¨ð¨ð ð¥ðð§©', url=f"google.com"),

                                    InlineKeyboardButton('âðð¦ððâ', url=f"https://imdb.com")

                                ]                            

                            ]

                        )

                    )         

                    







@Client.on_callback_query()

async def cb_handler(client: Client, query: CallbackQuery):

    if query.data == "close_data":

        await query.message.delete()

    elif query.data == "delallconfirm":

        userid = query.from_user.id

        chat_type = query.message.chat.type



        if chat_type == "private":

            grpid = await active_connection(str(userid))

            if grpid is not None:

                grp_id = grpid

                try:

                    chat = await client.get_chat(grpid)

                    title = chat.title

                except:

                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)

                    return await query.answer('Piracy Is Crime')

            else:

                await query.message.edit_text(

                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",

                    quote=True

                )

                return await query.answer('Piracy Is Crime')



        elif chat_type in ["group", "supergroup"]:

            grp_id = query.message.chat.id

            title = query.message.chat.title



        else:

            return await query.answer('Piracy Is Crime')



        st = await client.get_chat_member(grp_id, userid)

        if (st.status == "creator") or (str(userid) in ADMINS):

            await del_all(query.message, grp_id, title)

        else:

            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)

    elif query.data == "delallcancel":

        userid = query.from_user.id

        chat_type = query.message.chat.type



        if chat_type == "private":

            await query.message.reply_to_message.delete()

            await query.message.delete()



        elif chat_type in ["group", "supergroup"]:

            grp_id = query.message.chat.id

            st = await client.get_chat_member(grp_id, userid)

            if (st.status == "creator") or (str(userid) in ADMINS):

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

            parse_mode="md"

        )

        return await query.answer('Piracy Is Crime')

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

                parse_mode="md"

            )

        else:

            await query.message.edit_text('Some error occurred!!', parse_mode="md")

        return await query.answer('Piracy Is Crime')

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

                parse_mode="md"

            )

        else:

            await query.message.edit_text(

                f"Some error occurred!!",

                parse_mode="md"

            )

        return await query.answer('Piracy Is Crime')

    elif "deletecb" in query.data:

        await query.answer()



        user_id = query.from_user.id

        group_id = query.data.split(":")[1]



        delcon = await delete_connection(str(user_id), str(group_id))



        if delcon:

            await query.message.edit_text(

                "Successfully deleted connection"

            )

        else:

            await query.message.edit_text(

                f"Some error occurred!!",

                parse_mode="md"

            )

        return await query.answer('Piracy Is Crime')

    elif query.data == "backcb":

        await query.answer()



        userid = query.from_user.id



        groupids = await all_connections(str(userid))

        if groupids is None:

            await query.message.edit_text(

                "There are no active connections!! Connect to some groups first.",

            )

            return await query.answer('Piracy Is Crime')

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

        ident, file_id, rid = query.data.split("#")



        if int(rid) not in [query.from_user.id, 0]:

            return await query.answer(f"à´¹à´²àµ {query.from_user.first_name} à´®àµà´µà´¿ à´µàµà´£à´®àµà´àµà´à´¿àµ½ à´®àµà´µà´¿à´¯àµà´àµ à´ªàµà´°àµ à´à´¯à´àµà´àµà´", show_alert=True)



        files_ = await get_file_details(file_id)

        if not files_:

            return await query.answer('No such file exist.')

        files = files_[0]

        title = files.file_name

        size = get_size(files.file_size)

        mention = query.from_user.mention

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


        buttons = [
            [
                InlineKeyboardButton('â­ï¸ Support', url='https://t.me/mazhatthullikal'),
                InlineKeyboardButton('Channel â­ï¸', url='https://t.me/mazhatthullikal')
            ],
            [
                InlineKeyboardButton('ð¬ Series & Movie Club ð¬', url=f'https://t.me/mazhatthullikal')
            ]
            ]
        
        try:

            if AUTH_CHANNEL and not await is_subscribed(client, query):

                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

                return

            elif settings['botpm']:

                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

                return

            else:

                buttons = [
                  [
                        InlineKeyboardButton('â­ï¸ Support', url='https://t.me/mazhatthullikal'),
                        InlineKeyboardButton('Channel â­ï¸', url='https://t.me/mazhatthullikal')
                  ],
                  [
                        InlineKeyboardButton('ð¬ Series & Movie Club ð¬', url=f'https://t.me/mazhatthullikal')
                  ]
                  ]
        
                await client.send_cached_media(

                    chat_id=query.from_user.id,

                    file_id=file_id,

                    caption=f_caption,

                    protect_content=True if ident == "filep" else False 

                )

                await query.answer('Check PM, I have sent files in pm', show_alert=True)

        except UserIsBlocked:

            await query.answer('Unblock the bot mahn !', show_alert=True)

        except PeerIdInvalid:

            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

        except Exception as e:

            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

    

    elif query.data.startswith("Chat"):

        ident, file_id, rid = query.data.split("#")



        if int(rid) not in [query.from_user.id, 0]:

            return await query.answer(f"à´¹à´²àµ {query.from_user.first_name} à´®àµà´µà´¿ à´µàµà´£à´®àµà´àµà´à´¿àµ½ à´®àµà´µà´¿à´¯àµà´àµ à´ªàµà´°àµ à´à´¯à´àµà´àµà´", show_alert=True)



        files_ = await get_file_details(file_id)

        if not files_:

            return await query.answer('No such file exist.')

        files = files_[0]

        title = files.file_name

        size = get_size(files.file_size)

        mention = query.from_user.mention

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

            size = size

            mention = mention

        if f_caption is None:

            f_caption = f"{files.file_name}"

            size = f"{files.file_size}"

            mention = f"{query.from_user.mention}"



        try:

            buttons = [

                    [

                        InlineKeyboardButton('Series', url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"),

                        InlineKeyboardButton('Movies', url='https://t.me/nasrani_update'),

                    ]

                    ]

            msg = await client.send_cached_media(

                chat_id=AUTH_CHANNEL,

                file_id=file_id,

                caption=f'<b> ððð² ð {query.from_user.mention} </b>ð\n ð Má´á´ Éªá´ Ná´á´á´ : <code>{title}</code>\n âï¸ Má´á´ Éªá´ SÉªá´¢á´: {size}  \n\nâ ï¸ à´àµà´ªàµà´ªà´¿ à´±àµà´±àµà´±àµ à´à´³àµà´³à´¤àµ à´àµà´£àµà´àµ à´ à´à´°àµ à´«à´¯àµ½ 5 à´®à´¿à´¨à´¿à´±àµà´±àµ à´àµà´£àµà´àµ à´à´µà´¿à´àµ à´¨à´¿à´¨àµà´¨àµà´ à´¡à´¿à´²àµà´±àµà´±à´¾à´µàµà´...!!!\n\n\nà´à´µà´¿à´àµ à´¨à´¿à´¨àµà´¨àµà´ à´µàµà´±àµ à´à´µà´¿à´àµà´²àµà´ à´®à´¾à´±àµà´±à´¿à´¯à´¤à´¿à´¨àµ à´¶àµà´·à´ à´¡àµàµºà´²àµà´¡àµ à´àµà´¯àµà´¯àµà´...!!!\nFILES FORWARD TO YOUR SAVED MESSAGES\n\n\nAll files here Gets Deleted With in 5 Minutes\nâââââ á´á´ÉªÉ´ á´¡Éªá´Ê á´s ââââââ\n\nâ»ï¸ ðððð :- @nasrani_update\nâ»ï¸ ðððð :- @NasraniSeries\nâââââ á´á´ÉªÉ´ á´¡Éªá´Ê á´s ââââââ</b>\n',
                
                protect_content=True if ident == "filep" else False,

                reply_markup=InlineKeyboardMarkup(buttons)
                    
            )
            
            msg1 = await query.message.reply(

                f'<b> ððð² ð {query.from_user.mention} </b>ð\n\n<b>ð« ðð¨ð®ð« ðð¢ð¥ð ð¢ð¬ ððððð²\n\n ê°ÉªÊá´ê± Êá´Êá´ É¢á´á´ê± á´á´Êá´á´á´á´ á´¡Éªá´Ê ÉªÉ´ 5 á´ÉªÉ´á´á´á´ê± \n\ná´Êá´á´ê±á´ á´ÊÉªá´á´ á´Êá´ á´Éªá´á´Êá´ Êá´á´á´á´É´ á´É´á´ á´á´ÉªÉ´ á´Êá´ á´Êá´É´É´á´Ê á´á´ É¢á´á´ á´Êá´ á´á´á´ Éªá´. \n\n</b>'           

                f'<b>ð Má´á´ Éªá´ Ná´á´á´</b> : <code>{title}</code>\n\n'              

                f'<b>âï¸ Má´á´ Éªá´ SÉªá´¢á´</b> : <b>{size}</b>',

                True,

                'html',

                reply_markup=InlineKeyboardMarkup(

                    [
                        [
                            InlineKeyboardButton(f'ÉªÉ´Òá´', 'infos')
                        ],
                        [
                            InlineKeyboardButton("â ï¸ Can't Access â Click Here â ï¸", url=f'https://t.me/+h5G8KNeGhyI0NDI1')
                        ],                       
                        [
                            InlineKeyboardButton('ð¥ Download ð¥ ', url = msg.link)
                        ]
                    ]
                )
            )

            await query.answer('ð¥ð»ððâððð¸ð»ð¥',)
            await asyncio.sleep(120)
            await msg1.delete()
            await msg.delete()           
            del msg1, msg

        except Exception as e:

            logger.exception(e, exc_info=True)

            await query.answer(f"Encountering Issues", True)



    elif query.data.startswith("checksub"):

        if AUTH_CHANNEL and not await is_subscribed(client, query):

            await query.answer("I Like Your Smartness, But Don't Be Oversmart ð", show_alert=True)

            return

        ident, file_id = query.data.split("#")

        files_ = await get_file_details(file_id)

        if not files_:

            return await query.answer('No such file exist.')

        files = files_[0]

        title = files.file_name

        size = get_size(files.file_size)

        mention = query.from_user.mention

        f_caption = files.caption

        if CUSTOM_FILE_CAPTION:

            try:

                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,

                                                       file_size='' if size is None else size,

                                                       file_caption='' if f_caption is None else f_caption)

            except Exception as e:

                logger.exception(e)

                f_caption = f_caption

                size = size

                mention = mention

        if f_caption is None:

            f_caption = f"{title}"

        if size is None:

            size = f"{size}"

        if mention is None:

            mention = f"{mention}"



        buttons = [
            [
                InlineKeyboardButton('â­ï¸ Support', url='https://t.me/mazhatthullikal'),
                InlineKeyboardButton('Channel â­ï¸', url='https://t.me/mazhatthullikal')
            ],
            [
                InlineKeyboardButton('ð¬ Series & Movie Club ð¬', url=f'https://t.me/mazhatthullikal')
            ]
            ]
        await query.answer()

        await client.send_cached_media(

            chat_id=query.from_user.id,

            file_id=file_id,

            caption=f_caption,

            protect_content=True if ident == 'checksubp' else False

        )

    elif query.data == "pages":

        await query.answer()

    elif query.data == "start":

        buttons = [[

            InlineKeyboardButton('ðððð ðð ðð¨ ðð¨ð®ð« ðð«ð¨ð®ð©ð¬ð', url=f'http://t.me/{temp.U_NAME}?startgroup=true')

            ],[

            InlineKeyboardButton('ððððð«ðð¡ð', switch_inline_query_current_chat=''),

            InlineKeyboardButton('ð­ðð©ððð­ðð¬ð­', url='https://t.me/nasrani_update')

            ],[

            InlineKeyboardButton('ðµï¸ððð¥ð©ðµï¸', callback_data='page1'),

            InlineKeyboardButton('ðððð¨ð®ð­ð', callback_data='about')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â£â£"

        )

        await query.message.edit_text(

            text=script.MENU_TEXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),

            reply_markup=reply_markup,

            parse_mode='html'

        )
            

        await query.answer('Piracy Is Crime')

    elif query.data == "page1":

        buttons = [[

            InlineKeyboardButton('â©ðððððð', callback_data='admins'),
            InlineKeyboardButton('â©ðððððððð', callback_data='download'),
            InlineKeyboardButton('â©ððððððð', callback_data='convert')
            ],[
            InlineKeyboardButton('â©ðððððð', callback_data='search'),
            InlineKeyboardButton('â©ððððð', callback_data='stats'),   
            InlineKeyboardButton('â©ðððð', callback_data='user')
            ],[  
            InlineKeyboardButton('â©ððððððð', callback_data='sticker'),
            InlineKeyboardButton('â©ððððððð', callback_data='country'),
            InlineKeyboardButton('â©ððððð', callback_data='extra')
            ],[
            InlineKeyboardButton('â­ðððð', callback_data='start'),
            InlineKeyboardButton('â©ð-ððððð', callback_data='trans'),
            InlineKeyboardButton('âððððð', callback_data='page')            

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â¢â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£â£â£â£"

        )

        await query.message.edit_text(

            text=script.MENU_TEXT.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )


    elif query.data == "admins":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.ðððððð.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )

    elif query.data == "download":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.DOWN.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
    elif query.data == "convert":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ðððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.CONV.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )        
        
    elif query.data == "search":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )
    elif query.data == "trans":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ðððððððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.TRANS.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
     
    elif query.data == "sticker":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ðððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.STICKER.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
    elif query.data == "country":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ðððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.COUNTRY.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
    elif query.data == "extra":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ðððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.EXTRA.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )

    elif query.data == "user":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.USER.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )

    elif query.data == "download":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.DOWN.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
    elif query.data == "download":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.DOWN.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
    elif query.data == "download":

        buttons = [[
                                                                                  
            InlineKeyboardButton('â¬ððððððððâ¬', callback_data='start'),
            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1')

        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(

            text="â£â¢â¢"

        )

        await query.message.edit_text(

            text="â£â£â¢"

        )

        await query.message.edit_text(

            text="â£â£â£"

        )

        
        await query.message.edit_text(

            text=script.DOWN.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )
  
        await query.message.edit_text(

            text=script.SEARCH.format(query.from_user.mention),

            reply_markup=reply_markup,

            parse_mode='html'

        )                

    





        

        
        

    


    elif query.data == "stats":

        buttons = [[

            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1'),

            InlineKeyboardButton('â¬ðððððððâ¬', callback_data='rfrsh')

        ]]

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

            parse_mode='html'

        )

    elif query.data == "rfrsh":

        await query.answer("Fetching MongoDb DataBase")

        buttons = [[

            InlineKeyboardButton('â¬ððððâ¬', callback_data='page1'),

            InlineKeyboardButton('â¬ðððððððâ¬', callback_data='rfrsh')

        ]]

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

            parse_mode='html'

        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('â Yes' if settings["botpm"] else 'â No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('â Yes' if settings["file_secure"] else 'â No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('â Yes' if settings["imdb"] else 'â No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('â Yes' if settings["spell_check"] else 'â No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('â Yes' if settings["welcome"] else 'â No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer('Piracy Is Crime')
            

    elif query.data == "close":

        await query.message.delete()

    elif query.data == 'tips':

        await query.answer("=> Ask with correct spelling\n=> Don't ask movies those are not released in OTT Some Of Theatre Quality Availableð¤§\n=> For better results:\n\t\t\t\t\t\t- MovieName year\n\t\t\t\t\t\t- Eg: Kuruthi 2021", True)

    elif query.data == 'infos':

        await query.answer("â ï¸ Information â ï¸\n\nAfter 3 minutes this message will be automatically deleted\n\nIf you do not see the requested movie / series file, look at the next page\n\nâ¸á´á´á´ Éªá´s É¢Êá´á´á´", True)

    elif query.data == 'infoss':

        await query.answer("FILES FORWARD TO YOUR SAVED MESSAGES. All files here Gets Deleted With in 5 Minutes", True)

    
    elif query.data == 'inf':

        await query.answer("â ï¸ à´à´µà´¿à´àµ à´à´¨àµà´¨àµà´ à´¨àµà´àµà´à´£àµà´ à´à´£àµà´£à´¿ ", True)



    elif query.data == 'imdb':

        await query.answer("{search}", True)

    

    elif query.data == 'series':

        await query.answer("sá´ÊÉªá´s Êá´Ç«á´á´sá´ Òá´Êá´á´á´\n\nÉ¢á´ á´á´ É¢á´á´É¢Êá´ â  á´Êá´á´ sá´ÊÉªá´s É´á´á´á´ â  á´á´á´Ê á´á´ÊÊá´á´á´ É´á´á´á´ â  á´á´sá´á´ ÉªÉ´ á´ÊÉªs É¢Êá´á´á´\n\ná´xá´á´á´Êá´ : Alive á´Ê Alive S01E01\n\nð¯ á´á´É´á´ á´sá´ â  ':(!,./)\n\nâ¸á´á´á´ Éªá´s É¢Êá´á´á´", True)



    try: await query.answer('Piracy Is Crime') 

    except: pass





async def auto_filter(client, msg: pyrogram.types.Message, spoll=False):

    if not spoll:

        message = msg

        settings = await get_settings(message.chat.id)

        if message.text.startswith("/"): return  # ignore commands

        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):

            return

        
        if 0 < len(message.text) < 100:

            search = message.text

            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)

            if not files:

                if settings["spell_check"]:

                    return await advantage_spell_chok(msg)

                else:

                    return

        else:

            return

    else:


        settings = await get_settings(msg.message.chat.id)

        message = msg.message.reply_to_message  # msg will be callback query

        search, files, offset, total_results = spoll

    

    pre = 'filep' if settings['file_secure'] else 'file'

    pre = 'Chat' if settings['redirect_to'] == 'Chat' else pre



    if settings["button"]:

        btn = [

            [

                InlineKeyboardButton(

                    text=f"ð {file.file_name}ð ",

                    callback_data=f'{pre}#{file.file_id}#{msg.from_user.id if msg.from_user is not None else 0}',

                ),

                InlineKeyboardButton(

                    text=f"ð {get_size(file.file_size)}ð ",

                    callback_data=f'{pre}_#{file.file_id}#{msg.from_user.id if msg.from_user is not None else 0}',

                )

            ]

            for file in files

        ]

    else:

        btn = [

            [

                InlineKeyboardButton(

                        text=f"ð  [{get_size(file.file_size)}]ð {file.file_name}ð ", 

                        callback_data=f'{pre}#{file.file_id}#{msg.from_user.id if msg.from_user is not None else 0}'

                )

            ] 

            for file in files

        ]



    

    btn.insert(0,

        [

            InlineKeyboardButton(f'ð° {search} ð°', 'infoss'),

            

        ]

    )

    btn.insert(1,

        [

            InlineKeyboardButton(f'ð Files: {total_results}', 'dupe'),

            InlineKeyboardButton(f"ð­ {search} ð­",callback_data="pages")

        ]

    )

    btn.insert(14,

        [

            InlineKeyboardButton(f"ð{message.chat.title}ð",url="https://t.me/nasrani_update"),

            InlineKeyboardButton(f"ð¦{message.from_user.id}ð¦",url="tg://openmessage?user_id={user_id}")

        ]

    )

    
    

    
    m=await message.reply_sticker("CAACAgUAAx0CQTCW0gABB5EUYkx6-OZS7qCQC6kNGMagdQOqozoAAgQAA8EkMTGJ5R1uC7PIECME") 
    await asyncio.sleep(2)
    await m.delete()


    



    if offset != "":

        key = f"{message.chat.id}-{message.message_id}"

        BUTTONS[key] = search

        req = message.from_user.id if message.from_user else 0

        btn.append(

            [InlineKeyboardButton(text=f"ð 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),

             InlineKeyboardButton(text="â³ððððâ³", callback_data=f"next_{req}_{key}_{offset}")]

        )

    else:

        btn.append(

            [InlineKeyboardButton(text="â 1/1", callback_data="pages")]

        )


    


    





    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None

    TEMPLATE = settings['template']

    if imdb:

        cap = TEMPLATE.format(

            query=search,

            mention_bot=temp.MENTION,

            mention_user=message.from_user.mention if message.from_user else message.sender_chat.title,

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

        cap = f"ð®ââ {message.from_user.mention} É´á´á´Éªá´á´ :Éªðµ Êá´á´ á´á´ É´á´á´ sá´á´ á´Êá´ ðµÉªÊá´ð á´ðµ á´ÊÉªð á´á´á´ Éªá´ Êá´á´ á´ðá´á´á´ ðµá´Ê. Êá´á´á´ á´á´ É´á´ðá´ á´á´É¢á´ð\nÂ©ï¸ÖÖÕ¡ÉÊÉÉ É®Ê :{message.chat.title}"       

    if imdb and imdb.get('poster'):

        try:

            fmsg = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],

                                      reply_markup=InlineKeyboardMarkup(btn))

        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):

            pic = imdb.get('poster')

            poster = pic.replace('.jpg', "._V1_UX360.jpg")

            fmsg = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))

        except Exception as e:

            logger.exception(e)

            fmsg = await message.reply_photo(
                   caption=f"ð®ââ {message.from_user.mention} É´á´á´Éªá´á´ :Éªðµ Êá´á´ á´á´ É´á´á´ sá´á´ á´Êá´ ðµÉªÊá´ð á´ðµ á´ÊÉªð á´á´á´ Éªá´ Êá´á´ á´ðá´á´á´ ðµá´Ê. Êá´á´á´ á´á´ É´á´ðá´ á´á´É¢á´ð\nÂ©ï¸ÖÖÕ¡ÉÊÉÉ É®Ê :{message.chat.title}",
                   photo="https://telegra.ph/file/8a8ba3e824e1d2482253f.jpg",
                   parse_mode="html",
                   reply_markup=InlineKeyboardMarkup(btn))

    else:

        

        fmsg = await message.reply_photo(
               caption=f"ð®ââ {message.from_user.mention} É´á´á´Éªá´á´ :Éªðµ Êá´á´ á´á´ É´á´á´ sá´á´ á´Êá´ ðµÉªÊá´ð á´ðµ á´ÊÉªð á´á´á´ Éªá´ Êá´á´ á´ðá´á´á´ ðµá´Ê. Êá´á´á´ á´á´ É´á´ðá´ á´á´É¢á´ð\nÂ©ï¸ÖÖÕ¡ÉÊÉÉ É®Ê :{message.chat.title}",
               photo="https://telegra.ph/file/8a8ba3e824e1d2482253f.jpg",
               parse_mode="html",
               reply_markup=InlineKeyboardMarkup(btn))

    
 
    await asyncio.sleep(180)

    await fmsg.delete()


    buttons = [

            [

                InlineKeyboardButton(f"{message.from_user.first_name}", url=f"https://t.me/NasraniSeries"),

                InlineKeyboardButton('SUPPORT', url=f"https://t.me/NasraniChatGroup"),

            ]

            ]
    await message.reply_photo(
    photo=random.choice(SP),
    caption=f"âï¸ {message.from_user.mention} FÉªÊá´á´Ê Fá´Ê {search} CÊá´ê±á´á´ ðï¸",
    reply_markup=InlineKeyboardMarkup(buttons)
    )               
            

    



    if spoll:

        await msg.message.delete()





async def advantage_spell_chok(msg):

    query = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e)?(l)*(o)*|mal(ayalam)?|tamil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle)", "", msg.text, flags=re.IGNORECASE) # plis contribute some common words 

    query = query.strip() + " movie"

    g_s = await search_gagala(query)

    g_s += await search_gagala(msg.text)

    gs_parsed = []

    if not g_s:

        k = await msg.reply("à´¨à´¿à´àµà´àµ¾ à´àµà´¦à´¿à´àµà´àµà´¨àµà´¨ à´®àµà´µà´¿ à´à´¤à´¿à´²àµà´£àµà´àµà´¨àµà´¨àµ à´à´±à´ªàµà´ªàµ à´µà´°àµà´¤àµà´¤àµà´.")

        await asyncio.sleep(8)

        await k.delete()

        return

        await asyncio.sleep(8)

        await k.delete()

        return

    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE) # look for imdb / wiki results

    gs = list(filter(regex.match, g_s))

    gs_parsed = [re.sub(r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)', '', i, flags=re.IGNORECASE) for i in gs]

    if not gs_parsed:

        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*", re.IGNORECASE) # match something like Watch Niram | Amazon Prime 

        for mv in g_s:

            match  = reg.match(mv)

            if match:

                gs_parsed.append(match.group(1))

    user = msg.from_user.id if msg.from_user else 0

    movielist = []

    gs_parsed = list(dict.fromkeys(gs_parsed)) # removing duplicates https://stackoverflow.com/a/7961425

    if len(gs_parsed) > 3:

        gs_parsed = gs_parsed[:3]

    if gs_parsed:

        for mov in gs_parsed:

            imdb_s = await get_poster(mov.strip(), bulk=True) # searching each keyword in imdb

            if imdb_s:

                movielist +=[movie.get('title') for movie in imdb_s]

    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]

    movielist = list(dict.fromkeys(movielist)) # removing duplicates

    if not movielist:

          

        k = await msg.reply_video(

        video= "https://telegra.ph/file/ec5404d035924f1113d8d.mp4",

        caption=f"<b>ðHello:-à´¨à´¿à´àµà´àµ¾ à´àµà´¦à´¿à´àµà´ à´®àµà´µà´¿ à´µàµà´£à´®àµà´àµà´à´¿àµ½ à´®àµà´à´³à´¿à´²àµ à´µàµà´¡à´¿à´¯àµ à´à´£àµà´àµ à´à´¤àµ à´ªàµà´²àµ à´¸àµà´ªàµà´²àµà´²à´¿à´àµ à´¤àµà´±àµà´±à´¾à´¤àµ à´à´¯à´àµà´àµà´.ð</b>",

        parse_mode="html",

        reply_markup=InlineKeyboardMarkup(

                        [

                            [

                                InlineKeyboardButton('ðððð ðð ðð¨ ðð¨ð®ð« ðð«ð¨ð®ð©ð¬ð', url="http://t.me/nasrani_bot?startgroup=true")

                            ],

                            [

                                InlineKeyboardButton('ð§©ðð¨ð¨ð ð¥ðð§©', url=f"google.com/search?q={query.replace(' ','+')}"),

                                InlineKeyboardButton('âðð¦ððâ', url="https://imdb.com")

                            ]                            

                        ]

                    )

                )         

        



                            



        await asyncio.sleep(60)

        await k.delete()

        return

    SPELL_CHECK[msg.message_id] = movielist

    btn = [[

                InlineKeyboardButton(

                    text=movie.strip(),

                    callback_data=f"spolling#{user}#{k}",

                )

            ] for k, movie in enumerate(movielist)]    

    

    btn.append(

            [

                InlineKeyboardButton("ððð¥ð¨ð¬ðð", callback_data=f'spolling#{user}#close_spellcheck'),

                InlineKeyboardButton("song", url="https://imdb.com")       

            ],

        )

    btn.insert(0,

            [

                InlineKeyboardButton(f'ÉªÉ´Òá´', 'im'),

                InlineKeyboardButton(f'á´á´á´ Éªá´', 'movies'),

                InlineKeyboardButton(f'sá´ÊÉªá´s', 'series')

            ]

    )              

    k = await msg.reply_sticker("CAACAgUAAx0CQTCW0gABB5EUYkx6-OZS7qCQC6kNGMagdQOqozoAAgQAA8EkMTGJ5R1uC7PIECME") 

    await asyncio.sleep(1)

    await k.delete()

    k = await msg.reply_photo(

        photo= "https://telegra.ph/file/8a8ba3e824e1d2482253f.jpg",

        caption=f"<b>ðà´¹à´²àµ à´¨à´¿à´àµà´à´³àµà´àµ à´¸à´¿à´¨à´¿à´® à´à´¤à´¿à´²àµà´£àµà´àµà´¨àµà´¨àµ à´ªà´°à´¿à´¶àµà´§à´¿à´àµà´àµà´</b>",

        parse_mode="html",

        reply_markup=InlineKeyboardMarkup(btn))



    await asyncio.sleep(60)

    await k.delete()  

                 

    return k

                

async def manual_filters(client, message, text=False):

    group_id = message.chat.id

    name = text or message.text
    
    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id

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

                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)

                        else:

                            button = eval(btn)
                            buttons = [[

                                InlineKeyboardButton('ð¡ðºð¼ð', callback_data='help')

                            ]]

                            k = await client.send_message(                               

                                group_id,

                                reply_text,
                                
                                disable_web_page_preview=True,
                                

                                reply_markup=InlineKeyboardMarkup(button),

                                reply_to_message_id=reply_id

                            )
                            await asyncio.sleep(10)
                            await k.delete()      
                            
                            

                    elif btn == "[]":
                        buttons = [[

                            InlineKeyboardButton('ð¡ðºð¼ð', callback_data='help')

                        ]]

                        k = await client.send_cached_media(

                            group_id,

                            fileid,

                            caption= reply_text or "",
                            
                            
                            reply_to_message_id=reply_id

                        )

                        await asyncio.sleep(10)
                        await k.delete()                                                            
                    else:
                        button = eval(btn)
                        buttons = [[
                            InlineKeyboardButton('ð¡ðºð¼ð', callback_data='help')
                        ]]
                        k = await message.reply_cached_media(
                            
                            fileid,                                                        
                            caption= reply_text or "",
                            
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(10)
                        await k.delete()                          
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
