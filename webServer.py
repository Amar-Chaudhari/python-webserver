import datetime
import os
import socket
import sys
import threading

# Configuration File Name
_CONFIGURATION_FILE = "ws.conf"

# Global DICT to store server configuration directives
_ENVCONFIG = {}


# client connection handler function
# Accepts accepted socket connection, thrread number and mode
# mode = 500 - configuration file error
def handler(client_connection, threadID, mode):
    # Start time of the thread
    stime = datetime.datetime.now()
    print "Thread-%d - Start Time: %s" % (threadID, str(stime))
    while True:
        try:
            # To show that for pipelining the function will return to recv after sending 1 response
            print "Thread-%d - receiving inside thread" % (threadID)
            request = client_connection.recv(1024)

            # request = None when client closes the socket
            if not request:
                break

            # if mode is 500 then always show internal server error
            if mode == 500:
                http_response = GenerateHttp500Response(version="HTTP/1.1")
                client_connection.sendall(http_response)
                break

            client_req = request.splitlines()

            # Check the request format
            # Check if method is GET,PUT,etc
            # Check if http version is specified
            res, error = CheckRequestFormat(client_req)
            if not res:
                http_response = GenerateHttp400Response(version="HTTP/1.1", error=error)
                client_connection.sendall(http_response)
                break

            # Extra method, path and version from the header
            method, path, version = ExtractClientHeader(client_req)

            # Check if the method is supported by this web server
            # If not return 501 not implemented error
            check_501 = CheckRequestType(method)
            if not check_501:
                http_response = GenerateHttp501Response(version="HTTP/1.1")
                client_connection.sendall(http_response)
                break

            # Check if the header as keep-alive flag
            # if there is keep-alive flag then set timeout
            has_keepalive = CheckForKeepAlive(client_req)
            if has_keepalive:
                client_connection.setblocking(True)

                # Get timeout value from configuration file
                client_connection.settimeout(float(_ENVCONFIG['KeepaliveTime']))
                if method == "GET":
                    http_response = GenerateHttpResponse(path, keepalive=True, version=version,
                                                         has_keepalive=has_keepalive, method=method)
                elif method == "POST":
                    postdata = ExtraPostData(client_req)
                    http_response = GenerateHTTPPostRequest(path, keepalive=True, version=version,
                                                            has_keepalive=has_keepalive, method=method,
                                                            postdata=postdata)
                client_connection.sendall(http_response)
            else:
                if method == "GET":
                    http_response = GenerateHttpResponse(path, keepalive=False, version=version, method=method)
                elif method == "POST":
                    ExtraPostData(client_req)
                client_connection.sendall(http_response)
                break

        except socket.timeout:
            # timeout occurred after the last keep alive message
            # Time to close the socket and kill the thread
            print "Thread-%d - Socket Timeout" % (threadID)
            client_connection.close()
            break
        except ValueError:
            print "exception caught"

    # Thread execution is stopping after this
    etime = datetime.datetime.now()
    print "Thread-%d - End Time: %s" % (threadID, str(etime))
    rtime = etime - stime
    datetime.timedelta(0, 8, 562000)
    print "Thread-%d - Run Time: %s" % (threadID, str(rtime))

    # if connection was not closed anywhere above then it will be closed here
    client_connection.close()

    # return to kill the thread
    # there are other ways to do this
    return False


def ExtraPostData(request):
    try:
        if request:
            return request[-1]
    except ValueError:
        return ""
    return ""

# Function to check request method
# Allowed request are set with the RequestMethodSupport directive in configuration file
def CheckRequestType(method):
    try:
        supportedmethods = _ENVCONFIG['RequestMethodSupport']
        if len(supportedmethods) > 1:
            if method not in supportedmethods.split(','):
                return False
        else:
            if method != supportedmethods:
                return False
    except ValueError:
        pass

    return True


# Check request header format
# Check list -
# 1. Method
# 2. URI format
# 3. HTTP version
def CheckRequestFormat(client_req):
    try:
        method, url, ver = client_req[0].split()
        methods = "GET,OPTIONS,HEAD,POST,PUT,DELETE,TRACE"

        # Check if method is a valid http method
        if method not in methods.split(','):
            return False, "method"

        # Check if the URI startes with /
        # There could be some more checks for example:
        # IE does not allow ":" in URI
        if url[0] != "/":
            return False, "urlerror"

        # This server supports only HTTP/1.1 and HTTP/1.0
        # Anything other than those will be considered as in valid request
        if repr(ver).strip() == repr('HTTP/1.1') or repr(ver).strip() == repr('HTTP/1.0'):
            pass
        else:
            return False, "httpvererror"
    except ValueError:
        pass

    # if not error is found return true and no error
    return True, "no error"


