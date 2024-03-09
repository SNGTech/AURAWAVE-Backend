from extract import EEGExtract
import time
from datetime import datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

BUCKET = "eeg_data"
ORG = "AurawaveData"
TOKEN = "CaJbFl4L-knEgi69Wq0I-WyRj9J6ni3OZyybAuTkPnirsvnQFmKIoDxL7uwq3Yfxz1mUrcXkK5Voo90QaGlQ7w=="
# Store the URL of your InfluxDB instance
URL="http://localhost:8080"

EEG = EEGExtract('test_dataset', '010')

# In seconds
start, stop = 0, 100

data = EEG.extract('Fp1', start, stop)

def influx_main():
    client = influxdb_client.InfluxDBClient(url=URL, org=ORG, token=TOKEN)
    write_eeg_data(client)

def write_eeg_data(client: influxdb_client.InfluxDBClient):
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    for i, t in enumerate(data[1]):
        point = [
            {
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "measurement": "eeg_measurement_rpi",
                "tags": {
                    "type": "eeg",
                },
                "fields": {
                    "Fp1": data[0].T[i][0]
                }
            }
        ]
        write_api.write(bucket=BUCKET, org=ORG, record=point)

        print(f"Read point at time: {t * 1e3}ms with voltage: {data[0].T[i][0] * 1e6}uV")
        time.sleep(EEG.sampling_rate / 1e3)
    client = influxdb_client.InfluxDBClient(url=URL, org=ORG, token=TOKEN)
    write_eeg_data(client)

influx_main()
