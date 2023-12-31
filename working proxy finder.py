import requests
import concurrent.futures
from tqdm import tqdm
import os
from datetime import datetime

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Download the proxy list
print("Downloading proxy list...")
proxy_list_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
response = requests.get(proxy_list_url)
with open("http.txt", "w") as f:
    f.write(response.text)
print("Proxy list downloaded.")

# Load proxies from the file
with open("http.txt", "r") as f:
    proxies = [line.strip() for line in f]
print("Proxies loaded.")

def extract(proxy):
    try:
        r = requests.get('https://httpbin.org/ip', proxies={'http': proxy, 'https': proxy}, timeout=2)
        print(r.json(), 'working')
        return (proxy, True)
    except:
        return (proxy, False)
    
def check_and_reset_files(file_path):
    # If the file doesn't exist, create it and store the current date
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(today)
        return True
    # If the file exists, check the stored date
    else:
        with open(file_path, 'r') as f:
            stored_date = f.readline().strip()
        # If the stored date is earlier than today, clear the file and store today's date
        if stored_date < today:
            with open(file_path, 'w') as f:
                f.write(today)
            return True
    return False

def initialize_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass

# Test proxies and store working and non-working proxies in separate files
def main():
    file_directory = 'C:/Users/owens/Downloads/'
    date_file = os.path.join(file_directory, 'date.txt')
    working_proxies_file = os.path.join(file_directory, 'working_proxies.txt')
    non_working_proxies_file = os.path.join(file_directory, 'non_working_proxies.txt')

    # Check the date and reset files if necessary
    if check_and_reset_files(date_file):
        initialize_file(working_proxies_file)
        initialize_file(non_working_proxies_file)

    # Load previously checked proxies
    with open(working_proxies_file, "r") as f:
        working_proxies = {line.strip() for line in f}
    with open(non_working_proxies_file, "r") as f:
        non_working_proxies = {line.strip() for line in f}
    
    # Filter out already checked proxies
    proxies_to_check = [proxy for proxy in proxies if proxy not in working_proxies and proxy not in non_working_proxies]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Wrap the executor.map call with tqdm to display a progress bar
        results = list(tqdm(executor.map(extract, proxies_to_check), total=len(proxies_to_check)))

    # Write proxies to respective files
    with open(working_proxies_file, "a") as wp, open(non_working_proxies_file, "a") as nwp:
        for proxy, is_working in results:
            if is_working:
                wp.write(proxy + "\n")
            else:
                nwp.write(proxy + "\n")

if __name__ == "__main__":
    main()