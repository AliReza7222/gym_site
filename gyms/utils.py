import re
import requests

from bs4 import BeautifulSoup

from .models import Locations


def create_location():
    url = 'https://en.wikipedia.org/wiki/List_of_cities_in_Iran_by_province'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = soup.find_all('span', class_='mw-headline')
    list_pro = list()
    for tag_span in result[:31]:
        pro = tag_span.find('a', class_='mw-redirect')
        list_pro.append(pro.text.strip('Province').strip())

    table_tags = soup.find_all('table', class_='wikitable sortable')
    for index_table, table in enumerate(table_tags):
        cities = table.find_all('a')
        for city in cities:
            name_city = city.text
            if name_city in re.findall('[a-zA-Z-\s]+', name_city):
                Locations.objects.create(province=list_pro[index_table], name_city=city.text)
