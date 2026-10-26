import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from datetime import datetime
from constants import API_KEY, CHATID, HEADERS

from messageContext import MessageContext
from genius import GeniusScraper, GeniusSong
from anghami import AnghamiScraper
from songtell import SongTellScraper
from almaany import AlmaanyScraper
from urban import UrbanScraper
from sp import get_data_sp
from onthisday import OTDScraper
from lrc import LrcScraper
from instagram import InstagramScraper
from yts import YTS
from openSubtitles import OSubs
from oceanofpdf import BookScraper

import requests
import re
import random

import collections
import collections.abc
import sys

import json

# from server import server
# server()

bot = AsyncTeleBot(API_KEY)

msg = {}

async def chat(message):
    userId = message.chat.id
    nameUser = str(message.chat.first_name) + ' ' + str(message.chat.last_name)
    username = message.chat.username
    text = message.text
    date = datetime.now()
    data = f'User id: {userId}\nUsername: @{username}\nName: {nameUser}\nText: {text}\nDate: {date}'
    await bot.send_message(chat_id=CHATID, text=data)

# --- General ---

@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    name = message.chat.first_name if message.chat.first_name != None else message.chat.username
    smsg = f"Hello {name}!\n\nBot commands:\n/start - Restarts the bot.\n/ly - Get songs lyrics.\n/from_lyric - Find songs using lyrics.\n/lrc - Find synced lyrics.\n/sp - أسعار العملات والذهب والكريبتو.\n/coin - flip a coin (syrian lira)\n/otd - On this day in history.\n/book - Get books (english only).\n/yts - Get movies torrent file.\n/subs - Get English subtitles files.\n/subs_ar - ملفات ترجمة أفلام ومسلسلات وأنمي.\n/maana - للبحث عن معنى كلمة عربية في المعجم.\n/slang - define slang word.\n/contact - Report a bug / Suggest a feature."
    await bot.reply_to(message, smsg)
    await chat(message)

