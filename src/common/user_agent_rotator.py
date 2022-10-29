import random
import requests
import pandas as pd
from itertools import cycle

from constants import DEFAULT_USER_AGENT

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
    browers = [
        'software_name/firefox/',
        'software_name/chrome/',
        'software_name/facebook-app/',
        'software_name/android-webview/',
        'software_name/instagram/',
        'software_name/opera/',
        'software_name/edge/',
        'software_name/uc-browser/',
        'software_name/webkit-based-browser/',
        'operating_system_name/ios/',
        'operating_system_name/windows/',
        'operating_system_name/linux/',
        'operating_system_name/macos/',
        'operating_system_name/mac-os-x/',
        'operating_system_name/fire-os/',
        'operating_system_name/symbian/',
        'operating_system_name/chrome-os/'
    ]
    url = "https://developers.whatismybrowser.com/useragents/explore/"

    dfs = []
    for b in browers:
        print("downloading {0}".format(b))
        endpoint = "".join([url, b])

        for page_num in range(1, 10):
            url_with_page = "".join([endpoint, str(page_num)])
            print("URL: {0}".format(url_with_page))
            try:
                page = requests.get(
                    url_with_page, headers=DEFAULT_USER_AGENT, timeout=5)
            except Exception as e:
                print("Time out exception: {0}".format(e))
                continue
            print("Done request")
            table = pd.read_html(page.text)
            df = table[0]
            df.columns = df.columns.str.strip()
            dfs.append(df)

    results = pd.concat(dfs)
    if to_csv:
        results.to_csv("user_agents.csv")


if __name__ == "__main__":
    download_agent_headers()
