import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from telebot import types
from constants import BASE_LRC, HEADERS


class LrcScraper:
    def __init__(self, query):
        self.query = query.strip()
        self.songs_matched = {}
        self.markup = None
        self.selected_lrc_index = 0

    async def get_data_lrc(self):
        counter = 0
        
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            allowed_methods=["GET"] 
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        https = requests.Session()
        https.mount("https://", adapter)
        
        try:
            r = https.get(BASE_LRC + self.query, headers=HEADERS, timeout=60)
            if r.status_code == 200:
                parsed_json = json.loads(r.text)
                for song in parsed_json:
                    #number: [full_title, syncedLyrics, plainLyrics]
                    self.songs_matched[counter] = [
                                        f'{song['trackName']} - {song['artistName']}',
                                        song['syncedLyrics'],
                                        song['plainLyrics'],
                                        ]
                    counter += 1
        except Exception as e:
            print(f"Request failed: {e}")
            
        await self.get_markup()
            
    async def get_markup(self):
        markup = types.InlineKeyboardMarkup()
        if len(self.songs_matched.keys()) == 0:
            markup.add(types.InlineKeyboardButton(text='No resluts found', callback_data='ignore'), row_width=8)
        else:
            for key in list(self.songs_matched.keys()):
                markup.row(types.InlineKeyboardButton(text=self.songs_matched[key][0], callback_data='lrc' + str(key)))
        markup.add(types.InlineKeyboardButton(text='Close', callback_data='result_no'), row_width=8)
        self.markup = markup

        