# Function to extract method,path,http version
def ExtractClientHeader(request):
    try:
        if request:
            # assuming required fields will be always 0th element
            # generally this is true, but could fail if not followed
            # Couldnt find any standard format.
            (method, path, version) = request[0].split()
            return (method, path, version)
    except ValueError:
        raise ValueError


# Function to parse the request and find keepalive flag
def CheckForKeepAlive(request):
    try:
        if request:

            # Need to parse the whole request as the keep alive flag is not always on 6th position
            # Different browsers send it in different format
            for r in request:
                if 'Connection:' in r:
                    conn_option = r.split(':')[1]

                    # this is again messed up !
                    # IE uses the flag as Keep-Alive and chrome as keep-alive
                    # My logic is to convert it to lower and then compare
                    if conn_option.strip().lower() == 'keep-alive' or conn_option.strip().lower() == 'keepalive':
                        return conn_option.strip()
    except ValueError:
        pass

    return None


# Function to read the configuration file and create a global DICT
# This function will also check for any mis-configuration in the file
# and set the mode flag as 500 due to which the server will always show
# 500 Internal server error
def ReadConfig():
    if _CONFIGURATION_FILE and os.path.isfile(_CONFIGURATION_FILE):

        # Clear any data that might be in the dict
        _ENVCONFIG.clear()

        # Open the configuration file
        fh = open(_CONFIGURATION_FILE)
        content = fh.read().splitlines()

        for line in content:

            # ignore comments
            if line[0] is not "#":
                try:
                    if line.split()[0] == "DocumentRoot":
                        (var_name, value) = line.split()
                        if not value:
                            raise ValueError
                        _ENVCONFIG[var_name] = value.strip('"')
                    elif line.split()[0] == "DirectoryIndex":
                        splitted = line.split()
                        if len(splitted) < 2:
                            raise ValueError
                        var_name = splitted[0]
                        valpack = []
                        for i in xrange(1, len(splitted)):
                            valpack.append(splitted[i])
                        _ENVCONFIG[var_name] = valpack
                    elif line.split()[0] == "ContentType":
                        (var_name, value1, value2) = line.split()
                        _ENVCONFIG[var_name + " " + value1] = value2
                    elif line.split()[0] == "ListenPort":
                        (var_name, value) = line.split()
                        if not value:
                            raise ValueError
                        if int(value) < 1024:
                            print "Error: WebServer Can not start on ports < 1024\nError: Update ListenPort in configuration file"
                            sys.exit(0)
                        _ENVCONFIG[var_name] = value.strip('"')
                    else:
                        (var_name, value) = line.split()
                        if not value:
                            raise ValueError
                        _ENVCONFIG[var_name] = value.strip('"')

                # Catch any split error
                # This is used to check mis-configuration in the configuration file
                except ValueError:
                    return False
    else:
        print "Error: Set configuration file not present\nError: Exiting the server ..."
        sys.exit(0)

    return True


# Main server function
# Function will create new threads for requests
def ServerMain(mode):
    try:
        ServerIP = _ENVCONFIG['ServerIP']
        ServerPort = int(_ENVCONFIG["ListenPort"])
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind((ServerIP, ServerPort))

        # Accept 50 backlog connections in the queue
        # Not required as we are using threading
        listen_sock.listen(50)
        print 'Serving HTTP on port %s ...' % ServerPort
        id = 1
        while True:
            # Accept new request from clients
            client_connection, client_address = listen_sock.accept()

            # Create a new thread for every request
            # handler - is the function which servers http response
            # id - program generated thread id
            # mode = 500 when there is configuration file error
            t = threading.Thread(target=handler, args=(client_connection, id, mode))

            # start function will start the execution of the handler function
            t.start()
            id += 1
    except ValueError as e:
        print e
        print "Error: Something went wrong!"
        sys.exit(0)
    except KeyError as e:
        print "Error: Missing Configuration " + str(e)
        sys.exit(0)
    except KeyboardInterrupt:
        print "Info: Closing Socket and Exiting Server Gracefully..."
        listen_sock.close()
        sys.exit(0)


# Generic function to create a http response
# Function can be used for http/1.0 and http/1.0
# It will properly set the keep alive flag or connection close flag as required
def GenerateHttpResponse(path, keepalive, version, method, has_keepalive=""):
    # Check if no path has been specified
    # Server will search for the default files
    if path == "/":
        indexs = _ENVCONFIG["DirectoryIndex"]
        for file in indexs:
            fullpath = _ENVCONFIG["DocumentRoot"] + "/" + file
            if os.path.isfile(fullpath):
                break
    else:
        fullpath = _ENVCONFIG["DocumentRoot"] + path

    if method == "GET":
        if os.path.isfile(fullpath):
            fh = open(fullpath, "rb")
            data = fh.read()
            fh.close()
            size = len(data.strip())

            # If keep alive was received from the client then we need to return response with keepalive
            if keepalive:
                http_response_header = "%s 200 OK\nContent-Type: %s\nContent-Length: %d\nConnection: %s\n\r\n" % (
                    version,
                    GetContentType(fullpath), size, has_keepalive)
            else:
                http_response_header = "%s 200 OK\nContent-Type: %s\nContent-Length: %d\nConnection: close\n\r\n" % (
                    version,
                    GetContentType(fullpath), size)

        # if file was not found in document root then return a 404 not found response
        else:
            http_response_header = "%s 404\nContent-Type: %s\nConnection: close\n\r\n" % (
            version, GetContentType(fullpath))
            data = GetNotFoundPage()

    return (http_response_header + data)


