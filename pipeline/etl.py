"""
The main Extract-Transform-Load pipeline
script that fully processes the truck data.
"""
from datetime import datetime

from extract import extract
from transform import transform
from load import load


def etl(date_time: datetime) -> None:
    """
    Extracts the data from the S3 bucket,
    Transforms it into an acceptable format,
    Loads it into our Redshift database.
    """

    extract(date_time)
    transform(date_time)
    load(date_time)


if __name__ == "__main__":
    etl(datetime.now())
