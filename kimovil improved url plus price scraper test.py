import pandas as pd
import cloudscraper
import json
import re
import html
import time
import random
import threading
from html import unescape
from bs4 import BeautifulSoup
from itertools import product
from fake_useragent import UserAgent
from tqdm import tqdm

skip_existing = False  # Set this to False if you want to update prices for existing devices

# Estimate the total number of pages. If you know the exact number, you can set it directly.
total_pages = 61

ua = UserAgent()

with open("C:/Users/owens/Downloads/working_proxies.txt", "r") as f:
    proxies = [line.strip() for line in f]
print("Proxies loaded.")

querystring = {"xhr": "1"}

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.kimovil.com/en/compare-smartphones",
    "Sec-Ch-Ua": "^\^Chromium^^;v=^\^116^^, ^\^Not",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

class TimeoutException(Exception): 
    pass 

def timeout_handler():
    raise TimeoutException

def get_response_with_retries(url, headers, params, proxy, blacklist, max_retry_count=2):
    retry_count = 0
    while retry_count < max_retry_count:
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        headers['User-Agent'] = ua.random  # Generate a random user agent
        try:
            scraper = cloudscraper.create_scraper()
            print(f"Attempting request with proxy {proxy}")
            timeout_timer = threading.Timer(10, timeout_handler)  # Set a timer for 10 seconds
            timeout_timer.start()
            response = scraper.get(url, headers=headers, params=params, proxies=proxy_dict, timeout=2)
            timeout_timer.cancel()  # Cancel the timer
            print(f"Request successful with proxy {proxy}")
            if response.status_code == 200:
                return response
        except TimeoutException:
            print(f"Request with proxy {proxy} timed out")
        except Exception as e:
            print(f"Error using proxy {proxy}: {e}")
        finally:
            timeout_timer.cancel()  # Ensure the timer is always cancelled
        blacklist.add(proxy)
        if proxy in proxies:
            proxies.remove(proxy)
        retry_count += 1

        if len(proxies) == 0 and len(blacklist) > 0:
            print("All proxies are blacklisted. Emptying blacklist and retrying...")
            proxies.extend(list(blacklist))
            blacklist.clear()

    return None

current_proxy = None
filename = "C:/Users/owens/Downloads/deviceNamesAndPrices.csv"
page_number = 1
blacklist = set()

# Initialize or load existing dataframe
try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=['device_name', 'device_price', 'lowest_price'])

with tqdm(total=total_pages) as pbar:
    while True:
        if current_proxy is None or current_proxy in blacklist:
            # Select a new proxy if none is currently set or if it's in the blacklist
            current_proxy = random.choice(proxies)
            blacklist.discard(current_proxy)  # Remove from blacklist if it's there

        headers["User-Agent"] = ua.random
        url = f"https://www.kimovil.com/en/compare-smartphones/f_min_d+antutuBenchmark.438000,f_min_dr+value.6144,f_min_ds+value.65536,f_min_d+batteryMah.3000,f_min_d+batteryFastChargingWatt.20,page.{page_number}"
        
        response = get_response_with_retries(url, headers, querystring, current_proxy, blacklist)

        if response is not None:
            data = response.json()
            html_content = data["content"]

            soup = BeautifulSoup(html_content, 'html.parser')
            items = soup.find_all('li', class_=re.compile(r'item smartphone.*'))

            # If no items are found on the page, break the loop
            if not items:
                print("No items found on page. Stopping...")
                break

            for item in items:
                device_name = item.find('div', class_='title').text.strip()
                device_info_json = json.loads(html.unescape(item['data-info']))
                device_price = device_info_json.get('price')
                lowest_price = device_info_json.get('lowestPrice')

                if device_name in df['device_name'].values:
                    idx = df[df['device_name'] == device_name].index[0]
                    
                    if skip_existing and pd.notna(df.loc[idx, 'device_price']):
                        print(f"Skipping {device_name} due to existing price.")
                        continue
                    
                    if device_price is not None:
                        device_price = float(device_price)
                        df.loc[idx, 'device_price'] = device_price
                        if pd.isna(df.loc[idx, 'lowest_price']) or device_price < float(df.loc[idx, 'lowest_price']):
                            df.loc[idx, 'lowest_price'] = device_price

                else:
                    new_row = {'device_name': device_name, 'device_price': float(device_price) if device_price is not None else None, 'lowest_price': float(lowest_price) if lowest_price is not None else None}
                    df.loc[len(df)] = new_row
                    print(f"Added device: {device_name}")

            df.to_csv(filename, index=False)

            print(f"Finished scraping page {page_number}")
            page_number += 1
            pbar.update(1)
            time.sleep(random.uniform(2, 3))