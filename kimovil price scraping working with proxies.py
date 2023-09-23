import time
import cloudscraper
import requests
import re
import json
import csv
import os
import random
from tqdm import tqdm  # Import tqdm

#sleep = 10

filename = "C:/Users/owens/Downloads/devices.txt"

url_template = 'https://www.kimovil.com/_json/{}_prices_deals.json'

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
    #"X-Forwarded-For": "38.0.101.76"
}

scraper = cloudscraper.create_scraper()
print("Scraper created.")

with open(filename, 'r') as f:
    device_names = [line.strip() for line in f]
print(f"Loaded {len(device_names)} device names from {filename}")

price_dict = {}
print("Price dictionary initialized.")

csv_file = 'C:/Users/owens/Downloads/device_prices.csv'

# Download the proxy list
""" print("Downloading proxy list...")
proxy_list_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
response = requests.get(proxy_list_url)
with open("http.txt", "w") as f:
    f.write(response.text)
print("Proxy list downloaded.") """

# Load proxies from the working_proxies.txt file
with open("C:/Users/owens/Downloads/working_proxies.txt", "r") as f:
    proxies = [line.strip() for line in f]
print("Proxies loaded.")

#remaining_devices = [device_name for device_name in device_names if device_name not in price_dict]


# Load existing prices.
if os.path.exists(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)

        # Check if the header has the 'Error Messages' column
        if len(header) == 3:
            header.append('Error Messages')
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(header)

        for row in reader:
            if len(row) == 4:
                device, cur_price, lowest_price, error_message = row
            else:
                device, cur_price, lowest_price = row
                error_message = ''

            cur_price = None if cur_price == '' else float(cur_price)
            lowest_price = None if lowest_price == '' else float(lowest_price)
            price_dict[device] = [cur_price, lowest_price, error_message]

def get_response_with_retries(url, headers, params, proxies, blacklist):
    while proxies:
        proxy = random.choice(proxies)
        if proxy in blacklist:
            proxies.remove(proxy)
            continue
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        try:
            response = scraper.get(url, headers=headers, params=params, proxies=proxy_dict, timeout=3)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error using proxy {proxy}: {e}")
            blacklist.add(proxy)
            proxies.remove(proxy)

            # Empty the blacklist if all proxies are blacklisted and add them back to the proxies list
            if len(proxies) == 0 and len(blacklist) > 0:
                print("All proxies are blacklisted. Emptying blacklist and retrying...")
                proxies.extend(list(blacklist))
                blacklist.clear()
    return None

blacklist = set()
remaining_devices = device_names.copy()
progress_bar = tqdm(total=len(remaining_devices), desc="Processing devices", ncols=100)

while remaining_devices:
    device_name = remaining_devices.pop(0)

    # If you want to update all the prices, comment out the following lines.
    if device_name in price_dict:
        #print()
        error_message = price_dict[device_name][-1]
        current_price = price_dict[device_name][0]
        if error_message not in ['', 'Error getting the JSON'] and current_price is not None:
            #print(f"skipping {device_name}; has prices or an error message")
            progress_bar.update(1)
            continue

    
    if proxies:
        # Replace '+' with 'plus' considering the space before it.
        url_device_name = re.sub(r'( ?)\+', lambda match: ' Plus' if match.group(1) == '' else 'plus', device_name)
        
        # Remove parentheses and other invalid URL characters.
        url_device_name = re.sub(r'[^\w\s\+-]', '', url_device_name)
        
        # Replace spaces with hyphens and convert to lowercase for the URL.
        device_id = re.sub("\s", "-", url_device_name.lower())
        print()
        print(url_device_name)
        url = url_template.format(device_id)
        print(f"Processing {device_name}...")

        headers["User-Agent"] = random.choice(user_agents)
        response = get_response_with_retries(url, headers, querystring, proxies, blacklist)

        if response is None:
            print(f"Skipping {device_name} due to no working proxies")
            #remaining_devices.append(device_name)
            progress_bar.update(1)  # Update the progress bar when skipping a device
            continue
        print(response.text.strip())
        print(response.status_code)

        if response.status_code == 200 and response.text and response.text.strip() != "":
            data = json.loads(response.text)

            if data["prices"]:
                min_usd_price = min(float(price["usdPrice"]) for price in data["prices"])

                if device_name not in price_dict or price_dict[device_name][0] is None or min_usd_price < price_dict[device_name][0]:
                    price_dict[device_name] = [min_usd_price, min_usd_price, '']
            else:
                print(f"No prices found for {device_name}")                
                price_dict[device_name] = [None, None, 'No prices found']
        
        else:
            print(f'Error getting the JSON for {device_name}')
            if device_name not in price_dict:
                price_dict[device_name] = [None, None, 'Error getting the JSON']
            else:
                price_dict[device_name] = [price_dict[device_name][0], price_dict[device_name][1], 'Error getting the JSON']

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Device Name', 'Current Price (USD)', 'Lowest Price Seen (USD)', 'Error Messages'])
        for device, data in price_dict.items():
            prices, error_message = data[:-1], data[-1]
            writer.writerow([device] + [str(price) if price is not None else '' for price in prices] + [error_message])

    print(f'Data for {device_name} has been saved to {csv_file}')
    progress_bar.update(1)
    #time.sleep(random.uniform(1, 5))