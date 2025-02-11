"""
The file responsible for uploading
processed truck data to our redshift database.
"""

import sys
import os
import csv
from datetime import datetime
import redshift_connector
from dotenv import load_dotenv

TRUCK_DATA_FOLDER_NAME = "data"
COLLATED_FILE_PREFIX = "truck_data"


def red_connect() -> redshift_connector.Connection:
    """Establishes a connection to the Redshift database."""
    print("Establishing connection to the Redshift database...")
    try:
        conn = redshift_connector.connect(
            user=os.getenv("DATABASE_USERNAME"),
            password=os.getenv("DATABASE_PASSWORD"),
            host=os.getenv("DATABASE_IP"),
            port=os.getenv("DATABASE_PORT"),
            database=os.getenv("DATABASE_NAME"))
        print("Connection established successfully.")
        return conn
    except redshift_connector.Error as e:
        print("Error connecting to database: ", e)
        return None


def load_csv(date_time: datetime) -> list[dict]:
    """loads the local truck data csv into a list of dicts."""
    print("Loading truck data from CSV...")
    loaded_data = []
    try:
        file_time = date_time.strftime("%Y-%m-%d_%H:00")
        with open(f"{TRUCK_DATA_FOLDER_NAME}/{COLLATED_FILE_PREFIX}_{file_time}.csv",
                  encoding="utf-8") as f:
            for line in csv.DictReader(f):
                loaded_data.append(dict(line))
        print("Truck data loaded successfully.")
    except FileNotFoundError as e:
        print("File not found: ", e)

    return loaded_data


def upload_truck_data(db_conn: redshift_connector.Connection, transactions: list[dict]) -> None:
    """imports all of the transactions from our trucks into the 'truck' database."""
    cursor = db_conn.cursor()
    print("Importing truck transaction data into the database...")
    try:
        for pos, transaction in enumerate(transactions):
            progress = (pos + 1) / len(transactions) * 100
            sys.stdout.write(f"\rProgress: {progress:.2f}%")

            if transaction.get("type") == "cash":
                transaction_id = 1
            elif transaction.get("type") == "card":
                transaction_id = 2
            else:
                transaction_id = None
            cursor.execute(
                f"""INSERT INTO {os.getenv("DATABASE_SCHEMA")}.fact_transaction
                 (truck_id, payment_method_id, total, at)
                    VALUES ({transaction.get("truck_id")}, {transaction_id},
                     {transaction.get("total")}, '{transaction.get("timestamp")}');""")

            db_conn.commit()
        print("\nTruck transaction data imported successfully.")
    except redshift_connector.Error as e:
        print("\nError importing truck transaction data: ", e)

    finally:
        cursor.close()


def db_close(db_conn: redshift_connector.Connection) -> None:
    """Closes the connection to a Redshift database."""
    print("Closing database connection...")
    try:
        db_conn.close()
        print("Connection closed.")
    except redshift_connector.Error as e:
        print("Error closing database connection: ", e)


def tidy_up(date_time: datetime) -> None:
    """Remove all the truck data files locally"""
    print("Tidying up...")
    try:
        file_time = date_time.strftime("%Y-%m-%d_%H:00")
        os.remove(
            f"{TRUCK_DATA_FOLDER_NAME}/{COLLATED_FILE_PREFIX}_{file_time}.csv")
        if not os.listdir(TRUCK_DATA_FOLDER_NAME):
            os.rmdir(TRUCK_DATA_FOLDER_NAME)
        print("Tidy complete.")
    except (IndexError, FileNotFoundError):
        print("Error deleting truck data files.")


def load(date_time: datetime) -> None:
    """
    Fully loads all data from a file with the
    given datetime to the redshift database.
    """
    load_dotenv()
    conn = red_connect()
    data = load_csv(date_time)
    if conn and data:
        upload_truck_data(conn, data)
        tidy_up(date_time)
    db_close(conn)


if __name__ == "__main__":
    # 12 folder we know exists for testing
    load(datetime(2024, 11, 4, 12, 30))
