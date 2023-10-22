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
import concurrent.futures
import signal
import sys

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

interrupted = False

def handler(signum, frame):
    global interrupted
    interrupted = True
    print('Signal handler called with signal', signum)

# Set the signal handler
signal.signal(signal.SIGINT, handler)

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

filename = "C:/Users/owens/Downloads/deviceURLstrings.txt"
page_number_lock = threading.Lock()
page_number_cond = threading.Condition(page_number_lock)
blacklist = set()

proxies_lock = threading.Lock()
blacklist_lock = threading.Lock()

def fetch_device_names(page_number, proxies, blacklist):
    global interrupted
    current_proxy = None
    while True:
        if interrupted:
            return
        with proxies_lock:
            if current_proxy is None or current_proxy in blacklist:
                # Select a new proxy if none is currently set or if it's in the blacklist
                if len(proxies) == 0:
                    print("No more proxies available. Exiting...")
                    return
                current_proxy = random.choice(proxies)
                with blacklist_lock:
                    blacklist.discard(current_proxy)  # Remove from blacklist if it's there

        headers["User-Agent"] = ua.random
        url = f"https://www.kimovil.com/en/compare-smartphones/f_min_d+antutuBenchmark.438000,f_min_dr+value.6144,f_min_ds+value.65536,f_min_d+batteryMah.3000,f_min_d+batteryFastChargingWatt.20,page.{page_number[0]}"
        
        response = get_response_with_retries(url, headers, querystring, current_proxy, blacklist)

        if response is not None:
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
            else:
                print(f"No matches found on page {page_number}. Stopping the iteration.")
                return

            print(f"Finished scraping page {page_number[0]}")
            #page_number += 1
            time.sleep(random.uniform(2, 3))

        with page_number_cond:
            page_number_cond.notify()

page_number = [26]

# Create a ThreadPoolExecutor
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            with page_number_cond:
                future = executor.submit(fetch_device_names, page_number, proxies, blacklist)
                page_number_cond.wait()  # Wait for the worker thread to finish
            if future.result() is None:
                break
            with page_number_lock:
                page_number[0] += 1
except KeyboardInterrupt:
    executor.shutdown(wait=False)
    print("Stopped by user.")