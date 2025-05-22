#!./venv3/bin/python3

from flask import Flask, Response, request, jsonify
import json
import threading
import random
import string
import argparse

app = Flask(__name__)

data_store = { "data": ""}

def generate_random_string(length=51):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def update_data():
    global data_store
    data_store["data"] = generate_random_string() + "\n" + generate_random_string()

    timer = threading.Timer(60.0, update_data)
    timer.start()

@app.route('/data.txt', methods=['GET'])
def get_data():
    return Response(data_store["data"], mimetype='text/plain'), 200

def validate_and_compare(data, data_store):
    # Validation checks
    if not isinstance(data, dict):
        return {
            "code": -1,
            "message": "Bad format: data is not a dictionary"
        }, 400

    if 'answer' not in data:
        return {
            "code": -1,
            "message": "Bad format: missing 'answer' key"
        }, 400

    if not isinstance(data['answer'], list):
        return {
            "code": -1,
            "message": "Bad format: 'answer' is not a list"
        }, 400

    if len(data['answer']) != 2:
        return {
            "code": -1,
            "message": "Bad format: 'answer' does not have two elements"
        }, 400

    # Comparison with data_store
    lines = data_store["data"].splitlines() if data_store["data"] else ["", ""]
    first_line = lines[0] if len(lines) > 0 else ""
    second_line = lines[1] if len(lines) > 1 else ""

    if data['answer'][0] != first_line:
        return {
            "code": -2,
            "message": "First line of data does not mutch",
        }, 400

    if data['answer'][1] != second_line:
        return {
            "code": -3,
            "message": "Second line of data does not mutch",
        }, 400

    return {
        "code": 0,
        "message": "OK"
    }, 200

@app.route('/verify', methods=['POST'])
def verify():
    if request.is_json:
        data = request.get_json()
    else:
        try:
            raw = request.get_data(as_text=True)
            data = json.loads(raw)
        except Exception:
            data = None

    response, status = validate_and_compare(data, data_store)
    return jsonify(response), status

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--https', default=False, action='store_true')
    params = args.parse_args()

    update_data()
    if params.https:
        cert_file = 'cert/cert.pem'
        key_file = 'cert/key.pem'
        app.run(
            host='0.0.0.0',
            port=8443,
            ssl_context=(cert_file, key_file)  # HTTPS here
        )
    else:
       app.run(host='0.0.0.0', port=8080)
