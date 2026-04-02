import cloudscraper
from bs4 import BeautifulSoup as bs
import json
from telebot import types
from constants import BASE_BOOKS_SEARCH, BASE_BOOKS_GET

class BookScraper:
    def __init__(self, query):
        self.query = query.strip()
        self.scraper = cloudscraper.create_scraper()
        self.matched_books = {}
        self.swipe_markup = None
        self.current_index = 0 
        self.max_index = 0
        
    async def get_matched(self):
        payload = {
            'action': 'ajaxy_sf',
            'sf_value': self.query,
            'search': False
        }

        r = self.scraper.post(BASE_BOOKS_SEARCH, data=payload)
        parsed_json = json.loads(r.text)
        books = parsed_json['post'][0]['all']
        for i, book in enumerate(books):
            self.matched_books[i] = [
                            book['post_title'],
                            book['post_image'].rsplit('-', 1)[0] + '.jpg',
                            book['post_link']        
            ]
        self.max_index = len(self.matched_books.keys())
        await self.get_swipe_markup()
        
    async def get_swipe_markup(self):
        markup = types.InlineKeyboardMarkup()
        if self.max_index > 1 and self.current_index < 1:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_book'))
        elif self.current_index >= 1 and self.current_index < self.max_index - 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_book'), types.InlineKeyboardButton(text='➡️', callback_data='r_book'))
        elif self.current_index >= 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_book'))
        markup.row(types.InlineKeyboardButton(text='Choose', callback_data='book_choose'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='close_arrow'))
        self.swipe_markup = markup
        
    async def get_book(self):
        files = []
        r = self.scraper.get(self.matched_books[self.current_index][2])
        soup = bs(r.text, 'lxml')
        target = soup.find('div', class_='entry-content').ul.find_all('li')[-3]
        target.strong.decompose()
        paths = target.text.split(',')
        for path in paths:
            payload = {
                'filename':path.strip(),
                'id': 'srv3'
            }
            r = self.scraper.post(BASE_BOOKS_GET, data=payload)
            soup = bs(r.content, 'lxml')
            files.append(soup.body.div.find('script', type='text/JavaScript').text.strip().split('setTimeout("location.href = \'')[-1].split(';')[0].removesuffix('\''))
        return files