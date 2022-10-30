import pandas as pd

from typing import List
from src.property_dataclass import PropertyListing


class PropertyDatabase:
    def __init__(self, isCsv=False):
        self.isCsv = isCsv

    def save(self, data: List[PropertyListing]):
        if self.isCsv is True:
            df = pd.DataFrame([vars(listing) for listing in data])
            df.to_csv('vic-results.csv', encoding='utf-8', index=True)
