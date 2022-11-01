"""This program will query our DB and check which one is still on the market 
(off_market = false) and then query tenantapp.com.au to check if it's still on
or not. If it's not, update off_market = true and then update ad_removed_date
"""
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from src.transformer import Transformer
from src.property_database import PropertyDatabase
from src.input_html_extractor import InputHtmlExtractor
from src.common.user_agent_rotator import get_random_user_agent

MAX_RETRY = 15
DELAY_TIME = 1


class UpdateAdRemovedDate:
    def __init__(self, db: PropertyDatabase) -> None:
        self.db = db

    def request_html_from_url(self, url: str) -> BeautifulSoup:
        """Attempt to send a request to TenantApp page, setting the timeout for
        each request as 10s and number of retries as 15 max.

        Args:
            url (str): url to be requested

        Returns:
            BeautifulSoup: html content of the page
        """
        print("\nSending GET request to {0}".format(url))
        attempt = 0
        while attempt != MAX_RETRY:
            try:
                user_agent: dict[str, str] = get_random_user_agent()
                response = requests.get(url, timeout=15, headers=user_agent)

                # This code snippet below is for using requests_ip_rotator library
                # response = self.session.get(url, headers=user_agent)
                # print("Session: {0}".format(self.session))
                # print("Response: {0}".format(response))
                # if response.status_code != 200:
                #     continue

                print("Got response from {0} in {1} seconds".format(
                    url, response.elapsed.total_seconds()))
                return BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                print(
                    "Attempt #{0} failed with exception {1}".format(attempt, e))
                attempt += 1
                time.sleep(DELAY_TIME)

        return None

    def get_properties_on_market(self):
        on_market = self.db.select_all_where_not_off_market()
        properties = [{**row} for row in on_market]
        property_urls = [p['property_url'] for p in properties]
        return property_urls

    def update_ad_removed_date(self):
        transformer: Transformer = Transformer(InputHtmlExtractor(None))
        urls = self.get_properties_on_market()
        print("\nThere are {0} urls to be checked".format(len(urls)))
        for url in urls:
            print("\nChecking url... {0}".format(url))
            detail_page_html: BeautifulSoup = self.request_html_from_url(url)
            if detail_page_html is not None:
                print("Detail page not none")
                off_market_banner_exists = transformer.get_off_market_status(
                    detail_page_html)
                print("off market banner exists: {0}".format(
                    off_market_banner_exists))
                off_market = False if not off_market_banner_exists else True
                if off_market:
                    print("Updating row in DB....\n\n")
                    self.db.update_ad_removed_date(
                        url.split('/')[-1],
                        off_market,
                        datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == "__main__":
    db = PropertyDatabase()
    u = UpdateAdRemovedDate(db)
    u.update_ad_removed_date()
