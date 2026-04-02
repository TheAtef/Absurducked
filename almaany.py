import json
import cloudscraper
from bs4 import BeautifulSoup as bs
from telebot import types
import re

class AlmaanyScraper:
    def __init__(self, query):
        self.query = query.strip()
        self.link = f'https://www.almaany.com/suggest.php?term={self.query}&lang=arabic&t=d'
        self.suggestions = self.get_suggestions()
        self.markup = self.get_markup()
        self.dict_markup = None
        self.selected_word = None
        self.maany_list = None
        self.current_index = 0
        self.max_counter = 0
        self.five_maany = None
        
    def get_suggestions(self):
        scraper = cloudscraper.create_scraper()
        r = scraper.get(self.link)
        suggestions = []
        if r.status_code == 200:
            soup = bs(r.content, features='lxml')
            data = soup.text
            parsed_json = json.loads(data)
            results_counter = len(parsed_json)
            for x in range(results_counter):
                suggestions.append(parsed_json[x])
            return suggestions

    
    def get_markup(self):
        markup = types.InlineKeyboardMarkup()
        count = 0
        for suggestion in self.suggestions:
            markup.add(types.InlineKeyboardButton(text=suggestion, callback_data='Maany' + suggestion), row_width=8)
            count += 1
        markup.add(types.InlineKeyboardButton(text='إغلاق', callback_data='result_no'), row_width=8)
        return markup
        
    # def get_dict_markup(self):
    #     markup = types.InlineKeyboardMarkup()
    #     maany_btn = types.InlineKeyboardButton(text='المعاني الجامع', callback_data='Maany' + self.selected_word)
    #     mokhtar_btn = types.InlineKeyboardButton(text='مختار الصحاح', callback_data='Mokhtar' + self.selected_word)
    #     waseet_btn = types.InlineKeyboardButton(text='المعجم الوسيط', callback_data='Waseet' + self.selected_word)
    #     moaaser_btn = types.InlineKeyboardButton(text='العربيّة المعاصر', callback_data='Moaaser' + self.selected_word)
    #     ghani_btn = types.InlineKeyboardButton(text='الغني', callback_data='AlGhani' + self.selected_word)
    #     moheet_btn = types.InlineKeyboardButton(text='القاموس المحيط', callback_data='Moheet' + self.selected_word)
    #     markup.row(waseet_btn, mokhtar_btn, maany_btn)
    #     markup.row(moheet_btn, ghani_btn, moaaser_btn)
    #     markup.row(types.InlineKeyboardButton(text='إغلاق', callback_data='close_arrow'))
    #     self.dict_markup = markup
    #     return self.dict_markup
    
    def get_maany(self):
        url = f'https://www.almaany.com/ar/dict/ar-ar/{self.selected_word}/'
        # scraper = cfscrape.create_scraper()
        # r = scraper.get(url)
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url)
        if r.status_code == 200:
            soup = bs(r.content, features='lxml')
            maany_raw = soup.find("ol", class_=re.compile("^meaning$|results"))
            pattern = re.compile('^<span id="w$|\d{3,7}+')
            res = pattern.findall(str(maany_raw))
            maany_fixed = str(maany_raw)
            REPLACEMENTS = []
            for x in res:
                x_set = ('<span id="w{}">'.format(str(x)), "@*")
                REPLACEMENTS.append(x_set)
            for old, new in REPLACEMENTS:
                maany_fixed = maany_fixed.replace(old, new)
            maany_fixed = maany_fixed.replace('</li>', '\n')
            convert = bs(maany_fixed, features='lxml')
            maany = convert.text.strip()
            maany_list = maany.split("@*")
            maany_list.pop(0)
            for i, maana in enumerate(maany_list):
                maany_list[i] = re.sub(r'\n+', '\n', maana.strip())
            self.maany_list = maany_list
            self.max_counter = len(maany_list)
        
        
    # def get_maany_else(self, url):
    #     scraper = cloudscraper.create_scraper()
    #     r = scraper.get(url)
    #     if r.status_code == 200:
    #         soup = bs(r.content, features='lxml')
    #         maany_raw = soup.find("ol", class_=re.compile("^meaning$|results"))
    #         maany_fixed = str(maany_raw).replace("<span><b>", "@*")
    #         maany_fixed = maany_fixed.replace('<br/>', '\n')
    #         convert = bs(maany_fixed, features='lxml')
    #         maany = convert.text.strip()
    #         maany_list = []
    #         maany_list = maany.split("@*")
    #         maany_list.pop(0)
    #         return maany_list
        
    async def get_five_and_markup(self):
        markup = types.InlineKeyboardMarkup()
        message = ""
        j=0 
        for i, maana in enumerate(self.maany_list):
            if i >= self.current_index:
                message += str(i + 1) + "- " + maana + "\n\n"
                j+=1
            if j == 5:
                break
        if self.max_counter > 5 and self.current_index < 5:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_maany'))
        elif self.current_index >= 5 and self.current_index < self.max_counter - 5:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_maany'), types.InlineKeyboardButton(text='➡️', callback_data='r_maany'))
        elif self.current_index >= 5:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_maany'))
        markup.row(types.InlineKeyboardButton(text='إغلاق', callback_data='close_arrow'))
        self.songs_markup = markup
        self.five_maany = message