@bot.message_handler(commands=['contact'])
async def contact(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    smsg = "Contact bot creator to report a bug or suggest a feature:\n@Absurduck\nhttps://t.me/Absurduck"
    await bot.reply_to(message, smsg, disable_web_page_preview=True)
    await chat(message)
    
# --- SP ---    
@bot.message_handler(commands=['sp'])
async def sp(message):
    await bot.send_chat_action(message.chat.id, action='typing')
    
    currencies, gold, crypto = await get_data_sp()
    smsg = ''
    for item in currencies.values():
        smsg += item
    for item in gold.values():
        smsg += item
    for item in crypto.values():
        smsg += item
    if smsg == '':
        smsg = 'Sorry, something went wrong.'
    await bot.reply_to(message, smsg, parse_mode='markdown')
    await chat(message)
    
# --- OTD ---    
@bot.message_handler(commands=['otd'])
async def otd(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    msg[message.chat.id].serched['otd'] = OTDScraper(message.chat.id)
    await msg[message.chat.id].serched['otd'].get_data_otd()
    smsg, src = msg[message.chat.id].serched['otd'].events[0]
    c_smsg =  f'{msg[message.chat.id].serched['otd'].current_index +1}/{msg[message.chat.id].serched['otd'].max_index} - ' + smsg
    await bot.send_photo(message.chat.id, src, caption=c_smsg, reply_markup= msg[message.chat.id].serched['otd'].swipe_markup, reply_to_message_id=message.message_id, parse_mode='markdown')
    await chat(message)
    
# --- BOOK ---    
@bot.message_handler(commands=['book'])
async def otd(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/book')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/book book name')
        return
    msg[message.chat.id].serched['book'] = BookScraper(message.text.removeprefix('/book'))
    await msg[message.chat.id].serched['book'].get_matched()
    title, image, _ = msg[message.chat.id].serched['book'].matched_books[0]
    await bot.send_photo(message.chat.id, image, caption=title, reply_markup= msg[message.chat.id].serched['book'].swipe_markup, reply_to_message_id=message.message_id)
    await chat(message)
    
# --- Lyricism ---

@bot.message_handler(commands=['ly'])
async def from_lyric(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(msg[message.chat.id].chat_id, action='typing')
    if len(message.text.removeprefix('/ly')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/ly song name artist name\nExample:\n/ly bloodhail have a nice life')
        return
    msg[message.chat.id].serched['genius'] = GeniusScraper(message.text.removeprefix('/ly '), 1, 'song')
    await bot.send_message(msg[message.chat.id].chat_id, 'Choose your song:', reply_markup= msg[message.chat.id].serched['genius'].songs_markup, reply_to_message_id=message.message_id)
    await chat(message)
    
@bot.message_handler(commands=['from_lyric'])
async def from_lyric(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(msg[message.chat.id].chat_id, action='typing')
    if len(message.text.removeprefix('/from_lyric')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/from_lyric {lyrics you remember}\nExample:\n/from_lyric someday I wanna lay down like god did on sunday')
        return
    msg[message.chat.id].serched['genius'] = GeniusScraper(message.text.removeprefix('/from_lyric '), 1, 'lyric')
    await bot.send_message(msg[message.chat.id].chat_id, 'Choose your song:', reply_markup= msg[message.chat.id].serched['genius'].songs_markup, reply_to_message_id=message.message_id)
    await chat(message)
    
# --- LRC ---

@bot.message_handler(commands=['lrc'])
async def from_lyric(message):
    # await bot.reply_to(message, 'Feature under maintenance.')
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/lrc')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/lrc song name')
        return
    msg[message.chat.id].serched['lrc'] = LrcScraper(message.text.removeprefix('/lrc '))
    await msg[message.chat.id].serched['lrc'].get_data_lrc()
    await bot.send_message(message.chat.id, 'Choose your song:', reply_markup=msg[message.chat.id].serched['lrc'].markup, reply_to_message_id=message.message_id)
    await chat(message)

# --- Almaany ----

@bot.message_handler(commands=['maana'])
async def reply(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/maana')) == 0:
        await bot.reply_to(message, 'لاستخدام الميزة:\n/maana كلمة')
        return
    msg[message.chat.id].serched['almaany'] = AlmaanyScraper(message.text.removeprefix('/maana '))
    await bot.send_message(message.chat.id, 'اختر الكلمة:', reply_markup=msg[message.chat.id].serched['almaany'].markup, reply_to_message_id=message.message_id)
    await chat(message)
    
    
# --- YTS ----

@bot.message_handler(commands=['yts'])
async def reply(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/yts')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/yts movie name')
        return
    msg[message.chat.id].serched['yts'] = YTS(message.text.removeprefix('/yts '))
    await msg[message.chat.id].serched['yts'].get_matched()
    if msg[message.chat.id].serched['yts'].max_index == 0:
        await bot.send_message(message.chat.id, ':)', reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id)
    else:
        await bot.send_photo(message.chat.id, msg[message.chat.id].serched['yts'].matched[0][0], caption=msg[message.chat.id].serched['yts'].matched[0][1], reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id, parse_mode='markdown')
    await chat(message)
    
# --- OPENSUBS ----

@bot.message_handler(commands=['subs'])
async def reply(message):
    await chat(message)
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/subs')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/subs movie name')
        return
    msg[message.chat.id].serched['subs'] = OSubs(message.text.removeprefix('/subs '))
    await msg[message.chat.id].serched['subs'].get_matched()
    if msg[message.chat.id].serched['subs'].markup == None:
        await bot.reply_to(message, 'Sorry, this feature is down for now.')
        return
    await bot.send_message(message.chat.id, 'Choose:', reply_to_message_id=message.message_id, reply_markup= msg[message.chat.id].serched['subs'].markup)
    # if msg[message.chat.id].serched['subs'].max_index == 0:
    #     await bot.send_message(message.chat.id, ':)', reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id)
    # else:
    #     await bot.send_photo(message.chat.id, msg[message.chat.id].serched['yts'].matched[0][0], caption=msg[message.chat.id].serched['yts'].matched[0][1], reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id, parse_mode='markdown')
    
@bot.message_handler(commands=['subs_ar'])
async def reply(message):
    await chat(message)
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/subs_ar')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/subs movie name')
        return
    msg[message.chat.id].serched['subs'] = OSubs(message.text.removeprefix('/subs_ar '), lang='ara')
    await msg[message.chat.id].serched['subs'].get_matched()
    if msg[message.chat.id].serched['subs'].markup == None:
        await bot.reply_to(message, 'Sorry, this feature is down for now.')
        return
    await bot.send_message(message.chat.id, 'Choose:', reply_to_message_id=message.message_id, reply_markup= msg[message.chat.id].serched['subs'].markup)
    # if msg[message.chat.id].serched['subs'].max_index == 0:
    #     await bot.send_message(message.chat.id, ':)', reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id)
    # else:
    #     await bot.send_photo(message.chat.id, msg[message.chat.id].serched['yts'].matched[0][0], caption=msg[message.chat.id].serched['yts'].matched[0][1], reply_markup= msg[message.chat.id].serched['yts'].swipe_markup, reply_to_message_id=message.message_id, parse_mode='markdown')
    
# --- Urban Dictionary ---
@bot.message_handler(commands=['slang'])
async def reply(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(message.chat.id, action='typing')
    if len(message.text.removeprefix('/slang')) == 0:
        await bot.reply_to(message, 'To use the feature:\n/slang word')
        return
    msg[message.chat.id].serched['urban'] = UrbanScraper(message.text.removeprefix('/slang '))
    if await msg[message.chat.id].serched['urban'].can_get_exact():
        msg[message.chat.id].serched['urban'].term = msg[message.chat.id].serched['urban'].query
        await msg[message.chat.id].serched['urban'].get_definitions()
        await bot.send_message(message.chat.id, msg[message.chat.id].serched['urban'].definitions[0], reply_to_message_id=message.message_id, parse_mode="markdown", reply_markup=msg[message.chat.id].serched['urban'].swipe_markup)
    else:
        await msg[message.chat.id].serched['urban'].get_api()
        await bot.send_message(message.chat.id, 'Choose your term:', reply_markup=msg[message.chat.id].serched['urban'].markup, reply_to_message_id=message.message_id)
    await chat(message)


# --- COIN ---
@bot.message_handler(commands=['coin'])
async def reply(message):
    choice = random.choice(['CAACAgQAAxkBAAEbQK1pl0hYJEcUQejZ9bOmN9xe-3v4VQACQxwAAjg6uVAYY_jA_CiWCjoE', 'CAACAgQAAxkBAAEbQK9pl0haCxizszuf6MD9zN0DGlTiyAAC6B0AAljBuFABj2KygAuJjzoE',
                            'CAACAgQAAxkBAAEbQPFpl00Rqhg0vmOChOeLRiEHfeMh_gACHB4AAvUPuVD1OdmKPo1rCzoE', 'CAACAgQAAxkBAAEbQPNpl00SBC_COsysEjrZiweHYzRhsAACEBwAAmsQuVB5lkV6gsAAAa46BA'
                            ])
    await bot.send_sticker(message.chat.id, choice, message.message_id)
    await chat(message)
    
    
@bot.message_handler(commands=None)
async def reply(message):
    if (message.chat.id not in msg.keys()):
        msg[message.chat.id] = MessageContext(message)
    await bot.send_chat_action(msg[message.chat.id].chat_id, action='typing')
    await chat(message)
    if 'instagram.com/' in message.text:
        msg[message.chat.id].serched['instagram'] = InstagramScraper()
        patterns = [r'(https://)?www\.instagram\.com/reel/.+/', r'(https://)?www\.instagram\.com/p/.+/', r'(https://)?www\.instagram\.com/(?!(reel|p))[^?]+']
        pattern_index = None
        for index, pattern in enumerate(patterns):
            link = re.match(pattern, message.text)
            if link:
                pattern_index = index
                break
        if not link:
            await bot.reply_to(message, "Invalid Instagram URL.")
            return
        if pattern_index == 0:
            url = msg[message.chat.id].serched['instagram'].get_info(link.group(0), pattern_index)
            try:
                await bot.send_video(message.chat.id, url, reply_to_message_id=message.message_id, supports_streaming=True)
            except:
                await bot.reply_to(message, 'Sorry, reel size exceeds Telegram\'s limit.')           
            return
        await bot.reply_to(message, "This type of Instagram content is _currently_ not supported for downloading.", parse_mode='markdown')
        return
    
    if 'reddit.com' in message.text:
        r = requests.get(message.text)
        rr = requests.get(r.url.split('?', 1)[0] + '.json', headers=HEADERS)
        loaded = json.loads(rr.content)
        data = loaded[0]['data']['children'][0]['data']
        if 'is_gallery' in data:
            if data['is_gallery'] == True:
                for id in data['gallery_data']['items']:
                    asyncio.sleep(0.5)
                    link = 'https://i.redd.it/' + id['media_id']
                    try:
                        await bot.send_photo(message.chat.id, link + '.jpg', reply_to_message_id=message.message_id)
                    except:
                        await bot.send_video(message.chat.id, link + '.gif', reply_to_message_id=message.message_id, supports_streaming=True)
                #     print(id['media_id'])
                # for id in data['media_metadata']:
                #     item = data['media_metadata'][id]
                #     link = item['o'][0]['u'].split('?', 1)[0].replace('preview', 'i')
                #     if item['e'] == 'Image':
                #         await bot.send_photo(message.chat.id, link, reply_to_message_id=message.message_id) 
                #     elif item['e'] == 'AnimatedImage':
                #         await bot.send_video(message.chat.id, link, reply_to_message_id=message.message_id, supports_streaming=True)

        elif 'post_hint' in data:
            if data['post_hint'] == 'hosted:video':
                await bot.send_video(message.chat.id, data['secure_media']['reddit_video']['fallback_url'], reply_to_message_id=message.message_id, supports_streaming=True)
            elif data['post_hint'] == 'rich:video':
                await bot.send_video(message.chat.id, data['preview']['reddit_video_preview']['fallback_url'], reply_to_message_id=message.message_id, supports_streaming=True)
            elif data['post_hint'] == 'image':
                await bot.send_photo(message.chat.id, data['url_overridden_by_dest'], reply_to_message_id=message.message_id) 
        return
    
    await bot.send_chat_action(message.chat.id, action='typing')
    name = message.chat.first_name if message.chat.first_name != None else message.chat.username
    smsg = f"Hello {name}!\n\nBot commands:\n/start - Restarts the bot.\n/ly - Get songs lyrics.\n/from_lyric - Find songs using lyrics.\n/lrc - Find synced lyrics.\n/sp - أسعار العملات والذهب والكريبتو.\n/coin - flip a coin (syrian lira)\n/otd - On this day in history.\n/book - Get books (english only).\n/yts - Get movies torrent file.\n/subs - Get English subtitles files.\n/subs_ar - ملفات ترجمة أفلام ومسلسلات وأنمي.\n/maana - للبحث عن معنى كلمة عربية في المعجم.\n/slang - define slang word.\n/contact - Report a bug / Suggest a feature."
    await bot.reply_to(message, smsg)
    return
    

    
@bot.callback_query_handler(func=lambda call: True)
async def callback_data(call):
    if call.message:
        
        # --- General ---
        if call.data == 'ignore': # clicking on 'no results found'
            await bot.answer_callback_query(callback_query_id=call.id, text="No results found.")

        if call.data == 'result_no':
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.reply_to_message.message_id)
            await bot.answer_callback_query(callback_query_id=call.id, text="Closed successfully.")
            
        if call.data == 'long_done':
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            
        if call.data == 'close_arrow':
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            await bot.answer_callback_query(callback_query_id=call.id, text="Closed successfully.")
            
        # --- Genius ---
        if call.data == 'right':
            msg[call.message.chat.id].serched['genius'].current_index += 5
            msg[call.message.chat.id].serched['genius'].get_songs_markup()
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['genius'].songs_markup)

        if call.data == 'left':
            msg[call.message.chat.id].serched['genius'].current_index -= 5
            msg[call.message.chat.id].serched['genius'].get_songs_markup()
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['genius'].songs_markup)
            
        if call.data.startswith('selected'):
            await bot.send_chat_action(call.message.chat.id, action='typing')
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            song_selected = call.data.removeprefix('selected')
            msg[call.message.chat.id].serched['genius_song'] = GeniusSong(msg[call.message.chat.id].serched['genius'].songs_matched[song_selected]) 
            lyrics = msg[call.message.chat.id].serched['genius_song'].title.split('-')[0].strip() + ' | Lyrics:\n\n' + msg[call.message.chat.id].serched['genius_song'].lyrics
            if len(lyrics) <= 1024: # media with caption (1024 telegram's limit)  
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['genius_song'].photo, caption=lyrics, reply_markup= msg[call.message.chat.id].serched['genius'].info_markup, reply_to_message_id=call.message.reply_to_message.message_id)
            elif len(lyrics) > 1024 and len(lyrics) <= 4096: # media alone, normal message (4096 telegram's limit)  
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['genius_song'].photo, reply_to_message_id=call.message.reply_to_message.message_id)
                await bot.send_message(call.message.chat.id, lyrics, reply_markup = msg[call.message.chat.id].serched['genius'].info_markup)
            elif len(lyrics) > 4096: # media alone
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['genius_song'].photo, reply_to_message_id=call.message.reply_to_message.message_id)
                for x in range(0, len(lyrics), 4096): # multiple messages for > 4096 (telegram's limit)
                    await bot.send_message(chat_id=call.message.chat.id, text=lyrics[x:x+4096])
                long_markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton(text='About the song', callback_data='info_about'),
                                                    types.InlineKeyboardButton(text='Album tracklist', callback_data='info_album')],
                                                    [types.InlineKeyboardButton(text='Done', callback_data='long_done')]])
                await bot.send_message(chat_id=call.message.chat.id, text="More stuff to see:\n\n", reply_markup=long_markup)
        
        if call.data == 'click_done':
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            await bot.answer_callback_query(callback_query_id=call.id, text="Closed successfully.")
        
        if call.data == 'info_about':
            await bot.send_chat_action(call.message.chat.id, action='typing')
            await bot.send_message(chat_id=call.message.chat.id, text='About the song:\n' + msg[call.message.chat.id].serched['genius_song'].about, reply_to_message_id=call.message.message_id)

        if call.data == 'info_album':
            await bot.send_chat_action(call.message.chat.id, action='typing')
            album_text, tracks = msg[call.message.chat.id].serched['genius_song'].album_name, msg[call.message.chat.id].serched['genius_song'].album_tracks
            markup = types.InlineKeyboardMarkup()
            for track in tracks.keys():
                markup.row(types.InlineKeyboardButton(text= tracks[track][0], callback_data='album' + track))
            markup.row(types.InlineKeyboardButton(text='Done', callback_data='click_done'))
            await bot.send_photo(chat_id=call.message.chat.id, photo=msg[call.message.chat.id].serched['genius_song'].album_photo, caption=album_text, reply_markup=markup, reply_to_message_id=call.message.message_id)
        

        if call.data == 'genius_search':
            await bot.edit_message_text('Choose your song:', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['genius'].songs_markup)
            
        if call.data.startswith('album'):
            await bot.answer_callback_query(callback_query_id=call.id, text="Feature under maintenance.")
        
        # --- Anghami ---
        if call.data == 'anghami_search':
            # if 'anghami' in msg[call.message.chat.id].serched:
            #     await bot.edit_message_text('اختر الأغنية:', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['anghami'].songs_markup)
            # else:
            msg[call.message.chat.id].serched['anghami'] = AnghamiScraper(call.message.reply_to_message.text.removeprefix('/ly '))
            await bot.edit_message_text('اختر الأغنية:', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['anghami'].songs_markup)

        if call.data.startswith('anghami_selected'):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_chat_action(call.message.chat.id, action='typing')
            song_selected = call.data.removeprefix('anghami_selected')
            msg[call.message.chat.id].serched['anghami'].get_data(song_selected)
            if len(msg[call.message.chat.id].serched['anghami'].lyrics) <= 1024:
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['anghami'].photo, caption=msg[call.message.chat.id].serched['anghami'].lyrics, reply_to_message_id=call.message.reply_to_message.message_id)
            elif len(msg[call.message.chat.id].serched['anghami'].lyrics) > 1024 and len(msg[call.message.chat.id].serched['anghami'].lyrics) <= 4096:
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['anghami'].photo, reply_to_message_id=call.message.reply_to_message.message_id)
                await bot.send_message(call.message.chat.id, msg[call.message.chat.id].serched['anghami'].lyrics)
            elif len(msg[call.message.chat.id].serched['anghami'].lyrics) > 4096:
                await bot.send_photo(call.message.chat.id, msg[call.message.chat.id].serched['anghami'].photo, reply_to_message_id=call.message.reply_to_message.message_id)
                for x in range(0, len(msg[call.message.chat.id].serched['anghami'].lyrics), 4096):
                    await bot.send_message(chat_id=call.message.chat.id, text=msg[call.message.chat.id].serched['anghami'].lyrics[x:x+4096])
                    
                    
        # --- Song Tell ---
        if call.data == 'st_search':
            # if 'songtell' in msg[call.message.chat.id].serched:
            #     await bot.edit_message_text('Choose your song:', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['songtell'].songs_markup)
            # else:
            msg[call.message.chat.id].serched['songtell'] = SongTellScraper(call.message.reply_to_message.text.removeprefix('/ly '))
            await msg[call.message.chat.id].serched['songtell'].get_songs()
            await bot.edit_message_text('Choose your song:', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['songtell'].songs_markup)
            
        if call.data.startswith('st_selected'):
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_chat_action(call.message.chat.id, action='typing')
            msg[call.message.chat.id].serched['songtell'].selected_song = call.data.removeprefix('st_selected')
            await msg[call.message.chat.id].serched['songtell'].get_meaning()
            await bot.send_message(call.message.chat.id, msg[call.message.chat.id].serched['songtell'].meaning, reply_to_message_id=call.message.reply_to_message.message_id, parse_mode='html')
            if msg[call.message.chat.id].serched['songtell'].meaning_cont:
                await bot.send_message(call.message.chat.id, msg[call.message.chat.id].serched['songtell'].meaning_cont, reply_to_message_id=call.message.reply_to_message.message_id, parse_mode='html')
            return
            if len(msg[call.message.chat.id].serched['songtell'].meaning) > 1024 and len(msg[call.message.chat.id].serched['songtell'].meaning) <= 4096:
                await bot.send_message(call.message.chat.id, msg[call.message.chat.id].serched['songtell'].meaning, reply_to_message_id=call.message.reply_to_message.message_id)
            elif len(msg[call.message.chat.id].serched['songtell'].meaning) > 4096:
                for x in range(0, len(msg[call.message.chat.id].serched['songtell'].meaning), 4096):
                    await bot.send_message(chat_id=call.message.chat.id, text=msg[call.message.chat.id].serched['songtell'].meaning[x:x+4096], reply_to_message_id=call.message.reply_to_message.message_id)
            
            
        # --- Almaany ---
        if call.data.startswith('Maany'):
            msg[call.message.chat.id].serched['almaany'].selected_word = call.data.removeprefix('Maany')
            msg[call.message.chat.id].serched['almaany'].get_maany()
            await msg[call.message.chat.id].serched['almaany'].get_five_and_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['almaany'].five_maany, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['almaany'].songs_markup)
            
        if call.data == 'r_maany':
            msg[call.message.chat.id].serched['almaany'].current_index += 5
            await msg[call.message.chat.id].serched['almaany'].get_five_and_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['almaany'].five_maany, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['almaany'].songs_markup)
                
        if call.data == 'l_maany':
            msg[call.message.chat.id].serched['almaany'].current_index -= 5
            await msg[call.message.chat.id].serched['almaany'].get_five_and_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['almaany'].five_maany, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['almaany'].songs_markup)
                
                
        # --- Urban Dictionary ---
        if call.data.startswith('urban'):
            await msg[call.message.chat.id].serched['urban'].set_term(int(call.data.removeprefix('urban')))
            await msg[call.message.chat.id].serched['urban'].get_definitions()
            await bot.edit_message_text(msg[call.message.chat.id].serched['urban'].definitions[0], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['urban'].swipe_markup, parse_mode='markdown')
        
        if call.data == 'r_urban':
            msg[call.message.chat.id].serched['urban'].current_index += 1
            await msg[call.message.chat.id].serched['urban'].get_swipe_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['urban'].definitions[msg[call.message.chat.id].serched['urban'].current_index], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['urban'].swipe_markup, parse_mode='markdown')

        if call.data == 'l_urban':
            msg[call.message.chat.id].serched['urban'].current_index -= 1
            await msg[call.message.chat.id].serched['urban'].get_swipe_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['urban'].definitions[msg[call.message.chat.id].serched['urban'].current_index], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['urban'].swipe_markup, parse_mode='markdown')
    
    
        # --- OTD ---
        if call.data == 'r_otd':
            msg[call.message.chat.id].serched['otd'].current_index += 1
            smsg, src = msg[call.message.chat.id].serched['otd'].events[msg[call.message.chat.id].serched['otd'].current_index]
            c_smsg =  f'{msg[call.message.chat.id].serched['otd'].current_index +1}/{msg[call.message.chat.id].serched['otd'].max_index} - ' + smsg
            await msg[call.message.chat.id].serched['otd'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(src), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(c_smsg, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['otd'].swipe_markup, parse_mode='markdown')

        if call.data == 'l_otd':
            msg[call.message.chat.id].serched['otd'].current_index -= 1
            smsg, src = msg[call.message.chat.id].serched['otd'].events[msg[call.message.chat.id].serched['otd'].current_index]
            c_smsg =  f'{msg[call.message.chat.id].serched['otd'].current_index +1}/{msg[call.message.chat.id].serched['otd'].max_index} - ' + smsg
            await msg[call.message.chat.id].serched['otd'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(src), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(c_smsg, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['otd'].swipe_markup, parse_mode='markdown')
            
        # --- BOOKS ---
        if call.data == 'r_book':
            msg[call.message.chat.id].serched['book'].current_index += 1
            title, image, _ = msg[call.message.chat.id].serched['book'].matched_books[msg[call.message.chat.id].serched['book'].current_index]
            await msg[call.message.chat.id].serched['book'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(image), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(title, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['book'].swipe_markup)

        if call.data == 'l_book':
            msg[call.message.chat.id].serched['book'].current_index -= 1
            title, image, _ = msg[call.message.chat.id].serched['book'].matched_books[msg[call.message.chat.id].serched['book'].current_index]
            await msg[call.message.chat.id].serched['book'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(image), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(title, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['book'].swipe_markup)
        
        if call.data == 'book_choose':
            await bot.send_chat_action(call.message.chat.id, 'upload_document')
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            files = await msg[call.message.chat.id].serched['book'].get_book()
            for file in files:
                try:
                    await bot.send_document(call.message.chat.id, file, reply_to_message_id=call.message.reply_to_message.message_id)
                except:
                    await bot.send_chat_action(call.message.chat.id, 'upload_document')
                    r = msg[call.message.chat.id].serched['book'].scraper.get(file, stream=True, timeout=120)
                    await bot.send_document(call.message.chat.id, r.raw, visible_file_name=file.split('.com/')[-1].split('?')[0], reply_to_message_id=call.message.reply_to_message.message_id, timeout=120)
        
        # --- YTS ---
        if call.data == 'r_yts':
            msg[call.message.chat.id].serched['yts'].current_index += 1
            src, smsg, _ = msg[call.message.chat.id].serched['yts'].matched[msg[call.message.chat.id].serched['yts'].current_index]
            # c_smsg =  f'{msg[call.message.chat.id].serched['yts'].current_index +1}/{msg[call.message.chat.id].serched['yts'].max_index} - ' + smsg
            await msg[call.message.chat.id].serched['yts'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(src), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(smsg, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['yts'].swipe_markup, parse_mode='markdown')

        if call.data == 'l_yts':
            msg[call.message.chat.id].serched['yts'].current_index -= 1
            src, smsg, _ = msg[call.message.chat.id].serched['yts'].matched[msg[call.message.chat.id].serched['yts'].current_index]
            # c_smsg =  f'{msg[call.message.chat.id].serched['yts'].current_index +1}/{msg[call.message.chat.id].serched['yts'].max_index} - ' + smsg
            await msg[call.message.chat.id].serched['yts'].get_swipe_markup()
            await bot.edit_message_media(types.InputMediaPhoto(src), call.message.chat.id, call.message.message_id)
            await bot.edit_message_caption(smsg, call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['yts'].swipe_markup, parse_mode='markdown')

        if call.data == 'choose_yts':
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            await bot.send_chat_action(call.message.chat.id, 'upload_document')
            files = await msg[call.message.chat.id].serched['yts'].get_files()
            for file in files:
                link, filename, caption = file
                r = requests.get(link, stream=True)
                await bot.send_document(call.message.chat.id, r.raw, caption=caption, visible_file_name=filename, parse_mode='markdown')
        
        # --- OPENSUBS ---
        if call.data.startswith('subs'):
            msg[call.message.chat.id].serched['subs'].selected_index = int(call.data.removeprefix('subs'))
            if msg[call.message.chat.id].serched['subs'].matched[0][2] == 'movie':
                await msg[call.message.chat.id].serched['subs'].get_files()
                await bot.edit_message_text(msg[call.message.chat.id].serched['subs'].files[0][0], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['subs'].swipe_markup)
            if msg[call.message.chat.id].serched['subs'].matched[0][2] == 'tv':
                await msg[call.message.chat.id].serched['subs'].get_seasons()
                await bot.edit_message_text('Choose:\n(if no subs in season, try the unclassified)', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['subs'].seasons_markup)
            return 
        
        if call.data.startswith('season_subs'):
            if not msg[call.message.chat.id].user_free:
                await bot.answer_callback_query(callback_query_id=call.id, text="Please wait till your process is finished.")
                return
            msg[call.message.chat.id].serched['subs'].selected_season = int(call.data.removeprefix('season_subs'))
            #await bot.edit_message_text(msg[call.message.chat.id].serched['subs'].seasons_names[msg[call.message.chat.id].serched['subs'].selected_season], call.message.chat.id, call.message.message_id, reply_markup=await msg[call.message.chat.id].serched['subs'].get_season_markup())
            msg[call.message.chat.id].user_free = False
            try: 
                for episode in msg[call.message.chat.id].serched['subs'].seasons[msg[call.message.chat.id].serched['subs'].selected_season]:
                    await bot.send_chat_action(call.message.chat.id, 'upload_document')
                    name, caption, url = episode
                    if url == None:
                        await asyncio.sleep(0.5)
                        await bot.send_message(call.message.chat.id, name + caption, reply_to_message_id=call.message.reply_to_message.message_id)
                    else:
                        try: 
                            await bot.send_document(call.message.chat.id, url, call.message.reply_to_message.message_id, caption=caption, visible_file_name=name+'.zip')
                        except:
                            r = msg[call.message.chat.id].serched['subs'].sess.get(url, stream=True)
                            if 'Making sure you\'re not a bot!' in r.text or 'CAPTCHA robot test' in r.text:
                                await bot.send_message(call.message.chat.id, name + 'Sorry couldn\'t download the file, please report this to bot creator!', reply_to_message_id=call.message.reply_to_message.message_id)
                            else:

                                await bot.send_document(call.message.chat.id, r.raw, call.message.reply_to_message.message_id, caption=caption, visible_file_name=name+'.zip')
                await bot.send_message(call.message.chat.id, 'Done!')
            finally:
                msg[call.message.chat.id].user_free = True
                return
            
        # if call.data.startswith('ep_subs'):
        #     msg[call.message.chat.id].serched['subs'].selected_episode = int(call.data.removeprefix('ep_subs'))
        #     name, caption, url = msg[call.message.chat.id].serched['subs'].seasons[msg[call.message.chat.id].serched['subs'].selected_season][msg[call.message.chat.id].serched['subs'].selected_episode]
        #     if url == None:
        #         await bot.send_message(call.message.chat.id, name + caption, reply_to_message_id=call.message.reply_to_message.message_id)
        #     else:
        #         r = requests.get(url, stream=True)
        #         await bot.send_document(call.message.chat.id, r.raw, call.message.reply_to_message.message_id, caption=caption, visible_file_name=name+'.zip')
        
        # if call.data == 'back_to_seasons':
        #     await bot.edit_message_text('Choose:\n(if no subs in season, try the unclassified)', call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['subs'].seasons_markup)
        
        if call.data == 'r_subs':
            msg[call.message.chat.id].serched['subs'].current_index += 1
            await msg[call.message.chat.id].serched['subs'].get_swipe_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['subs'].files[msg[call.message.chat.id].serched['subs'].current_index][0], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['subs'].swipe_markup)

        if call.data == 'l_subs':
            msg[call.message.chat.id].serched['subs'].current_index -= 1
            await msg[call.message.chat.id].serched['subs'].get_swipe_markup()
            await bot.edit_message_text(msg[call.message.chat.id].serched['subs'].files[msg[call.message.chat.id].serched['subs'].current_index][0], call.message.chat.id, call.message.message_id, reply_markup=msg[call.message.chat.id].serched['subs'].swipe_markup)
        
        if call.data == 'get_subs':
            caption, url1, url2 = msg[call.message.chat.id].serched['subs'].files[msg[call.message.chat.id].serched['subs'].current_index]
            # r = requests.get(url, stream=True, headers={})
            try:
                await bot.send_document(call.message.chat.id, url1, call.message.reply_to_message.message_id, caption=caption)
            except:
                await bot.send_document(call.message.chat.id, url2, call.message.reply_to_message.message_id, caption=caption)
            return
        
        # --- LRC ---
        if call.data.startswith('lrc'):
            await bot.send_chat_action(call.message.chat.id, "typing")
            msg[call.message.chat.id].serched['lrc'].selected_lrc_index = int(call.data.removeprefix('lrc'))
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            lrc =  f'{msg[call.message.chat.id].serched['lrc'].songs_matched[msg[call.message.chat.id].serched['lrc'].selected_lrc_index][0]} | Synced Lyrics\n\n{msg[call.message.chat.id].serched['lrc'].songs_matched[msg[call.message.chat.id].serched['lrc'].selected_lrc_index][1]}'
            normal =  f'{msg[call.message.chat.id].serched['lrc'].songs_matched[msg[call.message.chat.id].serched['lrc'].selected_lrc_index][0]} | Lyrics\n\n{msg[call.message.chat.id].serched['lrc'].songs_matched[msg[call.message.chat.id].serched['lrc'].selected_lrc_index][2]}'
            await bot.send_message(call.message.chat.id, lrc, reply_to_message_id=call.message.reply_to_message.message_id)
            await bot.send_message(call.message.chat.id, normal, reply_to_message_id=call.message.reply_to_message.message_id)

while True:
    try:
        asyncio.run(bot.get_me())
        print(f'{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}, Bot is running...')
        asyncio.run(bot.infinity_polling(timeout=60, request_timeout=60))
    except Exception as e:
        asyncio.run(bot.get_me())
        print(f'{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}, An error occurred. Restarting bot...')
        asyncio.sleep(1)