"""This program will query our DB and check which one is still on the market 
(off_market = false) and then query tenantapp.com.au to check if it's still on
or not. If it's not, update off_market = true and then update ad_removed_date
"""
import time
import requests
import argparse
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

                print("Got response from {0} in {1} seconds".format(
                    url, response.elapsed.total_seconds()))
                return BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                print(
                    "Attempt #{0} failed with exception {1}".format(attempt, e))
                attempt += 1
                time.sleep(DELAY_TIME)

        return None

    def get_properties_on_market(self,
                                 state_and_territory: str,
                                 offset: int = 0,
                                 limit: int = 3000):
        on_market = self.db.select_all_where_not_off_market(
            state_and_territory, offset, limit)
        properties = [{**row} for row in on_market]
        property_urls = [p['property_url'] for p in properties]
        return property_urls

    def update_ad_removed_date(self,
                               state_and_territory: str = 'VIC',
                               offset: int = 0,
                               limit: int = 3000):
        print(f"\nUpdating for {state_and_territory}\n\n")
        transformer: Transformer = Transformer(InputHtmlExtractor(None))
        urls: list[str] = self.get_properties_on_market(
            state_and_territory, offset, limit)
        print("\nThere are {0} urls to be checked".format(len(urls)))
        count: int = 0

        # 59 d minutes from now - due to 1hr time limit on CircleCI Free Plan
        timeout = time.time() + 60*59
        for url in urls:
            if time.time() > timeout:
                print(f"Reaching time limit, stopping now...")
                break
            count += 1
            print(f"\n{count}. Checking url... {url}")
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
    STATES = [
        'VICTORIA',
        'TAS',
        'Vic',
        'vic',
        'Victoria',
        'Qld',
        'qld',
        'WA',  # alot
        'Wa',  # alot
        'ACT',  # alot
        'VIC',  # most
        'NSW',  # most
        'NT',
        'QLD',  # alot
        'nsw',
        'Nsw',
        'sa',
        'SA',  # alot
        'Queensland',
        'QUEENSLAND',
        'wa',
        'Tas',
        'TASMANIA',
        'Tasmania',
    ]
    parser = argparse.ArgumentParser(
        description="Web crawler for tenantapp.com.au")

    parser.add_argument(
        "-s",
        "--state",
        type=str,
        choices=STATES,
        default="VIC",
        help="Select a state in Australia to collect rental data from. Default is VIC"
    )

    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Offset the starting point for which the next rows should return from a query",
        required=False
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3000,
        help="Limit nunber of rows that the select query should return",
        required=False
    )

    # Parsing command args
    args = parser.parse_args()
    selected_state = args.state
    print(f"Selected state: {selected_state}")

    offset = args.offset
    print(f"Selected offset: {offset}")

    limit = args.limit
    print(f"Selected limit: {limit}")

    db = PropertyDatabase()
    u = UpdateAdRemovedDate(db)
    u.update_ad_removed_date(selected_state, offset, limit)
