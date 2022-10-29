import sys
import pytest
import src
from typing import List
from bs4 import BeautifulSoup

from .test_utils import read_html_from_local_file
from src.input_html_extractor import InputHtmlExtractor


SINGLE_PROPERTY_CARD_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_card.html')
SINGLE_PROPERTY_PAGE_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/single_property_page.html')
PROPERTY_LIST_HTML: BeautifulSoup = read_html_from_local_file(
    'tests/html/property_list_page.html')


property_list_extractor: InputHtmlExtractor = InputHtmlExtractor(
    PROPERTY_LIST_HTML)


def test_get_num_properties_whenUseCorrectHtmlTag_shouldReturnAllProperties():
    num_props: int = property_list_extractor.get_num_properties()
    assert num_props == 946


def test_get_num_pages_whenUseCorrectHtmlTag_shouldCalculateCorrectPages():
    num_pages: int = property_list_extractor.get_num_pages()
    assert num_pages == 95


def test_get_all_tags_without_attrs_whenNoHtmlInput_shouldUseHtmlOfWholePage():
    tags: List[BeautifulSoup] = property_list_extractor.get_all_tags_without_attrs(
        'span')
    assert len(tags) == 177


def test_get_all_tags_without_attrs_whenHtmlInputProvided_shouldNotUseHtmlOfWholePage():
    tags: List[BeautifulSoup] = property_list_extractor.get_all_tags_without_attrs(
        'span', SINGLE_PROPERTY_CARD_HTML)
    assert len(tags) == 14


def test_get_all_tags_with_attrs_whenNoHtmlInput_shouldUseHtmlOfWholePage():
    tags: List[BeautifulSoup] = property_list_extractor.get_all_tags_with_attrs(
        'span', 'class', 'd-inline-block')
    assert len(tags) == 30


def test_get_all_tags_with_attrs_whenHtmlInputProvided_shouldNotUseHtmlOfWholePage():
    tags: List[BeautifulSoup] = property_list_extractor.get_all_tags_with_attrs(
        'span', 'class', 'd-inline-block', SINGLE_PROPERTY_CARD_HTML)
    assert len(tags) == 3


def test_get_tag_content_without_attrs_whenUseCorrectHtmlTag_shouldReturnTrimmedText():
    content: str = property_list_extractor.get_tag_content_without_attrs(
        'h2', SINGLE_PROPERTY_CARD_HTML)
    assert content != '   10 Trafalgar Street, RHYLL   '
    assert content == '10 Trafalgar Street, RHYLL'


def test_get_tag_content_with_attrs_whenUseCorrectHtmlTag_shouldReturnTrimmedText():
    content: str = property_list_extractor.get_tag_content_with_attrs(
        'span', 'class', 'bold', SINGLE_PROPERTY_PAGE_HTML)
    assert content != '  Now  '
    assert content == 'Now'
