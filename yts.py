import requests
import json
from telebot import types
from constants import BASE_YTS_LIST, BASE_YTS_DETAILS, HEADERS


class YTS:
    def __init__(self, query):
        self.query = query.strip()
        self.matched = None
        self.swipe_markup = None
        self.current_index = 0
        self.max_index = 0
        self.files = None
        
    async def get_matched(self):
        r = requests.get(BASE_YTS_LIST + self.query)
        matched = {}
        parsed_json = json.loads(r.text)
        self.max_index = parsed_json['data']['movie_count']
        if self.max_index == 0:
            await self.get_swipe_markup()
            return
        movies = parsed_json['data']['movies']
        for i, movie in enumerate(movies):
            hours, minutes = divmod(movie['runtime'], 60)            
            matched[i] = [
                        movie['large_cover_image'],
                        f'{movie['title_long']}\n\n_{movie['summary']}_\n\nRuntime: {hours} hr, {minutes} min',
                        str(movie['id'])
                    ]
            
        self.matched = matched
        await self.get_swipe_markup()
        
        
    async def get_swipe_markup(self):
        markup = types.InlineKeyboardMarkup()
        if self.max_index == 0:
            markup.row(types.InlineKeyboardButton(text='No results found', callback_data='ignore'))
            markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
            self.swipe_markup = markup
            return
        if self.max_index > 1 and self.current_index < 1:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_yts'))
        elif self.current_index >= 1 and self.current_index < self.max_index - 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_yts'), types.InlineKeyboardButton(text='➡️', callback_data='r_yts'))
        elif self.current_index >= 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_yts'))
        markup.row(types.InlineKeyboardButton(text='Choose', callback_data='choose_yts'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='close_arrow'))
        self.swipe_markup = markup
        
        
    async def get_files(self):
        files = []
        r = requests.get(BASE_YTS_DETAILS + self.matched[self.current_index][2], headers=HEADERS)
        parsed_json = json.loads(r.text)
        torrents = parsed_json['data']['movie']['torrents']
        name = parsed_json['data']['movie']['title_long']
        for torrent in torrents:
            filename = f'{name} {torrent['quality']}{torrent['video_codec']} [{str.capitalize(torrent['type'])}].torrent'
            caption = f'Size: {torrent['size']}  Seeds/Peers: {str(torrent['seeds'])}/{str(torrent['peers'])}\n{torrent['quality']}{torrent['video_codec']} - [{str.capitalize(torrent['type'])}]\n\nHash: `{torrent['hash']}`'
            files.append((torrent['url'], filename, caption))
        self.files = files
        return files
        



    
