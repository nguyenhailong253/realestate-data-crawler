import pytest
import pandas as pd
import src
from typing import List
from bs4 import BeautifulSoup

from .test_utils import read_html_from_local_file
from src.transformer import Transformer
from src.property_database import PropertyDatabase
from src.tenantapp_crawler import TenantAppCrawler
from src.property_dataclass import PropertyListing
from src.input_html_extractor import InputHtmlExtractor

# Ref: using mock in pytest https://medium.com/analytics-vidhya/how-to-use-pytest-mock-to-simulate-responses-1ea41e964161
# https://blogs.sap.com/2022/02/16/how-to-write-independent-unit-test-with-pytest-and-mock-techniques/

SINGLE_PROPERTY_CARD_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_card.html')
SINGLE_PROPERTY_PAGE_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_page.html')
PROPERTY_LIST_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/property_list_page.html')


def create_transformer_with_property_list_html():
    extractor: InputHtmlExtractor = InputHtmlExtractor(PROPERTY_LIST_HTML)
    transformer: Transformer = Transformer(extractor)
    return transformer


@pytest.fixture
def setup_helper(mocker):
    mocker.patch("src.property_database.PropertyDatabase.__init__",
                 return_value=None)
    db = PropertyDatabase()
    transformer: Transformer = create_transformer_with_property_list_html()
    crawler: TenantAppCrawler = TenantAppCrawler(db=db)
    property_listing_data: PropertyListing = crawler.collect_info_from_list_page(
        transformer, SINGLE_PROPERTY_CARD_HTML)
    return transformer, crawler, property_listing_data


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_collect_info_from_list_page_shouldPopulateFieldsWithAvailableData(setup_helper):
    property_listing_data = setup_helper[2]
    assert property_listing_data.address == '10 Trafalgar Street, RHYLL'
    assert property_listing_data.price == '$390pw'
    assert property_listing_data.agency_property_listings_url == 'https://tenantapp.com.au/Rentals/Agency/rwphillipIs'
    assert property_listing_data.agency_logo == 'https://inspectre.blob.core.windows.net/logos/rwphillipIs.jpg'
    assert len(property_listing_data.property_images) == 13
    assert property_listing_data.property_url == 'https://tenantapp.com.au/Rentals/ViewListing/3811184'
    assert property_listing_data.property_id == '3811184'
    assert property_listing_data.move_in_date == '31/10/22'
    assert property_listing_data.data_collection_date is not None


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_collect_info_from_detail_page_shouldPopulateFieldsWithAvailableData(setup_helper):
    transformer: Transformer = setup_helper[0]
    crawler: TenantAppCrawler = setup_helper[1]
    property_listing_data: PropertyListing = setup_helper[2]

    data: PropertyListing = crawler.collect_info_from_detail_page(
        transformer,
        SINGLE_PROPERTY_PAGE_HTML,
        property_listing_data)

    assert data.listing_title == '3-bedroom home located within the peaceful town Rhyll'
    assert data.listing_description is not None
    assert data.num_bedrooms == '3'
    assert data.num_bathrooms == '1'
    assert data.num_garages == '0'
    assert data.property_features == ['Furnished', 'Cooling']
    assert data.google_maps_location_url == 'https://www.google.com/maps/search/?api=1&query=10%20Trafalgar%20Street%2C%20RHYLL;&center=-38.4683211,145.2968764&zoom=20;'
    assert data.gps_coordinates == 'GPS Location: -38.4683211, 145.2968764'
    assert data.suburb == 'RHYLL'
    assert data.state_and_territory == 'VIC'
    assert data.postcode == '3923'
    assert data.agent_name == 'Keely Mabilia'
    assert data.off_market is False
    assert data.ad_details_included is True
    assert data.ad_removed_date is None
    assert data.ad_posted_date is not None


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_collect_data_for_all_properties_whenListingExisted_shouldNotSaveToDb(mocker, setup_helper):
    transformer: Transformer = setup_helper[0]
    crawler: TenantAppCrawler = setup_helper[1]
    property_listings: List[PropertyListing] = [SINGLE_PROPERTY_CARD_HTML]

    fake_listing: PropertyListing = PropertyListing()
    fake_listing.property_id = 'test'

    mocker.patch("src.tenantapp_crawler.TenantAppCrawler.collect_info_from_list_page",
                 return_value=fake_listing)
    mock_is_data_existed = mocker.patch("src.tenantapp_crawler.TenantAppCrawler.is_property_data_existed",
                                        return_value=True)
    mock_request_html_from_url = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.request_html_from_url', return_value=SINGLE_PROPERTY_PAGE_HTML)
    mock_collect_info_from_detail_page = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.collect_info_from_detail_page')
    mock_save_single = mocker.patch(
        'src.property_database.PropertyDatabase.save_single')
    crawler.collect_data_for_all_properties(property_listings, transformer)

    assert mock_is_data_existed.call_count == 1
    assert mock_request_html_from_url.call_count == 0
    assert mock_collect_info_from_detail_page.call_count == 0
    assert mock_save_single.call_count == 0


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_collect_data_for_all_properties_whenListingNotExisted_andDetailPageIsLoaded_shouldSaveToDb(mocker, setup_helper):
    transformer: Transformer = setup_helper[0]
    crawler: TenantAppCrawler = setup_helper[1]
    property_listings: List[PropertyListing] = [SINGLE_PROPERTY_CARD_HTML]

    mock_is_data_existed = mocker.patch("src.tenantapp_crawler.TenantAppCrawler.is_property_data_existed",
                                        return_value=False)
    mock_request_html_from_url = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.request_html_from_url', return_value=SINGLE_PROPERTY_PAGE_HTML)
    mock_collect_info_from_detail_page = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.collect_info_from_detail_page')
    mock_save_single = mocker.patch(
        'src.property_database.PropertyDatabase.save_single')
    crawler.collect_data_for_all_properties(property_listings, transformer)

    assert mock_is_data_existed.call_count == 1
    assert mock_request_html_from_url.call_count == 1
    assert mock_collect_info_from_detail_page.call_count == 1
    assert mock_save_single.call_count == 1


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_collect_data_for_all_properties_whenListingNotExisted_andDetailPageFailsToLoad_shouldNotSaveToDb(mocker, setup_helper):
    transformer: Transformer = setup_helper[0]
    crawler: TenantAppCrawler = setup_helper[1]
    property_listings: List[PropertyListing] = [SINGLE_PROPERTY_CARD_HTML]

    mock_is_data_existed = mocker.patch("src.tenantapp_crawler.TenantAppCrawler.is_property_data_existed",
                                        return_value=False)
    mock_request_html_from_url = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.request_html_from_url', return_value=None)
    mock_collect_info_from_detail_page = mocker.patch(
        'src.tenantapp_crawler.TenantAppCrawler.collect_info_from_detail_page')
    mock_save_single = mocker.patch(
        'src.property_database.PropertyDatabase.save_single')
    crawler.collect_data_for_all_properties(property_listings, transformer)

    assert mock_is_data_existed.call_count == 1
    assert mock_request_html_from_url.call_count == 1
    assert mock_collect_info_from_detail_page.call_count == 0
    assert mock_save_single.call_count == 0


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_is_property_data_existed_whenAtLeastOneEntryWithSamePropertyIdAndOffMarketFlag_shouldReturnTrue(mocker, setup_helper):
    crawler: TenantAppCrawler = setup_helper[1]
    mocker.patch("src.property_database.PropertyDatabase.select_with_same_id",
                 return_value=['one entry'])
    existed: bool = crawler.is_property_data_existed('fake_id')
    assert existed == True


@pytest.mark.skip(reason="currently not working when extracting 'id' direclty")
def test_is_property_data_existed_whenNoEntryWithSamePropertyIdAndOffMarketFlag_shouldReturnFalse(mocker, setup_helper):
    crawler: TenantAppCrawler = setup_helper[1]
    mocker.patch("src.property_database.PropertyDatabase.select_with_same_id",
                 return_value=[])
    existed: bool = crawler.is_property_data_existed('fake_id')
    assert existed == False
