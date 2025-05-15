#!/bin/python3

import requests as re
import json

def getApiKey():
    infile = open('api.key', 'r')
    firstLine = infile.readline()
    return firstLine.rstrip() 


dataSource="http://localhost:8080/data.txt"
destination="https://poligon.aidevs.pl/verify"

dataRequest=re.get(dataSource)
if dataRequest.status_code== 200:
    print("ok")
    dataLines=dataRequest.text.splitlines()
    response={"task": "POLIGON",
                 "apikey": getApiKey(),
                 "answer": []
             }
    for l in dataLines:
        response["answer"].append(l)
    print(response["task"])
    print(response["answer"])
    responseData=json.dumps(response)
    print(responseData)
    result = re.post("https://poligon.aidevs.pl/verify", data=responseData)
    print(result.status_code)
    print(result.text)
else:
    print(dataRequest)
