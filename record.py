import time
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

class Recorder:
    def __init__(self, duration: int, test_data):
        self.duration = duration

        self.test_data = test_data # DEBUG LINE FOR PRESENTATION

        # Influx Configurations
        self.BUCKET = "eeg_data"
        self.ORG = "AurawaveData"
        TOKEN = "Qgo8yHYFH6RV_Q7iWU3JYxO2CsuTgZRn_IkIje31vrDrGisFS3b2wdrl3sO-Lqmizvs87IPJoHebjaJL8-lb0Q=="
        # Store the URL of your InfluxDB instance
        URL="http://localhost:8086"

        self.client = influxdb_client.InfluxDBClient(url=URL, org=self.ORG, token=TOKEN)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def start_recording(self):
        # Add delay before starting recording
        time.sleep(1)

        eeg_data = self.test_data['eeg_data']
        channels = self.test_data['eeg_data'].keys()
        start_time = time.time()

        res = {'eeg_data': {}}

        for channel in channels:
            res['eeg_data'][channel] = []

        i = 0
        while (time.time() - start_time) <= self.duration:

            point = {}
            # Build point
            for channel in channels:
                point[channel] = float(eeg_data[channel][i])
                res['eeg_data'][channel].append(float(point[channel]))

            eeg_point = [
                {
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "measurement": "eeg_measurement",
                    "tags": {
                        "type": "eeg",
                    },
                    "fields": point
                }
            ]

            self.write_api.write(bucket=self.BUCKET, org=self.ORG, record=eeg_point)

            print(f"Wrote point at time: {((time.time() - start_time) * 1e3):.0f}ms")
            time.sleep(1 / self.test_data['sample_freq'])
            i += 1

        # Build remainder of json response object
        res['sample_freq'] = self.test_data['sample_freq']
        res['profile_info'] = self.test_data['profile_info']

        return res

