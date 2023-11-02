import asyncio
import aiohttp
import aiofiles
import os
from tqdm import tqdm
from aiohttp_socks import ProxyConnector, ProxyType
from aiohttp import TCPConnector
from aiohttp.helpers import Proxy

class ProxyConnector(TCPConnector):
    def __init__(self, proxy, **kwargs):
        super().__init__(**kwargs)
        self._proxy = Proxy(proxy)

    async def _create_proxy_connection(self, req, traces, timeout):
        _, proto = await super()._create_connection(req, traces, timeout)
        return self._proxy, proto

async def initialize_file(file_path):
    if os.path.exists(file_path):
        async with aiofiles.open(file_path, 'a+') as f:
            await f.truncate(0)

async def download_proxy_list(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(await resp.text())

async def check_proxy(session, proxy):
    connector = ProxyConnector.from_url(proxy, proxy_type=ProxyType.HTTP)
    try:
        async with session.get('https://httpbin.org/ip', connector=connector, timeout=2) as response:
            if response.status == 200:
                print(await response.text(), 'working')
                return (proxy, True)
    except Exception as e:
        return (proxy, False)

async def main():
    proxy_list_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    file_path = "http.txt"

    await download_proxy_list(proxy_list_url, file_path)
    print("Proxy list downloaded.")

    async with aiofiles.open(file_path, 'r') as f:
        proxies = [line.strip() for line in await f.readlines()]
    print("Proxies loaded.")

    file_directory = 'C:/Users/owens/Downloads/'    
    working_proxies_file = os.path.join(file_directory, 'working_proxies.txt')
    
    await initialize_file(working_proxies_file)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for proxy in proxies:
            tasks.append(check_proxy(session, proxy))
        results = []
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            result = await future
            results.append(result)

    async with aiofiles.open(working_proxies_file, 'a') as f:
        for proxy, is_working in results:
            if is_working:
                await f.write(proxy + "\n")

if __name__ == "__main__":
    asyncio.run(main())