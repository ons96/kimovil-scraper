import time
import cloudscraper
import json
import csv
import os
import random
import requests
import re
from tqdm import tqdm
from requests.exceptions import RequestException
import logging
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

ua = UserAgent()

url = 'https://www.kimovil.com/en/where-to-buy-xiaomi-12'

querystring = {"xhr": "1"}

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.kimovil.com/en/compare-smartphones",
    "Sec-Ch-Ua": "^\^Chromium^^;v=^\^116^^, ^\^Not"
}

headers["User-Agent"] = ua.random

scraper = cloudscraper.create_scraper()
print("Scraper created.")

response = scraper.get(url, headers=headers, params=querystring, timeout=3)

soup = BeautifulSoup(response.text, 'html.parser')

miniki_div = soup.find('div', id='block-ki-composition')
if miniki_div:
    scores = miniki_div.find_all(class_='score')
    print([element.get_text() for element in scores])
else:
    print('No div with id "miniki" found')

table = soup.find('table', class_='k-dltable')
if table:
    table_html = str(table)
    match = re.search(r'<tr><th>\s*Type\s*</th><td>\s*(.*?)\s*<div', table_html, re.DOTALL)
    if match:
        print(match.group(1))
    else:
        print('No th labeled "Type" found')
else:
    print('No table with class "k-dltable" found')
    