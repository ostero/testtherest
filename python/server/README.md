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
- `http://localhost:8080/data.txt` exposes the current data (GET)
- `http://localhost:8080/verify` accepts POST requests with JSON or plain text payloads
### Endpoints

- **GET `/data.txt`**  
  Returns two lines of random data as plain text.

- **POST `/verify`**  
  Accepts JSON or plain text. The payload must be a dictionary with an `answer` key containing a list of two elements.  
  The server checks both lines against the current data and returns a JSON response with a code and message.

### To run expose https
You need certificate file `cert.pem` and the corresponding key file `key.pem`.  
Put them in the `cert` subfolder.
To generate self signed certificate issue:  
```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
