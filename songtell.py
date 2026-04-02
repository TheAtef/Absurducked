from telebot import types
from constants import BASE_SONGTELL, HEADERS
import requests
import json
from bs4 import BeautifulSoup as bs
import re

class SongTellScraper:
    def __init__(self, query):
        self.query = query.strip()
        self.selected_song = 0
        self.songs_matched = None
        self.songs_markup = None
        self.meaning = 'Sorry, we don\'t have the meaning for this song yet.'
        self.meaning_cont = ''
        
    async def get_songs(self):
        songs_matched = {}
        counter = 1
        markup = types.InlineKeyboardMarkup()
        url = BASE_SONGTELL + 'search.json?q=' +self.query
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            try:
                parsed_json = json.loads(r.text)
                for song in parsed_json['pageProps']['searchResults']:
                    title = song['full_title'].replace('by', '-').strip()
                    songs_matched[str(counter)] = [title, song['artist_names'], song['title'], song['id'], song['artist_slug'], song['song_slug']]
                    counter += 1
                for key in list(songs_matched.keys()):
                    markup.row(types.InlineKeyboardButton(text=songs_matched[key][0], callback_data='st_selected' + key))
            except:
                pass
        self.songs_matched = songs_matched
        if counter - 1 == 0:
            markup.row(types.InlineKeyboardButton(text='No results found', callback_data='ignore')) 
        markup.row(types.InlineKeyboardButton(text='Genius ☑️', callback_data='genius_search'),
                    types.InlineKeyboardButton(text='أنغامي ☑️', callback_data='ar_search'))
        markup.row(types.InlineKeyboardButton(text='Songtell ✅ (For songs meanings!)', callback_data='st_search'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
        self.songs_markup = markup

    async def get_meaning(self):
        url = f'{BASE_SONGTELL}{self.songs_matched[self.selected_song][4]}/{self.songs_matched[self.selected_song][5]}.json'
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            parsed_json = json.loads(r.text)
            if 'needsGeneration' in parsed_json['pageProps']:
                if parsed_json['pageProps']['needsGeneration'] == 'true':
                    return
            else:
                if parsed_json['pageProps']['meaningJson']:
                    meaningJson = parsed_json['pageProps']['meaningJson']
                    introduction = '<u>Introduction:</u>\n' + meaningJson['introduction'] + '\n\n' if meaningJson['introduction'] != '' else ''
                    quickSummary = '<u>Quick Summary:</u>\n' + meaningJson['quickSummary'] + '\n\n' if meaningJson['quickSummary'] != '' else ''
                    inDepthLyricsAnalysis = '<u>In Depth Lyrics Analysis:</u>\n' + meaningJson['inDepthLyricsAnalysis'] + '\n\n' if meaningJson['inDepthLyricsAnalysis'] != '' else ''
                    culturalAndHistoricalContext = '<u>Cultural And Historical Context:</u>\n' + meaningJson['culturalAndHistoricalContext'] + '\n\n' if meaningJson['culturalAndHistoricalContext'] != '' else ''
                    receptionAndSignificance = '<u>Reception And Significance:</u>\n' + meaningJson['receptionAndSignificance'] + '\n\n' if meaningJson['receptionAndSignificance'] != '' else ''
                    conclusion = '<u>Conclusion:</u>\n' + meaningJson['conclusion'] + '\n\n' if meaningJson['conclusion'] != '' else ''
                    faqs = '<u>FAQs:</u>\n' if len(meaningJson['FAQs']) > 0 else ''
                    for faq in meaningJson['FAQs']:
                        faqs += f'- {faq['question']}\n{faq['answer']}\n\n'
                    meaning = introduction + quickSummary + inDepthLyricsAnalysis
                    meaning_cont = culturalAndHistoricalContext + receptionAndSignificance + conclusion + faqs
                    self.meaning = meaning.strip()
                    self.meaning_cont = meaning_cont.strip()
                else:
                    self.meaning = parsed_json['pageProps']['meaning']
                    
                    


        
        # url = f'https://songtell.com/{self.songs_matched[self.selected_song][4]}/{self.songs_matched[self.selected_song][5]}'
        # r = requests.get(url, headers=HEADERS)
        # if r.status_code == 200:
        #     soup = bs(r.content, features='lxml')
        #     meaning = 'No meaning found.'
        #     try:
        #         meaning_raw = soup.find("div", id="article")
        #         meaning_fixed = str(meaning_raw).replace('</p>', '\n\n').replace('</dt>', '\n')
        #         convert = bs(meaning_fixed, features='lxml')
        #         meaning = convert.text                    
        #     except:
        #         pass
            
        #     self.meaning = meaning