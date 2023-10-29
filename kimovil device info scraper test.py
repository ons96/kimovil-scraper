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

logging.basicConfig(filename='scraper.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

filename = "C:/Users/owens/Downloads/devices.txt"

url_template = 'https://www.kimovil.com/en/where-to-buy-{}'

querystring = {"xhr": "1"}

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.kimovil.com/en/compare-smartphones",
    "Sec-Ch-Ua": "^\^Chromium^^;v=^\^116^^, ^\^Not"
    #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    #"X-Forwarded-For": "38.0.101.76"
}

scraper = cloudscraper.create_scraper()
print("Scraper created.")

with open(filename, 'r') as f:
    device_names = [line.strip() for line in f]
print(f"Loaded {len(device_names)} device names from {filename}")

price_dict = {}
print("Price dictionary initialized.")

csv_file = 'C:/Users/owens/Downloads/device_info.csv'

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
    for proxy in proxies:
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        try:
            response = scraper.get(url, headers=headers, params=params, proxies=proxy_dict, timeout=3)
            if response.status_code != 429:
                return response
            else:
                print(f"Rate limit reached with proxy {proxy}")
                raise requests.exceptions.HTTPError
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"Error using proxy {proxy}: {e}")
            blacklist.add(proxy)
            proxies.remove(proxy)
            if len(proxies) == 0 and len(blacklist) > 0:
                print("All proxies are blacklisted. Emptying blacklist and retrying...")
                proxies.extend(list(blacklist))
                blacklist.clear()
    return None

blacklist = set()
remaining_devices = device_names.copy()
progress_bar = tqdm(total=len(remaining_devices), desc="Processing devices", ncols=100)
current_proxy = random.choice(proxies)

while remaining_devices:
    device_name = remaining_devices.pop(0)

    # If you want to update all the prices, comment out the following lines.
    if device_name in price_dict:
        error_message = price_dict[device_name][-1]
        current_price = price_dict[device_name][0]
        if error_message not in ['', 'Error getting the JSON'] or current_price is not None:
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

        headers["User-Agent"] = ua.random
        response = get_response_with_retries(url, headers, querystring, proxies, blacklist)

        # Create a Beautiful Soup object and specify the parser.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the device specifications.
        # Replace the class names with the actual classes you find when you inspect the webpage. 
        ki_score = soup.find_all("div", class_="miniki")
        design_materials = soup.find(class_='design-materials-class').get_text()
        performance_hardware = soup.find(class_='performance-hardware-class').get_text()
        camera = soup.find(class_='camera-class').get_text()
        connectivity = soup.find(class_='connectivity-class').get_text()
        battery = soup.find(class_='battery-class').get_text()
        screen_type = soup.find(class_='screen-type-class').get_text()
        processor = soup.find(class_='processor-class').get_text()
        battery_size = soup.find(class_='battery-size-class').get_text()
        antutu_score = soup.find(class_='antutu-score-class').get_text()
        canada_network_bands = soup.find(class_='canada-network-bands-class').get_text()
        peak_brightness = soup.find(class_='peak-brightness-class').get_text()
        ram = soup.find(class_='ram-class').get_text()
        storage_amount = soup.find(class_='storage-amount-class').get_text()
        fingerprint_sensor = soup.find(class_='fingerprint-sensor-class').get_text()
        sd_card_slot = soup.find(class_='sd-card-slot-class').get_text()
        headphone_jack = soup.find(class_='headphone-jack-class').get_text()
        nfc = soup.find(class_='nfc-class').get_text()
        volte = soup.find(class_='volte-class').get_text()
        fast_charge_speed = soup.find(class_='fast-charge-speed-class').get_text()
        google_services = soup.find(class_='google-services-class').get_text()

        # Save the data.
        price_dict[device_name] = [device_name, ki_score, design_materials, performance_hardware, camera, connectivity, battery, 
                                screen_type, processor, battery_size, antutu_score, canada_network_bands, peak_brightness, ram, 
                                storage_amount, fingerprint_sensor, sd_card_slot, headphone_jack, nfc, volte, fast_charge_speed, 
                                google_services]

        if response is None:
            print(f"Skipping {device_name} due to no working proxies")
            remaining_devices.append(device_name)  # Add the device back to the list to try again later
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
        writer.writerow(['Device Name', 'Ki cost effective score', 'Design & Materials', 'Performance & Hardware', 'Camera', 
                        'Connectivity', 'Battery', 'Screen type', 'Processor', 'Battery size', 'AnTuTu score', 
                        'Canada network bands', 'Peak brightness', 'RAM', 'Storage amount', 'Fingerprint sensor', 
                        'SD card slot', 'Headphone jack', 'NFC', 'VoLTE', 'Fast charge speed', 'Google Services (official)','Error Messages'])
        for device, data in price_dict.items():
            writer.writerow([device] + data)

    print(f'Data for {device_name} has been saved to {csv_file}')
    progress_bar.update(1)
    time.sleep(random.uniform(2, 3))