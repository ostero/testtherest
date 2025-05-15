#!./venv3/bin/python3

from flask import Flask, Response
import threading
import random
import string

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


if __name__ == '__main__':
    update_data()
    app.run(host='0.0.0.0', port=8080)
