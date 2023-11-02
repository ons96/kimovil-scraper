import requests
import concurrent.futures
from tqdm import tqdm
import os
from datetime import datetime

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Create a Session object
session = requests.Session()

def extract(proxy):
    try:
        r = session.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=2)
        r.raise_for_status()
        print(r.json(), 'working')
        return (proxy, True)
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        return (proxy, False)

def check_and_reset_files(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(today)
        return True
    else:
        with open(file_path, 'r') as f:
            stored_date = f.readline().strip()
        if stored_date < today:
            with open(file_path, 'w') as f:
                f.write(today)
            return True
    return False

def initialize_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass

def main():
    print("Downloading proxy list...")
    proxy_list_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    response = session.get(proxy_list_url)
    with open("http.txt", "w") as f:
        f.write(response.text)
    print("Proxy list downloaded.")

    with open("http.txt", "r") as f:
        proxies = [line.strip() for line in f]
    print("Proxies loaded.")

    file_directory = 'C:/Users/owens/Downloads/'
    date_file = os.path.join(file_directory, 'date.txt')
    working_proxies_file = os.path.join(file_directory, 'working_proxies.txt')
    non_working_proxies_file = os.path.join(file_directory, 'non_working_proxies.txt')

    if check_and_reset_files(date_file):
        initialize_file(working_proxies_file)
        initialize_file(non_working_proxies_file)

    with open(working_proxies_file, "r") as f:
        working_proxies = {line.strip() for line in f}
    with open(non_working_proxies_file, "r") as f:
        non_working_proxies = {line.strip() for line in f}

    proxies_to_check = set(proxies) - working_proxies - non_working_proxies

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = list(tqdm(executor.map(extract, proxies_to_check), total=len(proxies_to_check)))

    with open(working_proxies_file, "a") as wp, open(non_working_proxies_file, "a") as nwp:
        for proxy, is_working in results:
            if is_working:
                wp.write(proxy + "\n")
            else:
                nwp.write(proxy + "\n")

if __name__ == "__main__":
    main()