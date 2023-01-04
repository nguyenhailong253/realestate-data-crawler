import time
import requests
import argparse
import logging
from datetime import datetime
from bs4 import BeautifulSoup

from src.transformer import Transformer
from src.property_database import PropertyDatabase
from src.input_html_extractor import InputHtmlExtractor
from src.common.user_agent_rotator import get_random_user_agent
from tests.test_utils import read_html_from_local_file, write_html_to_local_file

MAX_RETRY = 15
DELAY_TIME = 1


class AgencyCrawler:
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

    def get_properties_without_agency_details(self):
        on_market = self.db.select_where_no_agency_details()
        properties = [{**row} for row in on_market]
        return properties

    def get_agency_details(self):
        print(f"\nCollecting agency names and addresses...\n")
        transformer: Transformer = Transformer(InputHtmlExtractor(None))
        properties = self.get_properties_without_agency_details()
        print("\nThere are {0} urls to be checked".format(len(properties)))
        count: int = 0

        # 59 d minutes from now - due to 1hr time limit on CircleCI Free Plan
        timeout = time.time() + 60*59
        for p in properties:
            try:
                url = p['agency_property_listings_url']
                if time.time() > timeout:
                    print(f"Reaching time limit, stopping now...")
                    break
                count += 1
                print(
                    f"\n{count}. Checking url... {url} for property id {p['property_id']}\n")
                agency_page: BeautifulSoup = self.request_html_from_url(url)
                if agency_page is not None:
                    agency_banner = transformer.get_agency_banner(agency_page)
                    print(f"Agency banner: {agency_banner}\n")

                    agency_name = transformer.get_agency_name(agency_page)
                    print(f"Agency name: {agency_name}")
                    agency_address = transformer.get_agency_address(
                        agency_banner, agency_name)
                    print(f"Agency address: {agency_address}\n")
                    print("Updating row in DB....\n\n")
                    self.db.update_agency_details(
                        p['property_id'], url, agency_name, agency_address)
            except Exception as e:
                logging.exception(f"Failed to get agency detail: {e}")
                if "'NoneType' object has no attribute 'get_text'" in str(e):
                    print("Saving agency name and address as N/A")
                    self.db.update_agency_details(
                        p['property_id'], url, "N/A", "N/A")


if __name__ == "__main__":
    db = PropertyDatabase()
    ac = AgencyCrawler(db)
    ac.get_agency_details()
