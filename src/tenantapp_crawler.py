import json
import math
import random
import requests
import pandas as pd

from typing import List
from bs4 import BeautifulSoup
from src.transformer import Transformer
from src.input_html_extractor import InputHtmlExtractor
from src.common.constants import BASE_URL, STATES_URI
from src.common.user_agent_rotator import get_random_user_agent


class TenantAppCrawler:
    def __init__(self) -> None:
        self.rental_properties = []

    def collect_info_from_list_page(self, transformer, listing) -> dict[str, object]:
        result: dict[str, object] = {
            'address': transformer.get_address(listing),
            'price': transformer.get_price(listing),
            'agency_property_listings_url': transformer.get_agency_property_listings_url(listing),
            'agency_logo': transformer.get_agency_logo(listing),
            'property_images': transformer.get_property_images(listing),
            'num_bedrooms': transformer.get_num_bedrooms(listing),
            'num_bathrooms': transformer.get_num_bathrooms(listing),
            'num_garages': transformer.get_num_garages(listing),
            'property_url': transformer.get_property_url(listing),
            'property_id': transformer.get_property_id(listing),
            'move_in_date': transformer.get_move_in_date(listing),
            'data_collection_date': transformer.get_current_date(),
        }
        return result

    def collect_info_from_detail_page(self, result) -> dict[str, object]:
        print('Scraping address {0}'.format(result['address']))
        detail_url: str = result['property_url']
        print('Start scriping Detail url {0}...'.format(detail_url))
        detail_page_html: BeautifulSoup = self.request_html_from_url(
            detail_url)

        property_detail_extractor: InputHtmlExtractor = InputHtmlExtractor(
            detail_page_html)
        property_detail_transformer: Transformer = Transformer(
            property_detail_extractor)

        result['listing_title'] = property_detail_transformer.get_listing_title(
            detail_page_html)
        result['listing_description'] = property_detail_transformer.get_listing_description(
            detail_page_html)
        result['property_features'] = property_detail_transformer.get_property_features(
            detail_page_html)
        result['google_maps_location_url'] = property_detail_transformer.get_google_maps_location_url(
            detail_page_html)
        result['gps_coordinates'] = property_detail_transformer.get_gps_coordinates(
            detail_page_html)
        result['suburb'] = property_detail_transformer.get_suburb(
            detail_page_html)
        result['state'] = property_detail_transformer.get_state(
            detail_page_html)
        result['postcode'] = property_detail_transformer.get_postcode(
            detail_page_html)
        result['agent_name'] = property_detail_transformer.get_agent_name(
            detail_page_html)
        result['off_market'] = property_detail_transformer.get_off_market_status(
            detail_page_html)
        result['ad_details_included'] = True
        result['ad_removed_date'] = None
        result['ad_posted_date'] = result['data_collection_date']

        print('just a test, agent name {0}'.format(
            result['agent_name']))

        return result

    def run(self) -> None:
        for state_uri in STATES_URI:
            url: str = self.construct_url_with_pagination(state_uri)
            property_list_transformer: Transformer = Transformer(
                InputHtmlExtractor(self.request_html_from_url(url)))
            property_listings: List[BeautifulSoup] = property_list_transformer.get_all_properties(
            )
            print("There are {0} properties in {1}".format(
                len(property_listings), state_uri))

            for listing in property_listings:
                result = self.collect_info_from_list_page(
                    property_list_transformer, listing)
                result = self.collect_info_from_detail_page(result)

                self.rental_properties.append(result)

        print("All done, converting to CSV file")
        df = pd.DataFrame(self.rental_properties)
        df.to_csv('vic-results.csv', encoding='utf-8', index=True)

    def construct_url_with_pagination(self, state_uri) -> str:
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

        return BeautifulSoup(response.content, "html.parser")


if __name__ == "__main__":
    crawler = TenantAppCrawler()
    crawler.run()
