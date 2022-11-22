import dataclasses
from typing import List


@dataclasses.dataclass(init=False)
class PropertyListing:
    address: str
    price: str
    agency_property_listings_url: str
    agency_logo: str
    property_images: List[str]
    property_url: str
    property_id: str
    move_in_date: str
    listing_title: str
    listing_description: str
    num_bedrooms: str
    num_bathrooms: str
    num_garages: str
    property_features: List[str]
    google_maps_location_url: str
    gps_coordinates: str
    suburb: str
    state_and_territory: str
    postcode: str
    agent_name: str
    off_market: bool
    ad_details_included: bool
    ad_removed_date: str
    ad_posted_date: str
    data_collection_date: str
    agency_name: str
    agency_address: str
    etl_done: bool

    def __post_init__(self):
        if self.ad_details_included is None:
            self.ad_details_included = False
        if self.etl_done is None:
            self.etl_done = False
