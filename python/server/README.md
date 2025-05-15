#Example http get endpoint with python flask
## Installation  
### Requirements  
pyton3, pip3
```
source activate
```
### Start the server  
```
./svr.py
```
`http://localhost:8080/data.txt` should be exposed
### To run expose https
You need certificate file `cert.pem` and the corresponding key file `key.pem`.  
Put them in the `cert` subfolder.
To generate self signed certificate issue:  
```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
