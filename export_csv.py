import csv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


token = "IP7opg_k5MF_gSaFVaCudqQIjyjVj5fQorzxqzC-JAfxYnotppgHrF9a-DNM3YpOuBaNV_d7_S2PBR5CXjn0dw=="
url = "http://192.168.0.58:8086"
org = "JYLab3F"
bucket = "TABoardStability"

with InfluxDBClient(url=url, token=token, org=org) as client:
    query_api = client.query_api()

    ## using csv library
    query = f'from(bucket:"{bucket}") |> range(start: -10m)'
    csv_result = query_api.query_csv(query)

    output_filename = "stability_export.csv"

    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in csv_result:
            writer.writerow(row)

    print(f"Data successfully exported to {output_filename}")