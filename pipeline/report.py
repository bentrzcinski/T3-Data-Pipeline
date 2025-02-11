"""
Queries the redshift database for all the data
we want to put in a daily report,
and then generates a JSON file containing it all.
"""

import os
import json
from datetime import date, timedelta
import redshift_connector as red_conn
from load import red_connect

REPORT_FOLER_NAME = 'reports'
DATA_FILE_PREFIX = "report_data"


def get_truck_total(db_conn: red_conn.Connection, truck_id: int, date: date) -> float:
    """
    Gets the combined total value of transactions from the
    truck with the given truck ID on the provided day.
    """
    cursor = db_conn.cursor()

    try:
        query = f"""SELECT SUM(total)
                    FROM ben_trzcinski_schema.fact_transaction
                    WHERE truck_id = {truck_id} AND DATE_TRUNC('day', at) = '{date}'"""
        cursor.execute(query)
        total_value = cursor.fetchone()
        if not total_value[0]:
            return 0
        return round(total_value[0], 2)

    except:
        return -1

    finally:
        cursor.close()


def get_truck_transactions(db_conn: red_conn.Connection, truck_id: int, date: date) -> int:
    """
    Gets the total number of transactions from the
    truck with the given truck ID on the provided day.
    """
    cursor = db_conn.cursor()

    try:
        query = f"""SELECT COUNT(*)
                    FROM ben_trzcinski_schema.fact_transaction
                    WHERE truck_id = {truck_id} AND DATE_TRUNC('day', at) = '{date}'"""
        cursor.execute(query)
        total_count = cursor.fetchone()
        return total_count[0]

    except:
        return -1

    finally:
        cursor.close()


def get_total_number_of_trucks(db_conn: red_conn.Connection) -> int:
    """Gets the total number of trucks in the database."""
    cursor = db_conn.cursor()

    try:
        query = f"""SELECT COUNT(*)
                    FROM ben_trzcinski_schema.dim_truck"""
        cursor.execute(query)
        truck_count = cursor.fetchone()
        return truck_count[0]

    except:
        return -1

    finally:
        cursor.close()


def get_truck_name(db_conn: red_conn.Connection, truck_id: int) -> int:
    """Gets the name of a truck given its ID"""
    cursor = db_conn.cursor()

    try:
        query = f"""SELECT truck_name
                    FROM ben_trzcinski_schema.dim_truck
                    WHERE truck_id = {truck_id}"""
        cursor.execute(query)
        truck_name = cursor.fetchone()
        return truck_name[0]

    except:
        return "N/A"

    finally:
        cursor.close()


def get_average_spend(total_value: float, transaction_count: int) -> float:
    """Calculates the average amount of money spent per transaction."""
    try:
        return round(total_value/transaction_count, 2)

    except:
        return -1


def generate_report_data(date: date) -> dict:
    """Generates the data we need for our report of all trucks on a given date."""
    report_data = {}
    combined_truck_data = []
    total_value = 0
    total_count = 0
    total_average = 0
    conn = red_connect()
    truck_count = get_total_number_of_trucks(conn)
    for truck_id in range(1, truck_count + 1):
        truck_data = {}
        name = get_truck_name(conn, truck_id)
        total = get_truck_total(conn, truck_id, date)
        count = get_truck_transactions(conn, truck_id, date)
        avg = get_average_spend(total, count)
        truck_data["Truck name"] = name
        truck_data["Total transaction value"] = total
        truck_data["Total number of transactions"] = count
        truck_data["Average spend per transaction"] = avg
        total_value += total
        total_count += count
        total_average += avg
        combined_truck_data.append(truck_data)

    report_data["Trucks"] = combined_truck_data
    report_data["Totals"] = {"Name": "Total", "Total combined transaction value": total_value,
                             "Total number of transactions": total_count, "Overall average spend per transaction": round(total_average/truck_count, 2)}

    return report_data


def save_to_json(truck_data: dict, date: date) -> None:
    """Saves a list of our truck data to a local JSON file for viewing."""
    if not os.path.exists(REPORT_FOLER_NAME):
        os.mkdir(REPORT_FOLER_NAME)

    file_name = f"{REPORT_FOLER_NAME}/{DATA_FILE_PREFIX}_{date.today()}.json"
    with open(file_name, "w") as json_file:
        json.dump(truck_data, json_file, indent=4)


def generate_json_report(date: date) -> None:
    """Fully generates the truck data report as a local JSON file."""
    truck_data = generate_report_data(date)
    save_to_json(truck_data, date)


def save_to_html(html_content: str, date: date) -> None:
    """Saves a list of our truck data to a local HTML file for viewing."""
    if not os.path.exists(REPORT_FOLER_NAME):
        os.mkdir(REPORT_FOLER_NAME)

    file_name = f"{REPORT_FOLER_NAME}/{DATA_FILE_PREFIX}_{date.today()}.html"
    with open(file_name, "w") as html_file:
        html_file.write(html_content)


def generate_html_report(date: date) -> None:
    """Fully generates the truck data report as a local HTML file."""
    truck_data = generate_report_data(date)
    date_str = date.strftime("%d/%m/%Y")

    html_content = """
        <html>
        <head>
            <style>
                table { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .total-row { font-weight: bold; background-color: #e0e0e0; } /* Bold styling for the total row */
            </style>
        </head>
        <body>
        """

    html_content += f"""
            <h2>T3 Transactions Report {date_str}</h2>
            <table>
                <tr>
                    <th>Truck Name</th>
                    <th>Total Transaction Value</th>
                    <th>Number of Transactions</th>
                    <th>Average Spend Per Transaction</th>
                </tr>
        """

    for truck in truck_data["Trucks"]:
        html_content += f"""
            <tr>
                <td>{truck["Truck name"]}</td>
                <td>£{truck["Total transaction value"]}</td>
                <td>{truck["Total number of transactions"]}</td>
                <td>£{truck["Average spend per transaction"]}</td>
            </tr>
            """

    totals = truck_data["Totals"]
    html_content += f"""
        <tr class="total-row">
            <td>{totals["Name"]}</td>
            <td>£{totals["Total combined transaction value"]}</td>
            <td>{totals["Total number of transactions"]}</td>
            <td>£{totals["Overall average spend per transaction"]}</td>
        </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    return html_content


def lambda_handler(event, context):
    """The Lambda function for generating our daily report."""
    yesterday_date = date.today() - timedelta(days=1)
    html_report = generate_html_report(yesterday_date)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html_report
    }


if __name__ == "__main__":
    yesterday_date = date.today() - timedelta(days=1)
    save_to_html(generate_html_report(yesterday_date), yesterday_date)
