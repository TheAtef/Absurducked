import os

HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

HEADERS_URBAN = {
    'Referer': 'https://www.urbandictionary.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}

HEADERS_SP = {
    'Referer': 'https://sp-today.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}

API_KEY = os.environ.get('API_KEY')

BASE_GENIUS = os.environ.get('BASE_GENIUS')
BASE_ANGHAMI = os.environ.get('BASE_ANGHAMI')
BASE_SONGTELL = os.environ.get('BASE_SONGTELL')
BASE_LRC = os.environ.get('BASE_LRC')

BASE_URBAN = os.environ.get('BASE_URBAN')
BASE_SP = os.environ.get('BASE_SP')
BASE_OTD = os.environ.get('BASE_OTD')

BASE_YTS_LIST = os.environ.get('BASE_YTS_LIST')
BASE_YTS_DETAILS = os.environ.get('BASE_YTS_DETAILS')
BASE_OSUBS = os.environ.get('BASE_OSUBS')
BASE_OSUBS_FILES = os.environ.get('BASE_OSUBS_FILES')
BASE_OSUBS_TV = os.environ.get('BASE_OSUBS_TV')

BASE_BOOKS_SEARCH = os.environ.get('BASE_BOOKS_SEARCH')
BASE_BOOKS_GET = os.environ.get('BASE_BOOKS_GET')

CHATID = os.environ.get('CHATID')