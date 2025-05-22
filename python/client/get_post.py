#!venv3/bin/python3

import requests as re
import json
from config import Config  # Import the Config class

config = Config.load_from_yaml()

if not config.is_valid():
    print("Invalid configuration. Please check your api_key.yaml file.")
    exit(1)

dataSource = config.src
destination = config.dest

dataRequest = re.get(dataSource)
if dataRequest.status_code == 200:
    print("ok")
    dataLines = dataRequest.text.splitlines()
    response = {
        "task": "POLIGON",
        "apikey": config.apikey,
        "answer": []
    }
    for l in dataLines:
        response["answer"].append(l)
    print(response["task"])
    print(response["answer"])
    responseData = json.dumps(response)
    print(responseData)
    result = re.post(destination, data=responseData)
    print(result.status_code)
    print(result.text)
else:
    print(dataRequest)
