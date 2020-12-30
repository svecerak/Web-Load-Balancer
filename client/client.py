import socket
import argparse
from urllib.parse import urlparse
import sys
import os

# Set constant buffer

BUFFER_SIZE = 1024


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


# Boolean; returns true if file is text file; false otherwise

def is_text(file_type):
    return file_type == 'html' or file_type == 'txt'


# Boolean; returns true if file is image; false otherwise

def is_image(file_type):
    return file_type == 'jpg' or file_type == 'gif' or file_type == 'jpeg'


# Method downloads file, and outputs corresponding HTTP response

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to fetch with an HTTP GET request")
    parser.add_argument("-proxy", dest="proxy", help="Check for proxy flag")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    try:
        parsed_url = urlparse(args.url)

        if ((parsed_url.scheme != 'http') or (parsed_url.port == None) or (parsed_url.path == '') or (
                parsed_url.path == '/') or (parsed_url.hostname == None)):
            raise ValueError
        host = parsed_url.hostname
        port = parsed_url.port
        file = parsed_url.path
    except ValueError:
        print('Error:  Invalid URL.  Enter a URL of the form:  http://host:port/file')
        sys.exit(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
    client_socket.connect((host, port))

    # Send HTTP request to the server (maybe there does need to be 2 in above if/else)

    request = "GET /" + file[1:] + " HTTP/1.1\r\nHost: " + host + ":" + str(port) + "\r\n\r\n"
    client_socket.sendall(request.encode())

    # Client receives initial stream of bytes sent from server

    data = client_socket.recv(BUFFER_SIZE)

    print(data.decode())

    extract_body = data.split("\r\n\r\n".encode(), 1)  # Separate headers from message body
    headers = extract_body[0].decode()

    # Parse

    removed_location = headers.split("Location: ")
    left_side_of_headers = str(removed_location[0]).split(' ')
    response_code = left_side_of_headers[1]

    final_destination = removed_location[1]
    final_destination = final_destination.strip('http://')
    final_destination = final_destination.split('/', 1)[0]
    final_destination = final_destination.split(':')

    # host:port of server we'll be contacting

    final_host = final_destination[0]
    final_port = int(final_destination[1])

    if response_code == '301':

        final_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
        final_socket.connect((final_host, final_port))
        final_request = "GET /" + file[1:] + " HTTP/1.1\r\nHost: " + final_host + ":" + str(final_port) + "\r\n\r\n"

        print("Sending new request to confirmed server at port", final_port)
        final_socket.sendall(final_request.encode())
        data_from_server = final_socket.recv(BUFFER_SIZE)  # This receives the actual file from server

        extract_body = data_from_server.split("\r\n\r\n".encode(), 1)  # Separate headers from message body
        sanitized_header = data_from_server.replace('\r\n'.encode(), ' '.encode())  # Strip '\r\n
        header_list = sanitized_header.split(' '.encode(), 3)  # Make list by separating all headers
        response_code = extract_response_code(header_list).decode()  # Retrieve response code from headers list
        header_list = sanitized_header.split(' '.encode(), 7)  # Update header list

        # Check response code, and output corresponding data

        if response_code == "200":
            content_length = int(header_list[6])  # Extract content-length from list of headers

            with open(file[1:], 'wb') as f:
                f.write(extract_body[1])  # Write first stream of bytes (of size 1024) to File
                while BUFFER_SIZE < content_length:
                    remaining_data = final_socket.recv(BUFFER_SIZE)
                    if not remaining_data:
                        break
                    f.write(remaining_data)

            f.close()
            print("File " "'" + file[1:] + "' " + "successfully downloaded to " + get_current_directory())

        elif response_code == "404":
            print(data_from_server.decode())

        elif response_code == "501":
            print(data_from_server.decode())

        elif response_code == "505":
            print(data_from_server.decode())

        elif response_code == "523":
            print(data_from_server.decode())

        else:
            exit()

    else:
        exit()

    # Finally, close socket connection

    client_socket.close()


if __name__ == '__main__':
    main()
