import os
import pandas as pd
from sqlalchemy import (
    create_engine, MetaData, Table, insert, select, and_, update, or_
)
from sqlalchemy.orm import sessionmaker, Session

from typing import List
from src.property_dataclass import PropertyListing

DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_SCHEMA = os.environ.get('DB_SCHEMA')
DB_CONN_POOL_SIZE = 50

# Ref: using sqlalchemy https://towardsdatascience.com/sqlalchemy-python-tutorial-79a577141a91


class PropertyDatabase:
    def __init__(self):
        self.dbEngine = self.create_db_engine()
        self.conn = self.dbEngine.connect()
        self.metadata = MetaData(schema=DB_SCHEMA)
        self.table = self.get_real_estate_table()

    def create_db_engine(self):
        dbUrl = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        return create_engine(dbUrl, pool_size=DB_CONN_POOL_SIZE)

    def get_real_estate_table(self) -> Table:
        """Define the table entity based on the table from DB

        Returns:
            Table: _description_
        """
        realestate_table = Table(
            'propertylistings', self.metadata, autoload=True, autoload_with=self.dbEngine)
        return realestate_table

    def select_all(self) -> None:
        """SELECT * FROM TABLE

        Returns:
            _type_: _description_
        """
        # results = [{**row} for row in item]  # https://stackoverflow.com/a/56098483
        return self.conn.execute(select([self.table])).fetchall()

    def select_all_where_not_off_market(self,
                                        state_and_territory: str,
                                        offset: int = 0,
                                        limit: int = 3000) -> None:
        """SELECT * FROM TABLE WHERE off_market = false

        Returns:
            _type_: _description_
        """
        query = select([self.table]).where(
            and_(self.table.columns.off_market == False,
                 self.table.columns.ad_removed_date == None,
                 self.table.columns.state_and_territory == state_and_territory
                 )).order_by(self.table.columns.ad_posted_date).offset(offset).limit(limit)
        return self.conn.execute(query).fetchall()

    def select_where_no_agency_details(self) -> None:
        """SELECT * FROM TABLE WHERE agency_name is Null OR agency_address is Null

        Returns:
            _type_: _description_
        """
        query = select([self.table]).where(
            or_(self.table.columns.agency_name == None,
                self.table.columns.agency_address == None
                )).order_by(self.table.columns.ad_posted_date)
        return self.conn.execute(query).fetchall()

    def select_with_same_id(self, property_id: str):
        """Check if there's an existing entry with same id and also still on the market

        Args:
            property_id (str): id of the listing

        Returns:
            _type_: _description_
        """
        query = select([self.table]).where(
            and_(self.table.columns.property_id == property_id,
                 self.table.columns.off_market == False))
        return self.conn.execute(query).fetchall()

    def save_bulk(self, data: List[PropertyListing]) -> None:
        """Save a list of data to DB in one go

        Args:
            data (List[PropertyListing]): _description_
        """
        data_type_to_dict = [vars(listing) for listing in data]
        print("Saving data to DB....")
        query = insert(self.table)
        self.conn.execute(query, data_type_to_dict)

    def save_single(self, data: PropertyListing) -> None:
        """Save 1 item to DB

        Args:
            data (PropertyListing): _description_
        """
        data_type_to_dict = vars(data)
        query = insert(self.table).values(data_type_to_dict)
        self.conn.execute(query)

    def update_ad_removed_date(self, property_id: str, off_market: bool, ad_removed_date: str) -> None:
        query = update(self.table).values(off_market=off_market,
                                          ad_removed_date=ad_removed_date).where(
                                              and_(self.table.columns.property_id == property_id,
                                                   self.table.columns.ad_removed_date == None))
        self.conn.execute(query)

    def update_agency_details(self, property_id: str, agency_url: str, agency_name: bool, agency_address: str) -> None:
        query = update(self.table).values(agency_name=agency_name,
                                          agency_address=agency_address).where(
                                              and_(self.table.columns.property_id == property_id,
                                                   self.table.columns.agency_property_listings_url == agency_url))
        self.conn.execute(query)
