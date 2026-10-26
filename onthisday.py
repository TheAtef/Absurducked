import cloudscraper
from bs4 import BeautifulSoup as bs
import re
from telebot import types
from constants import BASE_OTD
# import cairosvg

class OTDScraper:
    def __init__(self, chat_id):
        self.scraper = cloudscraper.create_scraper()
        self.events = None
        self.swipe_markup = None
        self.current_index = 0
        self.max_index = 0
        self.chat_id = chat_id
        
    async def get_data_otd(self):
        events = []
        r = self.scraper.get(BASE_OTD)
        if(r.status_code == 200):
            soup = bs(r.content, features='lxml')
            # featured_event
            try:
                featured_event = soup.find("div", class_=re.compile("^otd-featured-event"))
                related = featured_event.find("a", class_=re.compile("^otd-he-link"))
                if related:
                    featured_event.find("a", class_=re.compile("^otd-he-link")).decompose()              
                date = featured_event.find("div", class_=re.compile("^date-label")).text.strip()
                # h2 = featured_event.find("h2").text
                title = featured_event.find("div", class_=re.compile("^title")).text.strip()
                description = featured_event.find("div", class_=re.compile("^description")).text.strip()
                src = featured_event.find("img").get('src')
                src_uncropped = re.search(r'[^\?]*', src)[0]
                events.append((f'On this day in _{date}_:\n\n***Featured - {title}***\n\n{description}', src_uncropped))
            except Exception as e:
                print(e)
            
            # more events
            try:
                more = soup.find("div", class_=re.compile("col-100 col-sm$"))
                # h2 = more.find("h2").text
                stuff = more.find_all("div", class_=re.compile("^md-history-event"))
                for item in stuff:
                    related = item.find("a", class_=re.compile("^otd-he-link"))
                    if related:
                        item.find("a", class_=re.compile("^otd-he-link")).decompose()
                    credit = item.find("div", class_=re.compile("^credit"))
                    if credit:
                        item.find("div", class_=re.compile("^credit")).decompose()   
                    date = item.find("div", class_=re.compile("^date-label")).text.strip()
                    body = item.find("div", class_=re.compile("^card-body")).text.strip()
                    src = item.find("img").get('src')
                    src_uncropped = re.search(r'[^\?]*', src)[0]
                    if '.svg' in src_uncropped:
                        # src_uncropped = cairosvg.svg2png(bytestring=src_uncropped)
                        # print(src_uncropped)
                        continue
                    events.append((f'On this day in _{date}_:\n\n{body}', src_uncropped))
            except Exception as e:
                print(e)
            
        self.events = events
        self.max_index = len(self.events)
        await self.get_swipe_markup()
        
    async def get_swipe_markup(self):
        markup = types.InlineKeyboardMarkup()
        if self.max_index > 1 and self.current_index < 1:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_otd'))
        elif self.current_index >= 1 and self.current_index < self.max_index - 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_otd'), types.InlineKeyboardButton(text='➡️', callback_data='r_otd'))
        elif self.current_index >= 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_otd'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='close_arrow'))
        self.swipe_markup = markup
        
