BASE_URL: str = 'https://tenantapp.com.au'

STATES_URI: list[str] = [
    'wa-rental-properties',
    'act-rental-properties',
    'sa-rental-properties',
    'tas-rental-properties',
    'qld-rental-properties',
    'nsw-rental-properties',
    'vic-rental-properties',
    'nt-rental-properties'
]

PROPERTIES_PER_PAGE: int = 10

TAG_NAME = 'tag'
ATTRIBUTE_NAME = 'attribute'
ATTRIBUTE_VALUE = 'value'

PROPERTY_LIST_HTML_ATTRS: dict[str, str] = {
    'property': {
        TAG_NAME: 'article',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-card-container',
    },
    'num_properties': {
        TAG_NAME: 'b',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'search-text-highlighted',
    },
}

PROPERTY_DETAIL_HTML_ATTRS: dict[str, str] = {
    'address': {
        TAG_NAME: 'h2',
    },
    'price': {
        TAG_NAME: 'h3',
    },
    'agency_properties_url': {
        TAG_NAME: 'a',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-card-banner-link',
    },
    'agency_logo': {
        TAG_NAME: 'a',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-card-banner-link',
    },
    'property_images': {
        TAG_NAME: 'img',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'carousel-image',
    },
    'beds_baths_garages': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-summary-details',
    },
    'beds_baths_garages_subtags': {
        TAG_NAME: 'span',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'd-inline-block',
    },
    'property_href': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'card-footer',
    },
    'move_in_date': {
        TAG_NAME: 'span',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'bold',
    },
    'listing_title': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'body-content-info',
    },
    'listing_title_subtag': {
        TAG_NAME: 'h2',
    },
    'listing_description': {
        TAG_NAME: 'p',
        ATTRIBUTE_NAME: 'id',
        ATTRIBUTE_VALUE: 'collapsePropertyDescription',
    },
    'property_features': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'features',
    },
    'property_features_subtag': {
        TAG_NAME: 'h3',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'm-0',
    },
    'google_maps_location_url': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-location',
    },
    'gps_coordinates': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-location',
    },
    'gps_coordinates_subtag': {
        TAG_NAME: 'p',
    },
    'suburb_info': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'property-location',
    },
    'suburb_info_subtag': {
        TAG_NAME: 'p',
    },
    'agent_name': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'class',
        ATTRIBUTE_VALUE: 'agent-contact-card',
    },
    'agent_name_subtag': {
        TAG_NAME: 'h3',
    },
    'off_market_status': {
        TAG_NAME: 'div',
        ATTRIBUTE_NAME: 'id',
        ATTRIBUTE_VALUE: 'divOffMarketBanner',
    },
}

DEFAULT_USER_AGENT = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}
