import cloudscraper
import json
from constants import BASE_GENIUS, HEADERS
from telebot import types
import re
from bs4 import BeautifulSoup as bs

class GeniusScraper:
    def __init__(self, query, num_pages, branch):
        self.query = query
        self.scraper = cloudscraper.create_scraper()
        self.num_pages = num_pages
        self.branch = branch
        self.current_index = 0
        self.songs_matched = self.get_songs()
        self.songs_markup = None
        self.info_markup = self.get_info_markup()
        self.get_songs_markup()
        
    def get_songs(self):
        songs_matched = {}
        counter = 1
        with self.scraper as s:
            for page in range(1, self.num_pages + 1): # 10 songs per page
                url = f'{BASE_GENIUS}/{self.branch}?page={page}&q={self.query.strip()}'
                r = s.get(url, headers=HEADERS)
                if r.status_code == 200:
                    parsed_json = json.loads(r.text)
                    for hit in parsed_json['response']['sections'][0]['hits']:
                        #number: [full_title, link, photo, album_photo, id]
                        songs_matched[str(counter)] = [
                                            hit['result']['full_title'].replace('by', '-'),
                                            hit['result']['url'],
                                            hit['result']['song_art_image_url'],
                                            hit['result']['header_image_url'],
                                            hit['result']['id']
                                            ]
                        counter += 1
        return songs_matched

    def get_songs_markup(self):
        markup = types.InlineKeyboardMarkup()
        for key in list(self.songs_matched.keys())[self.current_index:self.current_index+5]:
            markup.row(types.InlineKeyboardButton(text=self.songs_matched[key][0], callback_data='selected' + key))
        if len(self.songs_matched.keys()) > 5 and self.current_index < 5:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='right'))
        elif self.current_index >= 5 and self.current_index < len(self.songs_matched.keys()) - 5:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='left'), types.InlineKeyboardButton(text='➡️', callback_data='right'))
        elif len(self.songs_matched.keys()) != 0 and self.current_index >= 5:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='left'))
        if len(self.songs_matched.keys()) == 0:
            markup.row(types.InlineKeyboardButton(text='No results found', callback_data='ignore')) 
        if self.branch == 'song':
            markup.row(types.InlineKeyboardButton(text='Genius ✅', callback_data='genius_search'),
                        types.InlineKeyboardButton(text='أنغامي ☑️', callback_data='anghami_search'))
            markup.row(types.InlineKeyboardButton(text='Songtell ☑️ (For songs meanings!)', callback_data='st_search'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
        self.songs_markup = markup
    
    def get_info_markup(self):
        markup = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton(text='About the song', callback_data='info_about'),
             types.InlineKeyboardButton(text='Album tracklist', callback_data='info_album'),
            ],
            [types.InlineKeyboardButton(text='Done', callback_data='click_done')]
            ])
        return markup
    
    
class GeniusSong:
    def __init__(self, song_info): # [full_title, link, photo, album_photo, id]
        self.title, self.link, self.photo, self.album_photo, self.id = song_info
        self.scraper = cloudscraper.create_scraper()
        self.lyrics = None
        self.about = None
        self.album_name = None
        self.album_tracks = {}
        self.get_song()
        
    def get_song(self):
        r = self.scraper.get(self.link, headers=HEADERS)
        if r.status_code == 200:
            # get lyrics
            soup = bs(r.content, features='lxml')
            try:
                lyrics_raw = soup.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
                lyrics_raw.find("div", class_=re.compile("^LyricsHeader")).decompose()
                lyrics_raw.find("div", class_=re.compile("^LyricsFooter__Container")).decompose()
                lyrics_raw.find("div", class_=re.compile("^RightSidebar__Container")).decompose()
            except:
                pass
            if lyrics_raw == None:
                lyrics_raw = soup.find('div', class_=re.compile("^LyricsPlaceholder__Message")) # instrumental
            lyrics_fixed = str(lyrics_raw).replace('<br/>', '\n')
            convert = bs(lyrics_fixed, features='lxml')
            lyrics = convert.text # final lyrics
            self.lyrics = lyrics
        
            # get about
            about  = 'Sorry, couldn\'t find data.'
            try:
                about = soup.find('div', class_= re.compile("^SongDescription__Content")).get_text()
            except:
                pass
            self.about = about
        
            # get album
            tracks = {}
            album_name = 'Sorry, couldn\'t find data.'
            try:
                album_name = soup.find('a', class_=re.compile("^PrimaryAlbum__Title")).get_text()
            except:
                pass
            try:
                album_tracks = soup.find('ol', class_= re.compile("^AlbumTracklist__Container"))
                if album_tracks != None:
                    for i, li in enumerate(soup.find_all('li', class_=re.compile("^AlbumTracklist__Track"))):
                        x = li.get_text()
                        if re.search("\d", x) == None:
                            li.decompose()
                        if li.div.a != None:
                            #Number : [name, link]
                            tracks[str(i)] = [li.div.get_text(), li.div.a['href']]
                        else:
                            tracks[str(i)] = [li.div.get_text(), self.link]
            except:
                pass
            
            self.album_name = album_name
            self.album_tracks = tracks
        