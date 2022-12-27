import os
import sys
import json
import math
import time
import random
import requests
import argparse
import pandas as pd

from typing import List
from bs4 import BeautifulSoup
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
from src.property_database import PropertyDatabase
from src.transformer import Transformer
from src.property_dataclass import PropertyListing
from src.input_html_extractor import InputHtmlExtractor
from src.common.constants import BASE_URL, STATES_URI
from src.common.user_agent_rotator import get_random_user_agent

MAX_RETRY = 15
DELAY_TIME = 1

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


class TenantAppCrawler:
    def __init__(self, db: PropertyDatabase) -> None:
        self.database = db

        # This code snippet below is for using requests_ip_rotator library
        # self.gateway = ApiGateway(BASE_URL, regions=EXTRA_REGIONS)
        # self.gateway.start()
        # self.session = requests.Session()
        # self.session.mount(BASE_URL, self.gateway)

    def collect_info_from_detail_page(
            self,
            transformer: Transformer,
            detail_page_html: BeautifulSoup,
            data: PropertyListing) -> PropertyListing:
        """Collect detailed info on the listing's dedicated page

        Args:
            transformer (Transformer): _description_
            detail_page_html (BeautifulSoup): html of the listing's page
            data (PropertyListing): data object holding general info from previous method

        Returns:
            PropertyListing: data object with more info from the detailed page
        """
        print('\nScraping address {0}'.format(data.address))
        print('Start scraping Detail url {0}...\n'.format(
            data.property_url))

        data.listing_title = transformer.get_listing_title(detail_page_html)
        data.listing_description = transformer.get_listing_description(
            detail_page_html)
        data.num_bedrooms = transformer.get_num_bedrooms(detail_page_html)
        data.num_bathrooms = transformer.get_num_bathrooms(detail_page_html)
        data.num_garages = transformer.get_num_garages(detail_page_html)
        data.property_features = transformer.get_property_features(
            detail_page_html)
        data.google_maps_location_url = transformer.get_google_maps_location_url(
            detail_page_html)
        data.gps_coordinates = transformer.get_gps_coordinates(
            detail_page_html)
        data.suburb = transformer.get_suburb(detail_page_html)
        data.state_and_territory = transformer.get_state_and_territory(
            detail_page_html)
        data.postcode = transformer.get_postcode(detail_page_html)
        data.agent_name = transformer.get_agent_name(detail_page_html)
        data.off_market = transformer.get_off_market_status(detail_page_html)
        data.ad_details_included = True
        data.ad_removed_date = transformer.get_ad_removed_date(data)
        data.ad_posted_date = data.data_collection_date
        data.etl_done = False

        agency_full_details = transformer.get_agency_details(detail_page_html)
        data.agency_name = transformer.get_agency_name_from_detail_page(detail_page_html)
        data.agency_address = transformer.get_agency_address_from_detail_page(agency_full_details, data.agency_name)

        return data

    def is_property_data_existed(self, property_id: str) -> bool:
        """Return true if at least 1 entry has same property_id and off_market = false

        A property can be listed and unlisted multiple times
        e.g Listed in Oct 2022, unlisted in Nov 2022, listed again in Nov 2024, unlisted in Jan 2025
        We want to capture every time it is listed or unlisted as separate entry in the DB

        The data we find on the website is ALWAYS going to be listed, aka off_market = false
        So before we insert a new entry to the DB, we need to get ALL entries that have the same 
        property_id and off_market == false flags.

        At any point in time, there should be ONE and ONLY ONE property_id with off_market = false

        Another background process will check each entry and update off_market flag to true and populate ad_removed_date field later

        if our DB has at least 1 matching entry -> we skip crawling the current property

        Args:
            property_id (str): id of property on tenantapp.com.au

        Returns:
            bool: whether our db already has a data entry for this property
        """
        existing_rows = self.database.select_with_same_id(property_id)
        return True if len(existing_rows) > 0 else False

    def collect_info_from_list_page(self, transformer: Transformer, listing: BeautifulSoup) -> PropertyListing:
        """Collect the most basic info related to a listing.
        An important item is the property_url, which is the link to the detail
        page for each individual listing. This will be used later for collection
        of more detailed info

        Args:
            transformer (Transformer): _description_
            listing (BeautifulSoup): html for general info of a single listing

        Returns:
            PropertyListing: _description_
        """
        data: PropertyListing = PropertyListing()

        data.address = transformer.get_address(listing)
        data.price = transformer.get_price(listing)
        data.agency_property_listings_url = transformer.get_agency_property_listings_url(
            listing)
        data.agency_logo = transformer.get_agency_logo(listing)
        data.property_images = transformer.get_property_images(listing)
        data.property_url = transformer.get_property_url(listing)
        data.property_id = transformer.get_property_id(listing)
        data.move_in_date = transformer.get_move_in_date(listing)
        data.data_collection_date = transformer.get_current_date()

        return data

    def collect_data_for_all_properties(
            self,
            property_listings: List[BeautifulSoup],
            transformer: Transformer) -> None:
        """For each listing of each state, collect general data and then go to
        each listing's detail page to collect more data. Once done, save to DB

        Args:
            property_listings (List[BeautifulSoup]): list of listings
            transformer (Transformer): _description_
        """
        for listing in property_listings:
            try:
                start_time = time.time()
                data: PropertyListing = self.collect_info_from_list_page(
                    transformer, listing)

                if self.is_property_data_existed(data.property_id):
                    print("\nData already existed: {0}\n".format(
                        data.property_id))
                    continue

                # Send a request to the detailed page of the current listing
                detail_page_html: BeautifulSoup = self.request_html_from_url(
                    data.property_url)

                if detail_page_html is not None:
                    data = self.collect_info_from_detail_page(
                        transformer,
                        detail_page_html,
                        data)

                    self.database.save_single(data)
                end_time = time.time()
                print("Scraping one property took in total: {0} seconds\n\n".format(
                    end_time - start_time))
            except Exception as e:
                print("Error when collecting data: {0}".format(e))

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

    def construct_url_with_pagination(self, state_uri: str) -> str:
        """tenantapp.com.au has a "Load more" type of pagination behaviour,
        as in when going to the next page, it just loads the data of the next 
        page and append to the current page.

        What we do here is to land on the first page, find out how many properties
        in total, take that divide by the number of properties displayed per page
        (10), we'll get the total number of pages.

        Then, construct the url of the final page, which should include data from
        page 1 to the final page.

        Args:
            state_uri (str): uri for each state

        Returns:
            str: url of the final page for each state
        """
        url: str = "{0}/Rentals/{1}#List".format(BASE_URL, state_uri)
        html: BeautifulSoup = self.request_html_from_url(url)
        if html is not None:
            extractor: InputHtmlExtractor = InputHtmlExtractor(html)

            print("URL: {0}".format(url))
            print("Num of properties {0}".format(
                extractor.get_num_properties()))
            num_pages = extractor.get_num_pages()
            print("Num of pages {0}\n\n".format(num_pages))

            url: str = "{0}/Rentals/{1}?page={2}#List".format(
                BASE_URL, state_uri, num_pages)
            return url
        return None

    def run(self, state_uri: str) -> bool:
        """Run the crawler for tenantapp.com.au for each state in Australia.

        Args:
            state_uri (str): uri for each state

        Returns:
            bool: completely crawled all available property listings
        """
        try:
            url: str = self.construct_url_with_pagination(state_uri)
            transformer: Transformer = Transformer(
                InputHtmlExtractor(self.request_html_from_url(url)))
            property_listings: List[BeautifulSoup] = transformer.get_all_properties(
            )
            print("There are {0} properties in {1}\n\n".format(
                len(property_listings), state_uri))

            self.collect_data_for_all_properties(
                property_listings, transformer)

            print("======= All done for {0}!!! ======\n".format(state_uri))
            # self.gateway.shutdown()
            return True
        except Exception as e:
            print("System crashed! Error: {0}".format(e))
            # self.gateway.shutdown()
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Web crawler for tenantapp.com.au")
    parser.add_argument(
        "-s",
        "--state",
        type=str,
        choices=STATES_URI.keys(),
        default="vic",
        help="Select a state in Australia to collect rental data from. Default is VIC"
    )

    # Parsing command args
    args = parser.parse_args()
    selected_state = args.state
    print("Selected state: {0}".format(selected_state))
    print("URI: {0}".format(STATES_URI[selected_state]))

    # Instantiate DB and crawler
    database = PropertyDatabase()
    crawler = TenantAppCrawler(db=database)

    # Start crawling...
    success = crawler.run(STATES_URI[selected_state])
    sys.exit(0) if success else sys.exit(1)
