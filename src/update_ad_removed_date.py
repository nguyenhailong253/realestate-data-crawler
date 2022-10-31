"""This program will query our DB and check which one is still on the market 
(off_market = false) and then query tenantapp.com.au to check if it's still on
or not. If it's not, update off_market = true and then update ad_removed_date
"""
from src.property_database import PropertyDatabase


class UpdateAdRemovedDate:
    def __init__(self, db: PropertyDatabase) -> None:
        self.db = db

    def get_properties_on_market(self):
        # Call db to query all rows (maybe just get the property_url) with off_market = false
        pass
    
    def update_ad_removed_date(self):
        # For each property_url, check div for property off market
        # if yes, update row in DB: off_market = true, ad_removed_date = today
        # else, do nothing, skip
        pass


if __name__ == "__main__":
    database = PropertyDatabase()
