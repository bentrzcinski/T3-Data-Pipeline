"""
Extract all the truck data for the current time from the S3 bucket
and combine it all into one local .csv file.
"""

import os
from datetime import datetime
import boto3
from dotenv import load_dotenv
import pandas as pd

TRUCK_DATA_FOLDER_NAME = "data"
BUCKET_NAME = "sigma-resources-truck"
SUB_FOLDER_NAME = "trucks"
COLLATED_FILE_PREFIX = "truck_data"


def s3_connect() -> boto3.client:
    """Establish a connection to the S3 bucket."""
    try:
        conn = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        print("S3 connection established successfully.")
    except IndexError as e:
        print("Error establishing S3 connection: %s", e)
        return None

    return conn


def download_truck_data_files(date_time: datetime) -> bool:
    """Downloads truck data files from the S3 for a specific date and time."""
    s3 = s3_connect()

    year_month = date_time.strftime("%Y-%m")
    day = date_time.day
    hour = date_time.hour

    objects = s3.list_objects_v2(
        Bucket=BUCKET_NAME, Prefix=f"{SUB_FOLDER_NAME}/{year_month}/{day}/{hour}")

    if not os.path.exists(TRUCK_DATA_FOLDER_NAME):
        os.mkdir(TRUCK_DATA_FOLDER_NAME)

    print("Downloading truck data files from S3 bucket...")

    try:
        for obj in objects["Contents"]:
            file_key = obj["Key"]
            file_name = file_key.split("/")[-1]
            try:
                s3.download_file(BUCKET_NAME, file_key,
                                 f"{TRUCK_DATA_FOLDER_NAME}/{file_name}")
            except (IndexError, FileNotFoundError):
                print("Failed to download file %s", file_name)
                return False

        print("All truck data files downloaded successfully.")
        return True
    except KeyError:
        print("Error locating sub-folder in S3: ", objects["Prefix"])
        return False


def collate_data(date_time: datetime) -> None:
    """
    Collates the data into a single CSV file
    and names it after the time provided.
    """

    file_time = date_time.strftime("%Y-%m-%d_%H:00")

    print("Collating truck data into a single CSV file...")
    try:
        all_truck_data = []
        for file in os.listdir(TRUCK_DATA_FOLDER_NAME):
            if COLLATED_FILE_PREFIX not in file:
                truck_data = pd.read_csv(
                    f"{TRUCK_DATA_FOLDER_NAME}/{file}")
                truck_data['truck_id'] = int(file.split("_")[1][1:])
                all_truck_data.append(truck_data)
        combined_truck_data = pd.concat(all_truck_data, ignore_index=True)
        combined_truck_data.to_csv(
            f"{TRUCK_DATA_FOLDER_NAME}/{COLLATED_FILE_PREFIX}_{file_time}.csv", index=False)
        print("Truck data collated successfully.")
    except (IndexError, FileNotFoundError):
        print("Error collating truck data.")


def tidy_up() -> None:
    """Delete all the individual truck data files"""

    print("Tidying up...")
    try:
        for file in os.listdir(TRUCK_DATA_FOLDER_NAME):
            if COLLATED_FILE_PREFIX not in file:
                os.remove(f"{TRUCK_DATA_FOLDER_NAME}/{file}")
        print("Tidy complete.")
    except (IndexError, FileNotFoundError):
        print("Error deleting individual truck data files.")


def extract(date_time: datetime) -> None:
    """
    The main logic for the extract file,
    combines all the other functions to fully extract
    and compile data from the S3 bucket.
    """
    load_dotenv()
    if download_truck_data_files(date_time):
        collate_data(date_time)
    tidy_up()


if __name__ == "__main__":
    # 12 folder we know exists for testing
    extract(datetime(2024, 11, 4, 12, 30))
