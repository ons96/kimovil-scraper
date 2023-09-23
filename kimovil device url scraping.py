import cloudscraper
import json
import re
import html
import time
import random
from html import unescape
from bs4 import BeautifulSoup
from itertools import product

querystring = {"xhr": "1"}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; LM-X410(FG)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
]

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.kimovil.com/en/compare-smartphones",
    "Sec-Ch-Ua": "^\^Chromium^^;v=^\^116^^, ^\^Not",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

scraper = cloudscraper.create_scraper()
filename = "C:/Users/owens/Downloads/deviceURLstrings.txt"
page_number = 1

while True:
    headers["User-Agent"] = random.choice(user_agents)
    url = f"https://www.kimovil.com/en/compare-smartphones/f_min_d+antutuBenchmark.438000,f_min_dr+value.6144,f_min_ds+value.65536,f_min_d+batteryMah.3000,f_min_d+batteryFastChargingWatt.20,page.{page_number}"
    response = scraper.get(url, headers=headers, params=querystring)
    print(response.status_code)

    data = response.json()
    html_content = data["content"]
    pattern = re.compile(r'device-name\">\s*<div class=\"title\">(.*?)<\/div>\s*<div')
    device_names = pattern.findall(html_content)

    if device_names:
        with open(filename, "a+") as f:
            f.seek(0)
            existing_content = f.read().splitlines()

            unique_devices = []

            for device_name in device_names:
                if device_name not in existing_content and device_name not in unique_devices:
                    f.write(f"{device_name}\n")
                    unique_devices.append(device_name)
                    print(f"Added device: {device_name}")
                #else:                    
                    #print(f"Device already exists: {device_name}")
    else:
        print(f"No matches found on page {page_number}. Stopping the iteration.")
        break

    print (f"finished scraping page {page_number}")
    page_number += 1
    time.sleep(random.uniform(1, 5))