from influxdb import InfluxDBClient
from datetime import datetime
import time, sys
import os

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient as bridgeclient
value = bridgeclient()

db = "IoT_Project"
db_ip = os.environ['IOT_DB_IP']
client = InfluxDBClient(db_ip, 8086, db)
client.create_database(db)
client.switch_database(db)

while 1:
    try:
        h = value.get("Humidity")
        t = value.get("Temperature")
        t_2 = value.get("Temperature_2")
        p = value.get("Pressure")

        json_body = [
        {
            "measurement": "Humidity",
            "fields": {
                "value": float(h)
            }
        },
        {
            "measurement": "Temperature",
            "fields": {
                "value": float(t)
            }
        },
        {
            "measurement": "Temperature_2",
            "fields": {
                "value": float(t_2)
            }
        },
        {
            "measurement": "Pressure",
            "fields": {
                "value": float(p)
            }
        }
        ]

        client.write_points(json_body)
        print str(datetime.now()), h, t, t_2, p
        time.sleep(10)
    except:
        print str(datetime.now()), 'Error Occur!'
        client = InfluxDBClient(db_ip, 8086, db)
        client.create_database(db)
        client.switch_database(db)
        time.sleep(10)
