"""
How to use Asyncio with InfluxDB client.
"""
import asyncio
from datetime import datetime

from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


async def main():
    async with InfluxDBClientAsync(url="http://localhost:8086", token="my-token", org="my-org") as client:
        """
        Check the version of the InfluxDB
        """
        version = await client.version()
        print(f"\n------- Version -------\n")
        print(f"InfluxDB: {version}")

        """
        Prepare data
        """
        print(f"\n------- Write data by async API: -------\n")
        write_api = client.write_api()
        _point1 = Point("async_m").tag("location", "Prague").field("temperature", 25.3)
        _point2 = Point("async_m").tag("location", "New York").field("temperature", 24.3)
        successfully = await write_api.write(bucket="my-bucket", record=[_point1, _point2])
        print(f" > successfully: {successfully}")

        """
        Query: List of FluxTables
        """
        query_api = client.query_api()
        print(f"\n------- Query: List of FluxTables -------\n")
        tables = await query_api.query('from(bucket:"my-bucket") '
                                       '|> range(start: -10m) '
                                       '|> filter(fn: (r) => r["_measurement"] == "async_m")')

        for table in tables:
            for record in table.records:
                print(f'Temperature in {record["location"]} is {record["_value"]}')

        """
        Query: Stream of FluxRecords
        """
        print(f"\n------- Query: Stream of FluxRecords -------\n")
        query_api = client.query_api()
        records = await query_api.query_stream('from(bucket:"my-bucket") '
                                               '|> range(start: -10m) '
                                               '|> filter(fn: (r) => r["_measurement"] == "async_m")')
        async for record in records:
            print(record)

        """
        Query: Pandas DataFrame
        """
        print(f"\n------- Query: Pandas DataFrame -------\n")
        query_api = client.query_api()
        dataframe = await query_api.query_data_frame('from(bucket:"my-bucket") '
                                                     '|> range(start: -10m) '
                                                     '|> filter(fn: (r) => r["_measurement"] == "async_m")'
                                                     ' |> group()')
        print(dataframe)

        """
        Query: String output
        """
        print(f"\n------- Query: String output -------\n")
        query_api = client.query_api()
        raw = await query_api.query_raw('from(bucket:"my-bucket") '
                                        '|> range(start: -10m) '
                                        '|> filter(fn: (r) => r["_measurement"] == "async_m")')
        print(raw)

        """
        Delete data
        """
        print(f"\n------- Delete data with location = 'Prague' -------\n")
        successfully = await client.delete_api().delete(start=datetime.fromtimestamp(0), stop=datetime.now(),
                                                        predicate="location = \"Prague\"", bucket="my-bucket")
        print(f" > successfully: {successfully}")


if __name__ == "__main__":
    asyncio.run(main())
