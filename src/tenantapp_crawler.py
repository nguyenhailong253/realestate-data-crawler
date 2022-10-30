import json
import math
import time
import random
import requests
import pandas as pd

from typing import List
from bs4 import BeautifulSoup
from src.property_database import PropertyDatabase
from src.transformer import Transformer
from src.property_dataclass import PropertyListing
from src.input_html_extractor import InputHtmlExtractor
from src.common.constants import BASE_URL, STATES_URI
from src.common.user_agent_rotator import get_random_user_agent


class TenantAppCrawler:
    def __init__(self) -> None:
        self.rental_properties = []
        self.database = PropertyDatabase(isCsv=True)

    def collect_info_from_list_page(self, transformer: Transformer, listing: BeautifulSoup) -> PropertyListing:
        data = PropertyListing()
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

    def collect_info_from_detail_page(
            self,
            transformer: Transformer,
            detail_page_html: BeautifulSoup,
            data: PropertyListing) -> PropertyListing:
        print('Scraping address {0}'.format(data.address))
        print('Start scriping Detail url {0}...'.format(
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
        data.ad_removed_date = None
        data.ad_posted_date = data.data_collection_date

        return data

    def run(self, states_uris: List[str]) -> None:
        for state_uri in states_uris:
            url: str = self.construct_url_with_pagination(state_uri)
            transformer: Transformer = Transformer(
                InputHtmlExtractor(self.request_html_from_url(url)))
            property_listings: List[BeautifulSoup] = transformer.get_all_properties(
            )
            print("There are {0} properties in {1}".format(
                len(property_listings), state_uri))

            for listing in property_listings:
                data = self.collect_info_from_list_page(transformer, listing)

                detail_page_html: BeautifulSoup = self.request_html_from_url(
                    data.property_url)

                if detail_page_html is None:
                    data.ad_details_included = False
                else:
                    data = self.collect_info_from_detail_page(
                        transformer,
                        detail_page_html,
                        data)

                self.rental_properties.append(data)

        print("All done, converting to CSV file")
        self.database.save(self.rental_properties)

    def construct_url_with_pagination(self, state_uri: str) -> str:
        url: str = "{0}/Rentals/{1}#List".format(BASE_URL, state_uri)
        html: BeautifulSoup = self.request_html_from_url(url)
        property_list_extractor: InputHtmlExtractor = InputHtmlExtractor(html)

        print("URL: {0}".format(url))
        print("Num of properties {0}".format(
            property_list_extractor.get_num_properties()))
        num_pages = property_list_extractor.get_num_pages()
        print("Num of pages {0}".format(num_pages))

        url: str = "{0}/Rentals/{1}?page={2}#List".format(
            BASE_URL, state_uri, num_pages)
        return url

    def request_html_from_url(self, url: str) -> BeautifulSoup:
        print("Sending GET request to {0}".format(url))
        attempt = 0
        while attempt != 10:
            try:
                user_agent: dict[str, str] = get_random_user_agent()
                response = requests.get(url, timeout=10, headers=user_agent)
                print("Got response from {0} in {1} seconds".format(
                    url, response.elapsed.total_seconds()))
                break
            except Exception as e:
                print(
                    "Attempt #{0} failed with exception {1}".format(attempt, e))
                attempt += 1
                time.sleep(1)

        return None if attempt == 10 else BeautifulSoup(response.content, "html.parser")


if __name__ == "__main__":
    crawler = TenantAppCrawler()
    crawler.run(STATES_URI)
