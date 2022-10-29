import math
import requests
from typing import List
from itertools import cycle
from bs4 import BeautifulSoup

from src.common.constants import (
    PROPERTIES_PER_PAGE,
    PROPERTY_LIST_HTML_ATTRS,
    TAG_NAME, ATTRIBUTE_VALUE
)


class InputHtmlExtractor:
    def __init__(self, html: BeautifulSoup) -> None:
        self.raw_html_page = html

    def get_raw_html(self) -> BeautifulSoup:
        return self.raw_html_page

    def get_num_properties(self) -> int:
        self.num_properties: str = self.raw_html_page.find(
            PROPERTY_LIST_HTML_ATTRS['num_properties'][TAG_NAME],
            class_=PROPERTY_LIST_HTML_ATTRS['num_properties'][ATTRIBUTE_VALUE]).get_text().strip()
        return int(self.num_properties)

    def get_num_pages(self) -> int:
        self.num_pages: int = math.ceil(
            self.get_num_properties()/PROPERTIES_PER_PAGE)
        return self.num_pages

    def get_all_tags_without_attrs(self, tag: str, html_block: BeautifulSoup = None) -> List[BeautifulSoup]:
        html_block: BeautifulSoup = html_block if html_block is not None else self.raw_html_page
        tags: List[BeautifulSoup] = html_block.find_all(tag)
        return tags

    def get_all_tags_with_attrs(self, tag: str, attr_key: str, attr_val: str, html_block: BeautifulSoup = None) -> List[BeautifulSoup]:
        html_block: BeautifulSoup = html_block if html_block is not None else self.raw_html_page
        tags: List[BeautifulSoup] = html_block.find_all(
            tag, attrs={attr_key: attr_val})
        return tags

    def get_all_tags_by_class(self, tag: str, className: str, html_block: BeautifulSoup = None) -> List[BeautifulSoup]:
        return self.get_all_tags_with_attrs(tag, 'class', className, html_block)

    def get_single_tag_without_attrs(self, tag: str, html_block: BeautifulSoup = None) -> BeautifulSoup:
        html_block: BeautifulSoup = html_block if html_block is not None else self.raw_html_page
        child_tag: BeautifulSoup = html_block.find(tag)
        return child_tag

    def get_single_tag_with_attrs(self, tag: str, attr_key: str, attr_val: str, html_block: BeautifulSoup = None) -> BeautifulSoup:
        html_block: BeautifulSoup = html_block if html_block is not None else self.raw_html_page
        child_tag: str = html_block.find(tag, attrs={attr_key: attr_val})
        return child_tag

    def get_tag_content_without_attrs(self, tag: str, html_block: BeautifulSoup = None) -> str:
        content: str = self.get_single_tag_without_attrs(
            tag, html_block).get_text().strip()
        return content

    def get_tag_content_with_attrs(self, tag: str, attr_key: str, attr_val: str, html_block: BeautifulSoup = None) -> str:
        content: str = self.get_single_tag_with_attrs(
            tag, attr_key, attr_val, html_block).get_text().strip()
        return content

    def get_href(self, attr_key: str, attr_val: str, html_block: BeautifulSoup = None, tag: str = 'a') -> str:
        content: str = self.get_single_tag_with_attrs(
            tag, attr_key, attr_val, html_block)
        return content['href']

    def get_img(self, attr_key: str = None, attr_val: str = None, html_block: BeautifulSoup = None,  tag: str = 'img') -> str:
        content: str = self.get_single_tag_with_attrs(
            tag, attr_key, attr_val, html_block)
        return content['src']
