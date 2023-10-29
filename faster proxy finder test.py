#I think this works fine? But test to make sure
import aiohttp
import asyncio
from tqdm import tqdm
import os

# Download the proxy list
async def download_proxy_list():
    proxy_list_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    async with aiohttp.ClientSession() as session:
        async with session.get(proxy_list_url) as response:
            text = await response.text()
            with open("http.txt", "w") as f:
                f.write(text)
            return [line.strip() for line in text.splitlines()]

async def extract(proxy):
    try:
        # Add the "http://" prefix
        proxy_url = "http://" + proxy

        async with aiohttp.ClientSession() as session:
            async with session.get('https://httpbin.org/ip', proxy=proxy_url, timeout=2) as response:
                json = await response.json()
                print(f"{proxy} is working: {json}")
                return (proxy, True)
    except Exception as e:
        print(f"Error checking {proxy}: {e}")
        return (proxy, False)

def initialize_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass
    else:
        open(file_path, 'w').close()  # This will clear the contents of the file

# Test proxies and store working and non-working proxies in separate files
async def main():
    file_directory = 'C:/Users/owens/Downloads/'
    working_proxies_file = os.path.join(file_directory, 'working_proxies.txt')
    non_working_proxies_file = os.path.join(file_directory, 'non_working_proxies.txt')

    initialize_file(working_proxies_file)
    initialize_file(non_working_proxies_file)

    # Download and load proxies
    proxies = await download_proxy_list()

    results = []
    async with aiohttp.ClientSession() as session:
        for proxy in tqdm(proxies):
            result = await extract(proxy)
            results.append(result)

    # Write proxies to respective files
    with open(working_proxies_file, "a") as wp, open(non_working_proxies_file, "a") as nwp:
        for proxy, is_working in results:
            if is_working:
                wp.write(proxy + "\n")
            else:
                nwp.write(proxy + "\n")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())