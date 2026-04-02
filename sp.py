import requests
import  json
from datetime import datetime
from constants import BASE_SP, HEADERS_SP

format_time = "%Y-%m-%dT%H:%M:%S+03:00"

async def get_data_sp():
    currencies, gold, crypto = {}, {}, {}
    
    with requests.Session() as s:
        r = s.get(BASE_SP + 'currencies', headers=HEADERS_SP)
        if r.status_code == 200:
            parsed_json = json.loads(r.text)
            currencies['name'] = f'💵 ***Currencies:*** _{datetime.strptime(parsed_json['data']['currencies'][0]['updated_at'], format_time)}_\n\n'
            for item in parsed_json['data']['currencies']:
                city = item['cities']['damascus']
                currencies[item['code']] = f'{item['symbol']} - {item['name_ar']}:\nBuy: {float(city['buy']):,.0f} - Sell: {float(city['sell']):,.0f} - Change: {float(city['change']):.2f}%\n'
            
        r = s.get(BASE_SP + 'gold', headers=HEADERS_SP)
        if r.status_code == 200:
            parsed_json = json.loads(r.text)
            gold['name'] = f'\n🪙 ***Gold:*** _{datetime.strptime(parsed_json['data']['ounce']['updated_at'], format_time)}_\n\n'
            
            ounce = parsed_json['data']['ounce']
            gold['ounce'] =  f'Ounce:\nPrice: {float(ounce['price_usd']):,.2f}$ - Change: {float(ounce['change']):.2f}%\n'

            for item in parsed_json['data']['karats']:
                city = item['cities']['damascus']
                gold[item['karat']] =  f'{item['karat']}:\nBuy: {float(city['buy']):,.0f} - Sell: {float(city['sell']):,.0f} - Change: {float(city['change']):.2f}%\n'

        r = s.get(BASE_SP + 'crypto', headers=HEADERS_SP)
        if r.status_code == 200:
            crypto['name'] = '\n🌐 ***Crypto:***\n\n'
            parsed_json = json.loads(r.text)
            for item in parsed_json['data']:
                crypto[item['id']] = f'{item['name']} - {item['symbol']}:\nPrice: {float(item['price_usd']):,.2f}$ - Change 24h: {float(item['change_24h']):.2f}%\n'
                
    return currencies, gold, crypto

