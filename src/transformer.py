from typing import List
from datetime import datetime
from bs4 import BeautifulSoup

from src.common.constants import (
    BASE_URL,
    TAG_NAME,
    ATTRIBUTE_NAME,
    ATTRIBUTE_VALUE,
    PROPERTY_LIST_HTML_ATTRS,
    PROPERTY_DETAIL_HTML_ATTRS
)
from src.input_html_extractor import InputHtmlExtractor


class Transformer:
    def __init__(self, extractor: InputHtmlExtractor):
        self.extractor = extractor

    def get_all_properties(self) -> List[BeautifulSoup]:
        self.properties = self.extractor.get_all_tags_by_class(
            PROPERTY_LIST_HTML_ATTRS['property'][TAG_NAME],
            PROPERTY_LIST_HTML_ATTRS['property'][ATTRIBUTE_VALUE])
        return self.properties

    def get_address(self, listing: BeautifulSoup) -> str:
        return self.extractor.get_tag_content_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['address'][TAG_NAME], listing)

    def get_price(self, listing: BeautifulSoup) -> str:
        return self.extractor.get_tag_content_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['price'][TAG_NAME], listing)

    def get_agency_property_listings_url(self, listing: BeautifulSoup) -> str:
        uri: str = self.extractor.get_href(
            PROPERTY_DETAIL_HTML_ATTRS['agency_properties_url'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['agency_properties_url'][ATTRIBUTE_VALUE],
            listing)
        return "{0}{1}".format(BASE_URL, uri)

    def get_agency_logo(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['agency_properties_url'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['agency_properties_url'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['agency_properties_url'][ATTRIBUTE_VALUE],
            listing)
        image: str = self.extractor.get_img(html_block=parent_tag)
        return image

    def get_property_images(self, listing: BeautifulSoup) -> List[str]:
        img_tags: List[BeautifulSoup] = self.extractor.get_all_tags_by_class(
            PROPERTY_DETAIL_HTML_ATTRS['property_images'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['property_images'][ATTRIBUTE_VALUE],
            listing)
        imgs: List[str] = []
        for img_tag in img_tags:
            imgs.append(img_tag['src'])
        return imgs

    def get_beds_baths_garages(self, listing: BeautifulSoup) -> List[str]:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['beds_baths_garages'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['beds_baths_garages'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['beds_baths_garages'][ATTRIBUTE_VALUE])
        child_tags: List[BeautifulSoup] = self.extractor.get_all_tags_by_class(
            PROPERTY_DETAIL_HTML_ATTRS['beds_baths_garages_subtags'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['beds_baths_garages_subtags'][ATTRIBUTE_VALUE],
            parent_tag)
        beds_baths_garages = []
        for child_tag in child_tags:
            beds_baths_garages.append(child_tag.get_text())
        return beds_baths_garages

    def get_num_bedrooms(self, listing: BeautifulSoup) -> str:
        return self.get_beds_baths_garages(listing)[0]

    def get_num_bathrooms(self, listing: BeautifulSoup) -> str:
        return self.get_beds_baths_garages(listing)[1]

    def get_num_garages(self, listing: BeautifulSoup) -> str:
        return self.get_beds_baths_garages(listing)[2]

    def get_property_id(self, listing: BeautifulSoup) -> str:
        id_attr_val: str = listing['id']
        property_id: str = id_attr_val.split('-')[1]
        return property_id

    def get_property_url(self, listing: BeautifulSoup) -> str:
        property_url: str = "{0}/Rentals/ViewListing/{1}".format(
            BASE_URL, self.get_property_id(listing))
        return property_url

    def get_move_in_date(self, listing: BeautifulSoup) -> str:
        move_in_date: str = self.extractor.get_tag_content_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['move_in_date'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['move_in_date'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['move_in_date'][ATTRIBUTE_VALUE])
        return move_in_date

    def get_current_date(self) -> str:
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    def get_listing_title(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['listing_title'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['listing_title'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['listing_title'][ATTRIBUTE_VALUE],
            listing)
        return self.extractor.get_tag_content_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['listing_title_subtag'][TAG_NAME],
            parent_tag)

    def get_listing_description(self, listing: BeautifulSoup) -> str:
        return self.extractor.get_tag_content_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['listing_description'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['listing_description'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['listing_description'][ATTRIBUTE_VALUE],
            listing).replace("\n", "\\n")  # https://datascience.stackexchange.com/a/81361

    def get_property_features(self, listing: BeautifulSoup) -> List[str]:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['property_features'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['property_features'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['property_features'][ATTRIBUTE_VALUE],
            listing)
        child_tags: List[BeautifulSoup] = self.extractor.get_all_tags_by_class(
            PROPERTY_DETAIL_HTML_ATTRS['property_features_subtag'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['property_features_subtag'][ATTRIBUTE_VALUE],
            parent_tag)
        features = []
        for child_tag in child_tags:
            features.append(child_tag.get_text())
        return features

    def get_google_maps_location_url(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['google_maps_location_url'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['google_maps_location_url'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['google_maps_location_url'][ATTRIBUTE_VALUE],
            listing)
        maps_url: str = self.extractor.get_href(
            None, None, html_block=parent_tag)
        return maps_url

    def get_gps_coordinates(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['gps_coordinates'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['gps_coordinates'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['gps_coordinates'][ATTRIBUTE_VALUE],
            listing)
        gps_coordinates = self.extractor.get_all_tags_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['gps_coordinates_subtag'][TAG_NAME],
            html_block=parent_tag)[0]
        return gps_coordinates.get_text().strip()

    def get_suburb_info_list(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['suburb_info'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['suburb_info'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['suburb_info'][ATTRIBUTE_VALUE],
            listing)
        suburb_info = self.extractor.get_all_tags_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['suburb_info_subtag'][TAG_NAME],
            html_block=parent_tag)[1]
        return suburb_info.get_text().strip().split()

    def get_suburb(self, listing: BeautifulSoup) -> str:
        suburb_info = self.get_suburb_info_list(listing)
        return " ".join(suburb_info[1:-2])

    def get_state(self, listing: BeautifulSoup) -> str:
        suburb_info = self.get_suburb_info_list(listing)
        return suburb_info[-2]

    def get_postcode(self, listing: BeautifulSoup) -> str:
        suburb_info = self.get_suburb_info_list(listing)
        return suburb_info[-1]

    def get_agent_name(self, listing: BeautifulSoup) -> str:
        parent_tag: BeautifulSoup = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['agent_name'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['agent_name'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['agent_name'][ATTRIBUTE_VALUE],
            listing)
        return self.extractor.get_tag_content_without_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['agent_name_subtag'][TAG_NAME],
            parent_tag)

    def get_off_market_status(self, listing: BeautifulSoup) -> bool:
        off_market = self.extractor.get_single_tag_with_attrs(
            PROPERTY_DETAIL_HTML_ATTRS['off_market_status'][TAG_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['off_market_status'][ATTRIBUTE_NAME],
            PROPERTY_DETAIL_HTML_ATTRS['off_market_status'][ATTRIBUTE_VALUE],
            listing)
        return False if not off_market else True
