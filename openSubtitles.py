import requests
from bs4 import BeautifulSoup as bs
import re
import json
from telebot import types
from constants import BASE_OSUBS, BASE_OSUBS_FILES, BASE_OSUBS_TV, HEADERS_OS
from anubis_solver import solve_anubis_challenge
from requests.utils import add_dict_to_cookiejar

class OSubs:
    def __init__(self, query, lang='eng'):
        self.query = query
        self.sess = None
        self.matched = {}
        self.markup = None
        self.selected_index = 0 # first markup
        self.files = {}
        self.swipe_markup = None
        self.current_index = 0 # second markup
        self.max_index = 0 # second markup
        self.seasons = []
        self.seasons_names = []
        self.seasons_markup = None
        self.selected_season = 0
        self.lang = lang # eng, ara
        
        
    async def get_matched(self):
        self.matched = {}
        self.sess = requests.Session()     
        resp = self.sess.get('https://www.opensubtitles.org', timeout=10, allow_redirects=True)
        cookies = solve_anubis_challenge(self.sess, resp.url)
        add_dict_to_cookiejar(self.sess.cookies, cookies)
        
        r = self.sess.get(BASE_OSUBS + self.query, headers=HEADERS_OS)
        parsed_json = json.loads(r.text)
        for i, title in enumerate(parsed_json):
            if int(title['total']) > 0:
                self.matched[i] = [
                                    f'{title['name']} ({title['year']})',
                                    str(title['id']),
                                    title['kind']
                                ]
                
        markup = types.InlineKeyboardMarkup()
        for i, match in enumerate(self.matched.values()):
            markup.add(types.InlineKeyboardButton(text=match[0], callback_data='subs' + str(i)))
        markup.add(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
        self.markup = markup

    async def get_files(self):
        self.files = {}
        r = self.sess.get(BASE_OSUBS_FILES + self.lang + '/idmovie-' + self.matched[self.selected_index][1] + '/sort-7/asc-0')
        # print(r.url)
        soup = bs(r.content, 'lxml')
        table = soup.find('table', id='search_results')
        rows = table.find_all('tr', id=re.compile('^name'))
        counter = 0
        for row in rows:
            cells = row.find_all('td')
            name = row.span.get('title')
            if name == None:
                name = row.br.next_sibling.text
            if name == '':
                continue
            self.files[counter] = [
                            f'{name}\n\nDownloaded: {cells[4].a.text.replace('x', '')}\nRating: {cells[5].text} ({cells[5].span.get('title')})',
                            'https://www.opensubtitles.org/en/subtitleserve/sub/' + cells[4].a.get('href').split('/')[-1],
                            'https://dl.opensubtitles.org/en/download/sub/' + cells[4].a.get('href').split('/')[-1] + '.zip',
                        ]
            counter += 1
        self.max_index = len(self.files.keys())
        await self.get_swipe_markup()
        
        
    async def get_seasons(self):
        self.files = {}
        r = self.sess.get(BASE_OSUBS_FILES + self.lang + '/idmovie-' + self.matched[self.selected_index][1])
        soup = bs(r.content, 'lxml')
        table = soup.find('table', id='search_results')
        
        seasons = table.find_all('tr', class_=None)
        
        seasons_markup = types.InlineKeyboardMarkup()
        for i, season in enumerate(seasons):
            self.seasons_names.append(season.text)
            seasons_markup.row(types.InlineKeyboardButton(text=season.text, callback_data='season_subs'+str(i)))
        seasons_markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))        
        
        self.seasons_markup = seasons_markup
        
        lista = table.find_all('tr')
        sesn = []
        j = 2
        while True:
            if lista[j].get('itemprop') == 'episode':
                cells = lista[j].find_all('td')
                if cells[4].text == 'Upload':
                    sesn.append((cells[0].text.replace('\n','').replace('\t','') , '\n\nSorry, no subs found.', None))
                else:
                    sesn.append((cells[0].text.replace('\n','').replace('\t','') , f'{cells[0].text.replace('\n','').replace('\t','')}\n\nIMDB rating: {cells[3].text}/10', BASE_OSUBS_TV + self.lang + '/imdbid-' + cells[2].a.get('href').split('-')[-1]))
            else:
                self.seasons.append(sesn)
                sesn = []
            j +=1
            if j == len(lista): 
                self.seasons.append(sesn)
                break
        
    async def get_season_markup(self):
        markup = types.InlineKeyboardMarkup()
        for i, (ep_name, _, _) in enumerate(self.seasons[self.selected_season]):
            markup.row(types.InlineKeyboardButton(text=ep_name, callback_data='ep_subs' + str(i)))
        markup.row(types.InlineKeyboardButton(text='Go back to seasons', callback_data='back_to_seasons'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
        return markup
                        
    async def get_swipe_markup(self):
        markup = types.InlineKeyboardMarkup()
        if self.max_index == 0:
            markup.row(types.InlineKeyboardButton(text='No results found', callback_data='ignore'))
            markup.row(types.InlineKeyboardButton(text='Close', callback_data='result_no'))
            self.swipe_markup = markup
            return
        if self.max_index > 1 and self.current_index < 1:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_subs'))
        elif self.current_index >= 1 and self.current_index < self.max_index - 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_subs'), types.InlineKeyboardButton(text='➡️', callback_data='r_subs'))
        elif self.current_index >= 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_subs'))
        markup.row(types.InlineKeyboardButton(text='Get subs', callback_data='get_subs'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='close_arrow'))
        self.swipe_markup = markup