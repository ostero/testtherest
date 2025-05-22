#Example  http get endpoint with cpp-http-lib  
## Installation  
### Requirements  
  - install cmake  
  - copy `httplib.h`  
```
curl -fsSL https://raw.githubusercontent.com/yhirose/cpp-httplib/refs/heads/master/httplib.h -o include/third-party/httplib.h
```
### Build  
```
cmake -B build
cmake --build build
```
When the cmake is not availabel resort to traditional make  
```
make
```
### Start the server  
```
./build/RESTServer
```
`http://localhost:8080/data.txt` should be exposed
