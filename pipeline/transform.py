"""Cleans up the downloaded data ready for loading into the database."""

from datetime import datetime
import pandas as pd

TRUCK_DATA_FOLDER_NAME = "data"
COLLATED_FILE_PREFIX = "truck_data"


def load_data(date_time: datetime) -> pd.DataFrame:
    """
    Loads the collated data from a csv file with the
    given date into a Pandas DataFrame.
    """
    try:
        file_time = date_time.strftime("%Y-%m-%d_%H:00")
        truck_data = pd.read_csv(
            f"{TRUCK_DATA_FOLDER_NAME}/{COLLATED_FILE_PREFIX}_{file_time}.csv")
        return truck_data

    except FileNotFoundError as e:
        print("Unable to locate data file: ", e)
        return None


def save_data(truck_data: pd.DataFrame, date_time: datetime) -> None:
    """Saves the tidied data to a csv file with the given date."""
    try:
        file_time = date_time.strftime("%Y-%m-%d_%H:00")
        truck_data.to_csv(
            f"{TRUCK_DATA_FOLDER_NAME}/{COLLATED_FILE_PREFIX}_{file_time}.csv", index=False)

    except ValueError as e:
        print("Error while saving data file: ", e)


def assign_types(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Ensures the types of all the columns are what we expect."""
    tidy_data = truck_data

    try:
        tidy_data["timestamp"] = pd.to_datetime(tidy_data["timestamp"])
        tidy_data["type"] = tidy_data["type"].astype(str)
        tidy_data["total"] = tidy_data["total"].astype(float)
        return tidy_data

    except KeyError as e:
        print("Error assigning column types: ", e)
        return None


def tidy_total(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Tidies up the 'total' column of the truck data dataframe."""
    tidy_data = truck_data

    try:
        tidy_data = tidy_data[tidy_data["total"] != "blank"]
        tidy_data = tidy_data[tidy_data["total"] != "ERR"]
        tidy_data = tidy_data[tidy_data["total"] != "VOID"]
        tidy_data = tidy_data[tidy_data["total"].astype(float) > 0]
        tidy_data = tidy_data[tidy_data["total"].astype(float) < 100]
        return tidy_data

    except (KeyError, ValueError) as e:
        print("Error while tidying 'total' column: ", e)
        return None


def tidy_type(truck_data: pd.DataFrame) -> pd.DataFrame:
    """Tidies up the 'type' column of the truck data dataframe."""
    tidy_data = truck_data

    try:
        tidy_data = tidy_data[tidy_data["type"].isin(["cash", "card"])]
        return tidy_data

    except KeyError as e:
        print("Error while tidying 'type' column: ", e)
        return None


def transform(date_time: datetime) -> None:
    """
    Fully transform all the truck data for a given date 
    so it is cleaned and ready to upload to the database.
    """
    print("Cleaning the data...")

    truck_data = load_data(date_time)
    if truck_data is None:
        print("Failed to clean the data.")
        return None

    truck_data.dropna(inplace=True)

    truck_data = tidy_total(truck_data)
    if truck_data is None:
        print("Failed to clean the data.")
        return None

    truck_data = tidy_type(truck_data)
    if truck_data is None:
        print("Failed to clean the data.")
        return None

    truck_data = assign_types(truck_data)
    if truck_data is None:
        print("Failed to clean the data.")
        return None

    save_data(truck_data, date_time)

    print("Data cleaned successfully.")
    return None
