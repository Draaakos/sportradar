import time
import random
import requests


def sleep_randomly():
    """ this timer will sleep between 0.5 and 2.5 seconds"""
    time.sleep(random.uniform(0.5, 2.5))


def api_request(url):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,fr;q=0.7',
        'Origin': 'https://s5.sir.sportradar.com',
        'Referer': 'https://s5.sir.sportradar.com/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    sleep_randomly()
    return requests.get(url, headers=headers).json()