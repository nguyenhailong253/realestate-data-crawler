import pytest
import src
from typing import List
from bs4 import BeautifulSoup

from .test_utils import read_html_from_local_file
from src.transformer import Transformer
from src.input_html_extractor import InputHtmlExtractor
from src.property_dataclass import PropertyListing


SINGLE_PROPERTY_CARD_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_card.html')
SINGLE_PROPERTY_PAGE_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_page.html')
PROPERTY_LIST_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/property_list_page.html')
AGENCY_LISTINGS_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/agency_listings.html')


def create_transformer_with_property_list_html():
    extractor: InputHtmlExtractor = InputHtmlExtractor(PROPERTY_LIST_HTML)
    transformer: Transformer = Transformer(extractor)
    return transformer


transformer: Transformer = create_transformer_with_property_list_html()


def test_get_all_properties_whenUseCorrectHtmlTag_shouldReturnAllProperties():
    properties: List[BeautifulSoup] = transformer.get_all_properties()
    assert len(properties) == 10


def test_get_address_whenUseCorrectHtmlTag_shouldReturnCorrectAddress():
    address: str = transformer.get_address(
        SINGLE_PROPERTY_CARD_HTML)
    assert address == '10 Trafalgar Street, RHYLL'


def test_get_price_whenUseCorrectHtmlTag_shouldReturnCorrectPrice():
    price: str = transformer.get_price(
        SINGLE_PROPERTY_CARD_HTML)
    assert price == '$390pw'


def test_get_agency_property_listings_url_whenUseCorrectHtmlTag_shouldReturnCorrectUrl():
    url: str = transformer.get_agency_property_listings_url(
        SINGLE_PROPERTY_CARD_HTML)
    assert url == 'https://tenantapp.com.au/Rentals/Agency/rwphillipIs'


def test_get_agency_logo_whenUseCorrectHtmlTag_shouldReturnCorrectUrl():
    url: str = transformer.get_agency_logo(
        SINGLE_PROPERTY_CARD_HTML)
    assert url == 'https://inspectre.blob.core.windows.net/logos/rwphillipIs.jpg'


def test_get_property_images_whenUseCorrectHtmlTag_shouldReturnCorrectListOfImageUrls():
    images: List[str] = transformer.get_property_images(
        SINGLE_PROPERTY_CARD_HTML)
    assert len(images) == 13


def test_get_beds_baths_garages_whenUseCorrectHtmlTag_shouldReturnCorrectNumbers():
    beds_baths_garages: List[str] = transformer.get_beds_baths_garages(
        SINGLE_PROPERTY_PAGE_HTML)
    assert beds_baths_garages == ['3', '1', '0']


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_get_property_id__whenUseCorrectHtmlTag_shouldReturnCorrectId():
    property_id: str = transformer.get_property_id(
        SINGLE_PROPERTY_CARD_HTML)
    assert property_id == '3811184'


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_get_property_url__whenUseCorrectHtmlTag_shouldReturnCorrectUrl():
    property_url: str = transformer.get_property_url(
        SINGLE_PROPERTY_CARD_HTML)
    assert property_url == 'https://tenantapp.com.au/Rentals/ViewListing/3811184'


def test_get_move_in_date_whenUseCorrectHtmlTag_shouldReturnCorrectDate():
    move_in_date: str = transformer.get_move_in_date(
        SINGLE_PROPERTY_CARD_HTML)
    assert move_in_date == '31/10/22'


def test_get_listing_title_whenUseCorrectHtmlTag_shouldReturnCorrectTitle():
    title: str = transformer.get_listing_title(
        SINGLE_PROPERTY_PAGE_HTML)
    assert title == '3-bedroom home located within the peaceful town Rhyll'


def test_get_property_features_whenUseCorrectHtmlTag_shouldReturnCorrectTitle():
    features: List[str] = transformer.get_property_features(
        SINGLE_PROPERTY_PAGE_HTML)
    assert features == ['Furnished', 'Cooling']


def test_get_google_maps_location_url_whenUseCorrectHtmlTag_shouldReturnCorrectUrl():
    url: str = transformer.get_google_maps_location_url(
        SINGLE_PROPERTY_PAGE_HTML)
    assert url == 'https://www.google.com/maps/search/?api=1&query=10%20Trafalgar%20Street%2C%20RHYLL;&center=-38.4683211,145.2968764&zoom=20;'


def test_get_gps_coordinates_whenUseCorrectHtmlTag_shouldReturnCorrectCoordinates():
    gps: str = transformer.get_gps_coordinates(
        SINGLE_PROPERTY_PAGE_HTML)
    assert gps == 'GPS Location: -38.4683211, 145.2968764'


def test_get_suburb_whenUseCorrectHtmlTag_shouldReturnCorrectSuburb():
    suburb: str = transformer.get_suburb(
        SINGLE_PROPERTY_PAGE_HTML)
    assert suburb == 'RHYLL'


def test_get_state_and_territory_whenUseCorrectHtmlTag_shouldReturnCorrectState():
    state_and_territory: str = transformer.get_state_and_territory(
        SINGLE_PROPERTY_PAGE_HTML)
    assert state_and_territory == 'VIC'


def test_get_postcode_whenUseCorrectHtmlTag_shouldReturnCorrectPostcode():
    postcode: str = transformer.get_postcode(
        SINGLE_PROPERTY_PAGE_HTML)
    assert postcode == '3923'


def test_get_agent_name_whenUseCorrectHtmlTag_shouldReturnCorrectName():
    name: str = transformer.get_agent_name(
        SINGLE_PROPERTY_PAGE_HTML)
    assert name == 'Keely Mabilia'


def test_get_off_market_status_whenUseCorrectHtmlTag_shouldReturnCorrectStatus():
    off_market: bool = transformer.get_off_market_status(
        SINGLE_PROPERTY_PAGE_HTML)
    assert off_market == False


def test_get_ad_removed_date_whenNotOffMarket_shouldReturnNone():
    fake_data = PropertyListing()
    fake_data.off_market = False
    fake_data.data_collection_date = '31-10-2022'
    ad_removed_date: str = transformer.get_ad_removed_date(fake_data)
    assert ad_removed_date is None


def test_get_ad_removed_date_whenOffMarket_shouldReturnDataCollectionDate():
    fake_data = PropertyListing()
    fake_data.off_market = True
    fake_data.data_collection_date = '31-10-2022'
    ad_removed_date: str = transformer.get_ad_removed_date(fake_data)
    assert ad_removed_date == '31-10-2022'


def test_get_agency_banner_whenUseCorrectHtmlTag_shouldReturnCorrectAgencyNameAndAddress():
    banner: str = transformer.get_agency_banner(
        AGENCY_LISTINGS_HTML)
    assert banner == 'Barry Plant (Mitchell Shire) 147 Powlett Street, Kilmore, VIC 3764'


def test_get_agency_name_whenUseCorrectHtmlTag_shouldReturnCorrectAgencyName():
    name: str = transformer.get_agency_name(
        AGENCY_LISTINGS_HTML)
    assert name == 'Barry Plant (Mitchell Shire)'


def test_get_agency_address_shouldReturnCorrectAgencyAddress():
    banner = 'Barry Plant (Mitchell Shire) 147 Powlett Street, Kilmore, VIC 3764'
    name = 'Barry Plant (Mitchell Shire)'
    addr: str = transformer.get_agency_address(banner, name)
    assert addr == '147 Powlett Street, Kilmore, VIC 3764'
