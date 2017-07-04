from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import plotly
from plotly.graph_objs import Scatter, Layout
from influxdb import InfluxDBClient
from dateutil import parser
from datetime import timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
db = "IoT_Project"
db_ip = os.environ['IOT_DB_IP']

@app.route('/')
def index():
    return render_template('index.html')

def generate_div(x, y, title):
    div = str(plotly.offline.plot({
        "data": [Scatter(x=x, y=y)],
        "layout": Layout(title=title)
    }, output_type='div', include_plotlyjs=False))

    s = div.find('<script')
    script = div[s:]
    div = div[:s]
    script = script.replace('<script type="text/javascript">', '')
    script = script.replace('</script>', '')
    return str(div), str(script)

@socketio.on('update_data')
def gather_data(message):
    client = InfluxDBClient(db_ip, 8086, db)
    client.create_database(db)
    client.switch_database(db)

    result = client.query('select * from Temperature where time > now() - 1h;')
    x = [parser.parse(i['time'])+timedelta(hours=8) for i in list(result)[0]]
    y = [i['value'] for i in list(result)[0]]
    data_tem, script_tem = generate_div(x, y, "Temperature")

    result = client.query('select * from Humidity where time > now() - 1h;')
    y = [i['value'] for i in list(result)[0]]
    data_hum, script_hum = generate_div(x, y, "Humidity")

    result = client.query('select * from Pressure where time > now() - 1h;')
    y = [i['value'] for i in list(result)[0]]
    data_pre, script_pre = generate_div(x, y, "Pressure")



    emit('get_data', { "data_tem": data_tem, "script_tem": script_tem, "data_hum": data_hum, "script_hum": script_hum,"data_pre": data_pre, "script_pre": script_pre } )

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
