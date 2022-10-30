import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, insert, select
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
        realestate_table = Table(
            'propertylistings', self.metadata, autoload=True, autoload_with=self.dbEngine)
        return realestate_table

    def select_all(self) -> None:
        return self.conn.execute(select([self.table])).fetchall()

    def select_single(self, property_id: str):
        pass

    def save_bulk(self, data: List[PropertyListing]) -> None:
        data_type_to_dict = [vars(listing) for listing in data]
        print("Saving data to DB....")
        query = insert(self.table)
        self.conn.execute(query, data_type_to_dict)

    def save_single(self, data: PropertyListing) -> None:
        # MAYBE if self.select_single() return non-empty, and off_market is false and ad_removed is null, skip
        # else: insert
        data_type_to_dict = vars(data)
        query = insert(self.table).values(data_type_to_dict)
        self.conn.execute(query)

    def save_to_csv(self, data: List[PropertyListing], file_name: str) -> None:
        data_type_to_dict = [vars(listing) for listing in data]
        df = pd.DataFrame(data_type_to_dict)
        df.to_csv('{0}-results.csv'.format(file_name),
                  encoding='utf-8', index=True)
