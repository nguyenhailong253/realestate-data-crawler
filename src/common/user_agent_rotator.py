import random
import requests
import pandas as pd
from itertools import cycle

from .constants import DEFAULT_USER_AGENT

# Rotate user agent https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
# Rotate IP address and user agent https://medium.com/geekculture/rotate-ip-address-and-user-agent-to-scrape-data-a010216c8d0c


def load_user_headers():
    headers = set()
    df = pd.read_csv("user_agents.csv")
    for i, r in df.iterrows():
        headers.add(r['User agent'])
    return headers


def get_random_user_agent() -> dict[str, str]:
    headers = load_user_headers()
    agent: str = random.choice(list(headers))
    user_agent = {
        'User-Agent': agent,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    return user_agent


def download_agent_headers(to_csv=True):
    print("downloading free agent-headers....")
    browers = ['firefox', 'chrome', 'facebook-app', 'android-webview',
               'instagram', 'opera', 'edge', 'uc-browser', 'webkit-based-browser']
    url = "https://developers.whatismybrowser.com/useragents/explore/software_name/"

    dfs = []
    for b in browers:
        print("downloading {0}".format(b))
        endpoint = "".join([url, b])
        page = requests.get(endpoint, headers=DEFAULT_USER_AGENT, timeout=5)
        print("Done request")
        table = pd.read_html(page.text)
        df = table[0]
        df.columns = df.columns.str.strip()
        dfs.append(df)

    os = ['ios', 'windows', 'linux', 'macos',
          'mac-os-x', 'fire-os', 'symbian', 'chrome-os']
    url = "https://developers.whatismybrowser.com/useragents/explore/operating_system_name/"

    for o in os:
        print("downloading {0}".format(o))
        endpoint = "".join([url, o])
        page = requests.get(endpoint, headers=DEFAULT_USER_AGENT)
        print("Done request")
        table = pd.read_html(page.text)
        df = table[0]
        df.columns = df.columns.str.strip()
        dfs.append(df)

    results = pd.concat(dfs)
    if to_csv:
        results.to_csv("user_agents.csv")
