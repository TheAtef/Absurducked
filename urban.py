from constants import BASE_URBAN, HEADERS_URBAN
import requests
from bs4 import BeautifulSoup as bs
import re
from telebot import types
import json

class UrbanScraper:
    def __init__(self, query):
        self.query = query.strip()
        self.api = f'{BASE_URBAN}{self.query}'
        self.markup = None
        self.matches = 0
        self.terms = None
        self.term = None
        self.term_index = 0
        self.definitions = None
        self.current_index = 0
        self.swipe_markup = None
        
        
    async def can_get_exact(self):
        url = "https://www.urbandictionary.com/define.php?term=" + self.query
        r = requests.get(url, headers=HEADERS_URBAN)
        return ("No definitions found for " not in r.text)
    
    async def get_api(self):
        r = requests.get(self.api, headers=HEADERS_URBAN)
        if r.status_code == 200:
            soup = bs(r.content, features='lxml')
            data = soup.text
            parsed_json = json.loads(data)
            terms, previews = ([] for i in range(2))
            
            for j in range(len(parsed_json['results'])):
                pre = parsed_json['results'][j]['preview']
                rterm = parsed_json['results'][j]['term']
                terms.append(rterm)
                previews.append(pre)
            
            markup = types.InlineKeyboardMarkup()
            matches = 0
            for value in terms:
                markup.add(types.InlineKeyboardButton(text=value, callback_data='urban'+str(matches)))
                matches += 1
            if matches == 0:
                 markup.add(types.InlineKeyboardButton(text="No results found", callback_data='ignore'))
            markup.add(types.InlineKeyboardButton(text="Close" ,callback_data='result_no'))

            self.terms = terms
            self.markup = markup
            self.matches = matches

    async def get_definitions(self):
        url = "https://www.urbandictionary.com/define.php?term=" + self.term
        r = requests.get(url, headers=HEADERS_URBAN)
        if r.status_code == 200:
            soup = bs(r.content, features='lxml')
            div = soup.find("div", class_=re.compile("mx-0")).section
            definitions = div.find_all_next("div", class_=re.compile("^definition"))
            for i, definition in enumerate(definitions):
                try:
                    meaning = definition.find("div", class_=re.compile("meaning"))
                    meaning = str(meaning).replace("<br/>", "\n")
                    convert_meaning = bs(meaning, features='lxml').text
                    example = definition.find("div", class_=re.compile("example"))
                    example = str(example).replace("<br/>", "\n")
                    convert_example = bs(example, features='lxml').text
                    # votes = definition.find_all_next("span", class_=re.compile("text-xs font-bold uppercase"))
                    # upvotes = bs(str(votes[0]), features='lxml').text
                    # downvotes = bs(str(votes[1]), features='lxml').text
                    #### or:
                    # upvotes = definition.find('span', attrs={'data-x-text': 'upCount'})
                    # convert_upvotes = bs(upvotes, features='lxml').text
                    # downvotes = definition.find('span', attrs={'data-x-text': 'downCount'})
                    # convert_downvotes = bs(str(downvotes), features='lxml').text
                    # print(convert_downvotes)
                    definitions[i] = str(i+1) + ". " + convert_meaning + "\n\n_" + convert_example + "_" #+ "\n\n👍 " + convert_upvotes + " 👎 " + convert_downvotes
                except:
                    pass
            # target.insert(0, term.title() + " Definition in Urban Dictionary:")
            self.definitions = definitions
            self.matches = len(definitions)
            await self.get_swipe_markup()
        
        
    async def get_swipe_markup(self):
        markup = types.InlineKeyboardMarkup()
        if self.matches > 1 and self.current_index < 1:
            markup.row(types.InlineKeyboardButton(text='➡️', callback_data='r_urban'))
        elif self.current_index >= 1 and self.current_index < self.matches - 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_urban'), types.InlineKeyboardButton(text='➡️', callback_data='r_urban'))
        elif self.current_index >= 1:
            markup.row(types.InlineKeyboardButton(text='⬅️', callback_data='l_urban'))
        markup.row(types.InlineKeyboardButton(text='Close', callback_data='close_arrow'))
        self.swipe_markup = markup
        
    async def set_term(self, term_index):
        self.term_index = term_index
        self.term = self.terms[self.term_index]