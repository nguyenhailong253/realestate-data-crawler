import pandas as pd
from typing import List
from src.property_dataclass import PropertyListing


def save_to_csv(self, data: List[PropertyListing], file_name: str) -> None:
    data_type_to_dict = [vars(listing) for listing in data]
    df = pd.DataFrame(data_type_to_dict)
    df.to_csv('{0}-results.csv'.format(file_name),
              encoding='utf-8', index=True)
