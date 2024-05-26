"""
Neologism database scraper
"""

from datetime import datetime
import random
from time import sleep

from bs4 import BeautifulSoup
import numpy as np
import requests

from new_value import has_new_value

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}

url = 'https://neolex.iling.spb.ru/search?search_api_fulltext=&page={page}'
new_url = ('https://neolex.iling.spb.ru/search?search_api_fulltext=&indexed-glossary-facets%5B0%5D=has_new_value%3A1'
           '&page={page}')

count = 0
page = 0

data = [['Слово', 'Тип единицы', 'Лексико-семантические связи', 'Темы',
         'Энциклопедическая справка', 'Словообразовательная справка', 'Год',
         'Новое значение?']]

neo_types = {
    'type-41': 'Слово',
    'type-42': 'Устойчивое словосочетание',
    'type-506': 'Устойчивое словосочетание (обобщающее)',
    'type-43': 'Фразеологизм'
}

while count <= 510:

    print('Page:', page)
    response = requests.get(url.format(page=page), HEADERS)
    print(f"Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'lxml')

    tables = soup.find_all('div', {'class': 'entry-grid-row views-row'})

    for table in tables:

        if table.find('details', {
                'class': 'sub-entry'}) is not None:
            continue

        try:
            name = table.find('span', {
                'class': 'field field--name-title field--type-string field--label-hidden'}).text.strip()
        except AttributeError:
            name = ''

        try:
            for t in neo_types:
                if table.find('h5', {'class': 'card-title'}).find('span', {'class': f'headword-{t}'}):
                    neo_type = neo_types.get(t)
        except AttributeError:
            neo_type = ''

        try:
            links = [l.text.strip() for l in table.find('div', {'class': 'sense-references'}).find_all(
                'span', {'class': 'field field--name-title field--type-string field--label-hidden'})]
        except AttributeError:
            links = []

        try:
            themes = [l.text.strip() for l in table.find('p', {'class': 'ideographic-terms'}).find_all(
                'span', {'class': 'border badge'})]
        except AttributeError:
            themes = []

        try:
            enc = table.find('p', {
                'class': 'extraling-reference'}).text.replace('\n', '').replace(';', ',').strip()
        except AttributeError:
            enc = ''

        try:
            et = table.find('li', {
                'class': 'field-etym-variant ml-2 mr-2'}).text.replace('\n', '').replace(';', ',').strip()
        except AttributeError:
            et = ''

        try:
            year = table.find('div', {'class': 'card-footer'}).text.strip()
        except AttributeError:
            year = ''

        # print(name, links, themes, enc, et, year)

        data.append([name, neo_type, ','.join(links), ','.join(themes), enc, et, year, ''])
        count += 1

        print(count)

    sleep(random.randrange(2, 5))
    page += 1

count = 0
page = 0

for i in range(28):
    print('Page:', page)
    response = requests.get(new_url.format(page=page), HEADERS)
    print(f"Status Code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'lxml')

    tables = soup.find_all('div', {'class': 'entry-grid-row views-row'})

    for table in tables:

        for d in data[1:]:
            if has_new_value(table, d[0]):
                d[-1] = 'Да'
            continue

        count += 1

    sleep(random.randrange(2, 5))
    page += 1

filename = datetime.now().strftime('%Y%m%d_%H%M%S.csv')
np.savetxt(filename,
           data,
           delimiter=";",
           fmt='%s')
