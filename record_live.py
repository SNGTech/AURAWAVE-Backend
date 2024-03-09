import time
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
from dotenv import load_dotenv
import os

class RecorderLive:
    def __init__(self, duration: int):
        load_dotenv()

        self.duration = duration

        # Influx Configurations
        self.BUCKET = "eeg_data"
        self.ORG = "AurawaveData"
        TOKEN = os.getenv('INFLUXDB_API_TOKEN')
        # Store the URL of your InfluxDB instance
        URL="http://localhost:8080" # CHANGE THIS TO your IPv4 Address of your Computer Server, port should match your InfluxDB port

        self.client = influxdb_client.InfluxDBClient(url=URL, org=self.ORG, token=TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def start_recording_fp1(self):
        # Add delay before starting recording
        time.sleep(1)

        start_time = time.time()

        res = {'eeg_data': {}}

        # for channel in ['Fp1']:
        #     res['eeg_data'][channel] = []

        # while (time.time() - start_time) <= self.duration:
        #     time.sleep(0.25)

        query_api = QueryApi(self.client)

        flux_query = f'from(bucket: "{self.BUCKET}") ' \
                 f'|> range(start: -{self.duration}s) ' \
                 f'|> filter(fn: (r) => r["_measurement"] == "eeg_measurement_rpi")' \
                 f'|> filter(fn: (r) => r["_field"] == "Fp1")' \
                 f'|> filter(fn: (r) => r["type"] == "eeg")'
        
        response = query_api.query(flux_query)
        eeg_data = []
        for table in response:
            for record in table.records:
                eeg_data.append(record["_value"])

        # for table in response:
        #     for record in table.records:
        #         try:
        #             'updatedAt' in record
        #         except KeyError:
        #             record['updatedAt'] = record.get_time()
        #             record[record.get_field()] = record.get_value()
        #         result.append(record.values)

        # print(result)

        # Build remainder of json response object (USING SAMPLE DATA FOR NOW)
        res['eeg_data']['Fp1'] = eeg_data
        res['sample_freq'] = 500.0
        res['profile_info'] = { 'Gender': 'M', 'Age': 77 }

        return res
