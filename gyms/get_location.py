# import os
# import requests
# import json
#
# from bs4 import BeautifulSoup
#
# from models import Locations
#
#
# def get_location():
#     url = 'https://en.wikipedia.org/wiki/List_of_cities_in_Iran_by_province'
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     result = soup.find_all('span', class_='mw-headline')
#     dict_ans = dict()
#     for tag_span in result[:31]:
#         pro = tag_span.find('a', class_='mw-redirect')
#         dict_ans[pro.text.strip('Province ')] = []
#
#     table_tags = soup.find_all('table', class_='wikitable sortable')
#
#     list_pro = list(dict_ans.keys())
#     for index_table, table in enumerate(table_tags):
#         list_city = list()
#         cities = table.find_all('a')
#         for city in cities:
#             list_city.append(city.text)
#             if not Locations.objects.filter(province=list_pro[index_table], name_city=city.text).exists:
#                 location_obj = Locations(province=list_pro[index_table], name_city=city.text)
#                 location_obj.save()
#         dict_ans[list_pro[index_table]] = list_city

#     create a file json
#     if not os.path.exists('locations.json'):
#         with open('locations.json', 'w') as data:
#             json.dump(dict_ans, data)
