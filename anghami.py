import cloudscraper
import requests
import re
from bs4 import BeautifulSoup as bs
import json
from telebot import types
from constants import BASE_ANGHAMI, HEADERS


class AnghamiScraper:
    def __init__(self, query):
        self.query = query
        self.songs_matched = {}
        self.songs_markup = self.get_songs()
        self.lyrics = None
        self.photo = None
        
    def get_songs(self):
        scraper = cloudscraper.create_scraper()
        songs_matched = {}
        counter = 1
        markup = types.InlineKeyboardMarkup()
        url = BASE_ANGHAMI + self.query.strip()
        r = scraper.get(url)
        if r.status_code == 200:
            parsed_json = json.loads(r.text)
            for song in parsed_json['sections'][0]['data']:
                if 'lyrics' in song and 'languageid' in song:
                    if song['lyrics'] == 1 and song['languageid'] == 1:
                        songs_matched[str(counter)] = [song['id'],  song['coverArt'], song['title'] + ' - ' + song['artist']]
                        counter += 1
            for key in list(songs_matched.keys()):
                markup.row(types.InlineKeyboardButton(text=songs_matched[key][2], callback_data='anghami_selected' + key))
        self.songs_matched = songs_matched
        if counter - 1 == 0:
            markup.row(types.InlineKeyboardButton(text='لم يتم العثور على نتائج', callback_data='ignore')) 
        markup.row(types.InlineKeyboardButton(text='Genius ☑️', callback_data='genius_search'),
                    types.InlineKeyboardButton(text='أنغامي ✅', callback_data='anghami_search'))
        markup.row(types.InlineKeyboardButton(text='Songtell ☑️ (For songs meanings!)', callback_data='st_search'))
        markup.row(types.InlineKeyboardButton(text='إغلاق', callback_data='result_no'))
        return markup
    
    def get_data(self, song_selected):
        photo_url = 'https://angartwork.anghcdn.co/?id=' + str(self.songs_matched[song_selected][1])
        lyrics_url = 'https://kalimat.anghami.com/lyrics/' + str(self.songs_matched[song_selected][0])
        r = requests.get(lyrics_url, headers=HEADERS)
        if r.status_code == 200:
            soup_ar = bs(r.content, 'lxml')
        try:
            lyrics = self.songs_matched[song_selected][2].split('-')[0].strip() + ' | كلمات:\n\n' + soup_ar.find('pre', class_=re.compile("^lyrics-body")).text
        except AttributeError:
            lyrics = self.songs_matched[song_selected][2].split('-')[0].strip() + ' | كلمات:\n\n' + soup_ar.find('h4', class_=re.compile("^error-page")).text
        
        self.lyrics = lyrics
        self.photo = photo_url
