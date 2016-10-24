# TLEN 5330 Programming Assignment 2

## Objectives
- To create a HTTP-based web server that handles multiple simultaneous requests from users.

## Background
- In this Assignment we are expected to learn basic of TCP socket Programming.
- We are expected to learn the HTTP protocol including various HTTP errors.
- We are also expected to learn socket threading and handle simultaneous requests using threading.

### Requirments
- Python 2.7
- Document Directory: `www`
- Configuration file: `ws.conf`

## Implementation Details
### Read configuration parameters
- The server first reads configuration parameters from `ws.conf` file.
- The file contains derivateives such as server ip, port number and content-types
- If there is an error in the file then the server will start while returning `HTTP 500 Internal server` for all requests

###  Handling simultaneous requets
- Server handles simultaneous requests using multi-threading.
- The main `server function` create a new thread with `handler` function.
- The handler function then receives data from client, checks the request and then returns httpresponse
- If the handler function receives an `Connection: Keep-Alive` directive, it will set socket timeout and wait for more data.
- If no data was received in the timeout period or the last packet did not have a `Connection: Keep-Alive` derivateiv then the handler function will close the socket and kill the thread.

### Error Handing

#### HTTP 400 Bad Request
- Server will first check for the method directive
  - if the method is not (GET,OPTIONS,HEAD,POST,PUT,DELETE,TRACE) it will return `Invalid method error`
- Server will next check the path of request file
  - if the path does not start with `/`, server will return `Invalid URL error`
- Server will next check for the `HTTP` version
  - if the verion is not `HTTP/1.1` or `HTTP/1.0`, server will return `Invalid HTTP-Verion error`

#### HTTP 404 Not Found
- If the server can not find the requested file in `DocumentRoot` directory, it will return a `404 not found` error

#### HTTP 501 Not Implemented
- If the method in request header is not present in `RequestMethodSupport` paramter of configuration file then server will return `501 not implemented` error

#### HTTP 500 Internal Server Error
- If there is an error in server configuration file, such as no value specified for content-type or no port specified then server will return a `500 internal server error`

### How to run the program
#### Server
```
python2.7 webServer.py
```

### Error Testing
#### 404 Bad Requests
```
(echo -en "GET /index.html HTTP/2.1\r\nHost: localhost\r\n\n"; sleep 10) | telnet 127.0.0.1 8080
(echo -en "GRT /index.html HTTP/1.1\r\nHost: localhost\r\n\n"; sleep 10) | telnet 127.0.0.1 8080
(echo -en "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\n"; sleep 10) | telnet 127.0.0.1 8080
```

#### 501 Not Implemented
```
(echo -en "POST /index.html HTTP/1.1\r\nHost: localhost\r\n\n"; sleep 10) | telnet 127.0.0.1 8080
```
