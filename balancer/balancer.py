import socket
import operator
import random
import time

# Define a constant for our buffer size and length for timeout

BUFFER_SIZE = 1024
TIMEOUT = 300


# Parse the config.txt file; returns a list of all potential host:port servers
# Strips out any empty lines, checks for empty config files

def parse_config(filename):
    with open(filename) as file:
        lines = file.readlines()
        junk = []
        list_of_servers = []

        if len(lines) == 0:
            print('Config file empty, shutting down...')
            exit()

        for line in lines:
            if line in ['\n', '\r\n']:
                junk.append(line)
            else:
                stripped_line = line.rstrip()
                list_of_servers.append(stripped_line)

    return list_of_servers


# Using the Triangle Number Series, this algorithm picks a random number (needle)
# and determines which level of the pyramid it belongs to. The lower the level, the faster
# the server its associated with. Since our dictionary of {server:port, server_performance) is sorted
# in descending order(slow->fast), this function returns the corresponding index within the dict

def calculate_index(needle, num_servers, the_sum):
    n = 2
    position = 0

    # If exists only 1 potential server or needle is 1, must be at index 0 in dict

    if num_servers == 1 or needle == 1:
        return position

    else:
        while 1:
            position += 1
            upper_bound = n * (n + 1) // 2

            if needle <= upper_bound:
                return position

            n += 1


# Evaluates the performance of all potential servers listed in the config file;
# Appends the results to a dictionary, where key='host:port', val='server_performance'
# Also keeps track how many potential servers are currently active, appends to list for record keeping

def performance_test(potential_servers, server_destinations):
    server_dictionary = {}
    confirmed_active_servers = []

    i = 0

    while i < potential_servers:
        hp_tuple = server_destinations[i].split(':')  # Is a list with 2 indices ('Host_one' , 'Port_one')
        host = hp_tuple[0]
        port = int(hp_tuple[1])

        # File used for measuring server performance

        test_file = 'test.jpg'

        # Create socket object

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set boolean flag to true; on catch, updated to false

        server_active = True
        try:
            client_socket.connect((host, port))
        except ConnectionRefusedError:
            server_active = False

        # If the current server is confirmed to be active & working, test its performance;
        # Otherwise, skip and move on to next server iteration

        if server_active:
            confirmed_active_servers.append(i)
            request = "GET /" + test_file + " HTTP/1.1\r\nHost: " + host + ":" + str(port) + "\r\n\r\n"

            # Start timer

            start = time.time()

            # Send request, and store response

            client_socket.sendall(request.encode())
            data = client_socket.recv(BUFFER_SIZE)

            # Parsing

            extract_body = data.split("\r\n\r\n".encode(), 1)  # Separate headers from message body
            sanitized_header = data.replace('\r\n'.encode(), ' '.encode())  # Strip '\r\n
            header_list = sanitized_header.split(' '.encode(), 7)  # Update header list
            content_length = int(header_list[6])  # Extract content-length from list of headers

            with open(test_file, 'wb') as f:
                f.write(extract_body[1])
                while BUFFER_SIZE < content_length:
                    remaining_data = client_socket.recv(BUFFER_SIZE)
                    if not remaining_data:
                        break
                    f.write(remaining_data)
            f.close()

            # Calculate duration of file transfer

            end = time.time()
            duration = end - start

            # Add tuple to dictionary, where key='host:port' and val='file transfer duration'
            server_dictionary[server_destinations[i]] = duration

        i += 1

    if len(confirmed_active_servers) == 0:
        print("Shutting down... no active servers...")
        exit()

    return server_dictionary, confirmed_active_servers


# Our main function

def main():

    # Retrieve list of servers, and count of potential servers

    server_destinations = parse_config('config.txt')
    potential_servers = len(server_destinations)

    # Create the socket.  We will ask this to work on any interface and to pick
    # a free port at random.  We'll print this out for clients to use.
    # Set timeout to our defined constant

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket object
    server_socket.settimeout(TIMEOUT)
    server_socket.bind(('', 0))
    print('Will wait for client connections at port ' + str(server_socket.getsockname()[1]))
    server_socket.listen(5)  # Listen for client connection

    while True:
        try:

            # Run performance tester, and store results in dedicated variables

            server_dictionary, confirmed_active_servers = performance_test(potential_servers, server_destinations)
            total_active_servers = len(confirmed_active_servers)
            print("Running performance test...")
            print("Active servers  : ", total_active_servers)
            print("Inactive servers: ", potential_servers - total_active_servers)

            # Sorted from slowest to fastest

            sorted_server_dictionary = sorted(server_dictionary.items(), key=operator.itemgetter(1), reverse=True)
            print('Sorted Dict: ', sorted_server_dictionary)

            # Calculate sum of servers, and randomize a number between 1 and sum inclusive

            series_sum = total_active_servers * (total_active_servers + 1) // 2
            print('Sum   : ', series_sum)
            needle = (random.randint(1, series_sum))
            print('Needle: ', needle)

            # Calculate index of the server the load balancer has chosen

            index = calculate_index(needle, total_active_servers, series_sum)
            print('Index : ', index)

            # Just parsing

            string_version = str(sorted_server_dictionary[index])
            string_version = string_version.strip("()")
            print('Chosen dictionary value: ', string_version)
            print("Waiting for request from client\r\n")
            string_one = string_version.split(',')
            key = string_one[0].strip("''")

            # Establish connection with client

            conn, addr = server_socket.accept()
            data_from_client = conn.recv(4096).decode()
            print("Received request from client...")
            print("Sending forwarding address to client...\r\n")

            filename_requested = 'placeholder.html'
            forwarding_address = "http://" + key + "/" + filename_requested

            conn.sendall("HTTP/1.1 301 Moved Permanently\r\n".encode()
                         + "Location: ".encode() + forwarding_address.encode() + "\r\n\r\n".encode()
                         + "<html><body><h1>301 Moved Permanently</body></html>".encode())

        except socket.timeout:

            # Return back to top of try/except, where it reruns the performance test

            print('Timed out... Running new performance test... \r\n')


if __name__ == '__main__':
    main()