# Function to return HTTP reponse for POST request
# It will return post data to path received in the POST request
# This function will also take care of the keep alive flag
def GenerateHTTPPostRequest(path, keepalive, version, method, postdata, has_keepalive=""):
    data = ""
    if method == "POST":
        fullpath = _ENVCONFIG["DocumentRoot"] + path
        if os.path.isfile(fullpath):

            # Return a HTML page with post data in it
            # This is hard coded for now but could be automated depending on the use
            data = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Testing Post</title>
    </head>
    <body>
        <h2>Enter Data to test POST Request</h2>
        <form method="post" action="/testpost.html">
            <input type="text" name="planetName" required placeholder="Enter Planet Name">
            <input type="submit" name="submit" value="submit">
        </form>
    <h1> Post Data </h1>
    <pre>

    """ + postdata + """
    </pre>
    </body>
    </html>
    """
            size = len(data)
            # If keep alive was received from the client then we need to return response with keepalive
            if keepalive:
                http_response_header = "%s 200 OK\nContent-Type: %s\nContent-Length: %d\nConnection: %s\n\r\n" % (
                    version,
                    GetContentType(fullpath), size, has_keepalive)
            else:
                http_response_header = "%s 200 OK\nContent-Type: %s\nContent-Length: %d\nConnection: close\n\r\n" % (
                    version,
                    GetContentType(fullpath), size)
                # if file was not found in document root then return a 404 not found response
        else:
            http_response_header = "%s 404\nContent-Type: %s\nConnection: close\n\r\n" % (
                version, GetContentType(fullpath))
            data = GetNotFoundPage()

    return (http_response_header + data)


# Function to return html page for 501 error
def Get501FoundPage():
    return "<html><body>501 Not Implemented <<error type>>: <<requested data>></body></html>"


# Function to return html page for 400 error
# Function will return appropriate html for type of error
def GenerateHttp400Response(version, error):
    http_response_header = "%s 400\nConnection: close\n\r\n" % (version)
    data = ""
    if error == "method":
        data = """
<html><body>400 Bad Request Reason: Invalid Method :<<request method>></body></html>
"""
    elif error == "urlerror":
        data = """
<html><body>400 Bad Request Reason: Invalid URL: <<requested url>></body></html>
"""
    elif error == "httpvererror":
        data = """
<html><body>400 Bad Request Reason: Invalid HTTP-Version: <<req version>></body></html>
"""
    return (http_response_header + data)


# Function to return html page for 501 error
def GenerateHttp501Response(version):
    http_response_header = "%s 501 Not Implemented\nConnection: close\n\r\n" % (version)
    data = Get501FoundPage()
    return (http_response_header + data)


# Function to return html page for 500 error
def GenerateHttp500Response(version):
    http_response_header = "%s 500 Internal Server Error\nConnection: close\n\r\n" % (version)
    data = Get500FoundPage()
    return (http_response_header + data)


# Function to return content type from the global configuration dict
# If content-type was not found the return False
def GetContentType(path):
    try:
        content_type = path.split('.')
        key = "." + content_type[-1]
        http_response_header_contenttype = _ENVCONFIG['ContentType ' + key]
    except KeyError:
        http_response_header_contenttype = False

    return http_response_header_contenttype


# Function to return html page for 400 error
def GetNotFoundPage():
    return "<html><body> <b>Ops, File Not Found</b> </body> </html>"


# Function to return html page for 500 error
def Get500FoundPage():
    return "<html><body> <h1> Internal Server Error</h1> </body> </html>"


# Function to generate num of files
# Could be use to test simultaneous connections
def GenerateFiles(num):
    for i in xrange(1, num):
        fh = open(_ENVCONFIG["DocumentRoot"] + "/" + "index" + str(i) + ".html", "w")
        data = """
<html>
<body>
<h1>Hello World</h1>
</body>
</html>"""
        fh.write(data)


if __name__ == "__main__":
    if not ReadConfig():
        mode = 500
        ServerMain(mode=mode)
    else:
        # GenerateFiles(100)
        ServerMain(mode=1)
