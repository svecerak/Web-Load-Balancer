Config file formatted as 'host:port'. Example config provided.
File used for testing server performance is 'test.jpg', and has been included in server folder. 

server
------

To run the server, simple execute:

  python server.py

potentially substituting your installation of python3 in for python depending
on your distribution and configuration.  The server will report the port 
number that it is listening on for your client to use. For the purposes of this 
exercise, you will need to run multiple instances of server to allow the balancer
to determine the optimal choice. Place any files to transfer into the same directory 
as the server.


load balancer
------

To run the load balancer, simple execute:

  python balancer.py
  
The balancer will report the port number that it is listening on for your client to 
use. Before the load balancer starts accepting traffic from clients, it needs to do 
a performance test on the servers.  For this, it will make a simple transfer request 
from each server and time how long it takes to complete each request. After running the 
performance test, the load balancer can rank the servers it knows about in terms of 
their transfer times. Using an algorithm, it will prioritize redirection of client requests 
to faster servers. The load balancer can now start accepting client requests. When the load 
balancer receives a request from the client, it will select a target server from its server 
list as discussed above.  The load balancer will redirect the client to this server by returning 
a 301 Moved Permanently response to the client with a Location: header line specifying the 
selected target server to retrieve the file from. 


client
------

To run the client, execute:

  python client.py http://host:port/file

where host is where the balancer is running (e.g. localhost), port is the port 
number reported by the balancer where it is running and file is the name of the 
file you want to retrieve. If the client receives a 301 Moved Permanently response to a
request, it prints out the message as usual, but instead of exiting, it immediately initiates 
another request to retrieve the file from the URL given in the Location: header.  It will then
download the file and/or report errors encountered normally from there. Again, you might need
to substitute python3 in for python depending on your installation and configuration.
