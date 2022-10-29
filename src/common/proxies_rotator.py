import requests
import traceback
import pandas as pd
from lxml.html import fromstring
from itertools import cycle

from constants import DEFAULT_USER_AGENT

# Rotate proxies https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/

FILE_NAME = "proxies.csv"


def download_free_proxies(to_csv=True):
    print("downloading free proxies...")
    url = "https://free-proxy-list.net/"
    page = requests.get(url, headers=DEFAULT_USER_AGENT)
    table = pd.read_html(page.text)
    df = table[0]
    df.dropna(inplace=True)
    df = df.groupby(['Https']).get_group('yes')
    df.reset_index(inplace=True)

    if to_csv:
        df.to_csv(FILE_NAME)


class Proxy:
    def __init__(self):
        proxies = self.load_proxies()
        self.proxy_pool = cycle(proxies)

    def load_proxies(self):
        proxies = set()
        try:
            df = pd.read_csv(FILE_NAME)
            for i, r in df.iterrows():
                proxy = ':'.join([r['IP Address'], str(r['Port'])[:-2]])
                proxies.add(proxy)
        except Exception as e:
            print(e)

        return proxies

    def get_proxies(self):
        proxy = next(self.proxy_pool)
        return {"http": proxy, "https": proxy}

    def reset_proxy_pool(self):
        download_free_proxies()
        proxies = self.load_proxies()
        self.proxy_pool = cycle(proxies)
