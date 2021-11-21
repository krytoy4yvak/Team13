import json
from threading import Thread

from flask import Flask, request

from anomaly import anomaly_find
from forecast import predict

app = Flask(__name__)


@app.route('/forecast/<period>', methods=['POST'])
def predict_sensor_data(period):
    body = request.get_json()
    period_int = int(period)
    building_id = int(body['building_id'])
    block_id = int(body['block_id'])
    sensor_id = int(body['sensor_id'])

    thread = Thread(target=predict, args=(building_id, block_id, sensor_id, period_int))
    thread.daemon = True
    thread.start()

    return json.dumps({'status': 'OK'})


@app.route('/anomaly', methods=['POST'])
def find_anomaly_data():
    body = request.get_json()
    building_id = int(body['building_id'])
    block_id = int(body['block_id'])
    sensor_id = int(body['sensor_id'])

    thread = Thread(target=anomaly_find, args=(building_id, block_id, sensor_id))
    thread.daemon = True
    thread.start()

    return json.dumps({'status': 'OK'})


@app.route('/health/liveness')
def health():
    return json.dumps({'status': 'OK'})


@app.route('/health/readiness')
def ready():
    return json.dumps({'status': 'OK'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
