import os
import csv
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

# Load variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

token = os.getenv("INFLUX_TOKEN")
url = os.getenv("INFLUX_URL")
org = os.getenv("INFLUX_ORG")

missing_vars = [var for var in ["INFLUX_TOKEN", "INFLUX_URL", "INFLUX_ORG"] if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(f"Missing InfluxDB configuration. Variables not found: {', '.join(missing_vars)}. "
                       f"Ensure they are set in your .env file at {env_path}.")

BUCKET = "TABoardStability"
OUTPUT_FILENAME = "stability_export.csv"

with InfluxDBClient(url=url, token=token, org=org) as client:
    query_api = client.query_api()

    # Construct the Flux query
    query = f'''
        from(bucket: "{BUCKET}")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "Efficiency")
    '''

    print(f"Querying InfluxDB and exporting to {OUTPUT_FILENAME}...")

    try:
        # Convert the iterator to a list immediately to prevent exhaustion
        csv_data = list(query_api.query_csv(query))

        if csv_data:
            with open(OUTPUT_FILENAME, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)
            print(f"Successfully exported {len(csv_data)} rows to {OUTPUT_FILENAME}")
        else:
            print("Query returned no data. Check your bucket name and time range.")
    except Exception as e:
        print(f"An error occurred during export: {e}")