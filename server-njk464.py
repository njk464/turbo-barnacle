# njk464
# Nick Kantor
# Project 2
# CS356 Spring 2016
from socket import *
import sys
import signal
# The routing table. I set it up as a list of tuples. The first elment in the tuple represents the base address for the range. 
# The second the mask size.
# The third the The next element the AS. 
# The forth the cost
routing_table = [(0,0,"A",100)]

# routing table update method
def update(creq):
	return

def query(creq):
	return ("0.0.0.0", "A", 100)
# checks to see what kind of request it is
def is_update(creq):
	creq = creq.split("\r\n")
	return "UPDATE" in creq[0]
# send the response
def send(cs, is_ack, address, AS, cost):
	# generate the response
	if (is_ack):
		response="ACK\r\nEND\r\n"
	else:
		response="RESULT\r\n" + address + " " + AS + " " + str(cost) + "\r\nEND\r\n"
	# send the response
	# print (response)
	cs.send(response.encode())

# set the port to the command line argument
serverPort = int(sys.argv[1])
# create a TCP socker
serverSocket = socket(AF_INET,SOCK_STREAM)
# bind the socket
serverSocket.bind(('',serverPort))
# start listening
serverSocket.listen(1)
# true while listening
Listening = True
print ("Listening on port", serverPort)

# signal handler for Ctrl+C
def signal_handler(signal, frame):
    serverSocket.close()
    Listening = False
    print ('Server closed')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
while Listening:
	connectionSocket, addr = serverSocket.accept()
	# receive the request
	clientRequest = connectionSocket.recv(8192)
	# decode it from byte format
	creq = clientRequest.decode()
	# boolean for if the response will be an ack
	is_ack = True
	# address for query response
	address = "0.0.0.0"
	# The Autonomous system that the router will forward to
	AS = "A"
	# the cost
	cost = 10
	if (is_update(creq)):
		update(creq)
	else:
		is_ack = False
		(address, AS, cost) = query(creq)
	# send the response		
	send(connectionSocket, is_ack, address, AS, cost)
	# close the socket
	connectionSocket.close()
serverSocket.close()
print ('Server closed')
