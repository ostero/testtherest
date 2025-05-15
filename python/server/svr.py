#!./venv3/bin/python3

from flask import Flask, Response
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
    # Path to your certificate and key


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

    # Run HTTPS server
