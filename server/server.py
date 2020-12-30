import socket
from os import path
import os


# Parse request header and return list

def parse_header(header):
    sanitized_header = header.replace('\r\n', ' ')
    parsed_header = sanitized_header.split(' ', 3)
    return parsed_header


# Check for valid HTTP request

def valid_request(exists, protocol, method):
    return exists == "True" and protocol == "HTTP/1.1" and method == 'GET'


# Client requests file that does not exist

def file_not_found(exists, protocol, method):
    return exists == "False" and protocol == "HTTP/1.1" and method == 'GET'


# Client HTTP request version is 1.1, but invalid method in request.

def invalid_method(protocol, method):
    return protocol == 'HTTP/1.1' and method != 'GET'


# Client HTTP request version other than 1.1

def version_unsupported(protocol):
    return protocol != 'HTTP/1.1'


# Get current directory

def get_current_directory():
    return os.path.abspath(os.getcwd())


# Get file extension type

def get_file_extension(filename):
    temp = os.path.splitext(filename)[1]
    return temp[1:]


# Extract filename after last '/' from path

def extract_filename(filename):
    return filename.rsplit('/', 1)[-1]


# Extract HTTP response code

def extract_response_code(header_list):
    return header_list[1]


# Returns file size in bytes

def get_file_size(file):
    size = os.stat(file)
    return str(size.st_size)


# Boolean; returns true if file is text file; false otherwise

def is_text(file_type):
    return file_type == 'html' or file_type == 'txt'


# Boolean; returns true if file is image; false otherwise

def is_image(file_type):
    return file_type == 'jpg' or file_type == 'gif' or file_type == 'jpeg'


# Create the socket.  We will ask this to work on any interface and to pick
# a free port at random.  We'll print this out for clients to use.
# Set timeout to our defined constant

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket object
server_socket.bind(('', 0))
print('Will wait for client connections at port ' + str(server_socket.getsockname()[1]))
server_socket.listen(5)  # Listen for client connection

while True:
    connection, address = server_socket.accept()                    # Establish connection with client
    data = connection.recv(4096).decode()                           # Retrieve data from client

    header_list = parse_header(data)                                # Separate headers in data into indexed list
    request_method = header_list[0]
    requested_filename = header_list[1]
    protocol_version = header_list[2]

    sanitized_filename = requested_filename[1:]                     # Strip leading '/' from filename
    file_exists = str(path.exists(sanitized_filename))              # Checks if file exists
    file_type = get_file_extension(sanitized_filename)              # Get extension of filename

    # Check for valid HTTP request

    if valid_request(file_exists, protocol_version, request_method):

        # TEXT

        if is_text(file_type):
            file = open(sanitized_filename, 'rb')
            file_read = file.read()
            content_type = "text/html"
            file_size = get_file_size(sanitized_filename)

            # Keep going until all the data has been read in

            while file_read:
                connection.sendall("HTTP/1.1 200 OK\r\n".encode()
                                   + "Content-Type: ".encode() + content_type.encode() + "\r\n".encode()
                                   + "Content-Length: ".encode() + file_size.encode() + "\r\n\r\n".encode()
                                   + file_read)
                file_read = file.read()
                file.close()
            print(sanitized_filename, ' has been sent to client.')

        # IMAGE

        elif is_image(file_type):
            file = open(sanitized_filename, 'rb')
            file_read = file.read()
            content_type = "image/jpg"
            img_size = get_file_size(sanitized_filename)

            # Keep going until all the data has been read in

            while file_read:
                connection.sendall("HTTP/1.1 200 OK\r\n".encode()
                                   + "Content-Type: ".encode() + content_type.encode() + "\r\n".encode()
                                   + "Content-Length: ".encode() + img_size.encode() + "\r\n\r\n".encode()
                                   + file_read)
                file_read = file.read()
            file.close()
            print(sanitized_filename, ' has been sent to client.')

        else:
            exit()

    # Client requests file that does not exist

    elif file_not_found(file_exists, protocol_version, request_method):
        print("SERVER: 404")
        connection.send("HTTP/1.1 404 Not Found\r\n\r\n".encode()
                        + "<html><body><h1> File Not Found </body></html>".encode())

    # Client HTTP request version is 1.1, but invalid method in request.

    elif invalid_method(protocol_version, request_method):
        print("SERVER 501")
        connection.send("HTTP/1.1 501 Method Not Implemented\r\n\r\n".encode()
                        + "<html><body><h1> Invalid method in request </body></html>".encode())

    # Client HTTP request version other than 1.1

    elif version_unsupported(protocol_version):
        print("SERVER 505")
        connection.send("HTTP/1.1 505 Version Not Supported\r\n\r\n".encode()
                        + "<html><body><h1> Version Not Supported. This server only supports HTTP/1.1 </body></html>".encode())

    else:
        exit()

    connection.close()
