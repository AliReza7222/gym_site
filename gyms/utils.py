import requests

from bs4 import BeautifulSoup

from .models import Locations


def create_location():
    url = 'https://en.wikipedia.org/wiki/List_of_cities_in_Iran_by_province'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = soup.find_all('span', class_='mw-headline')
    dict_ans = dict()
    for tag_span in result[:31]:
        pro = tag_span.find('a', class_='mw-redirect')
        dict_ans[pro.text.strip('Province').strip()] = []

    table_tags = soup.find_all('table', class_='wikitable sortable')

    list_pro = list(dict_ans.keys())
    for index_table, table in enumerate(table_tags):
        list_city = list()
        cities = table.find_all('a')
        for city in cities:
            list_city.append(city.text)
            Locations.objects.create(province=list_pro[index_table], name_city=city.text)
        dict_ans[list_pro[index_table]] = list_city
