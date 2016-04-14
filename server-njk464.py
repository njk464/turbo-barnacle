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
routing_table = [("0.0.0.0",0,"A",100)]

# server and connection sockets
serverSocket = None
connectionSocket = None

# signal handler for Ctrl+C
def signal_handler(signal, frame):
	if (connectionSocket is not None):
		connectionSocket.close()
	if (serverSocket is not None):
		serverSocket.close()
	Listening = False
	print ('Server closed')
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# method for checking ip address matches
def is_match(rout_address, address, rout_mask):
	rout_address = rout_address.split(".")
	address = address.split(".")
	for i in range(rout_mask//8):
		if rout_address[i] != address[i]:
			return False
	return True

# routing table update method
def update(creq):
	creq = creq.split("\r\n")
	for i in range(1,len(creq)-2):
		update = creq[i].split(" ")
		(address, mask) = update[1].split("/")
		routing_table.append((address, int(mask), update[0], int(update[2])))

# method for handling query requests
def query(creq):
	creq = creq.split("\r\n")
	address = creq[1]
	AS = "A"
	cost = 100
	mask = 0
	for i in routing_table:
		(rout_address, rout_mask, rout_AS, rout_cost) = i
		# checks if the address and rout_address are a match
		if is_match(rout_address, address, rout_mask):
			# verifies that this route has higher precedence then the current route
			if (rout_cost < cost or (rout_cost == cost and rout_mask >= mask)):
				AS = rout_AS
				cost = rout_cost
				mask = rout_mask
	return (address, AS, cost)

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
	# print (response)
	# send the response
	cs.send(response.encode())

def main():
	# set the port to the command line argument
	serverPort = int(sys.argv[1])
	# create a TCP socker
	serverSocket = socket(AF_INET,SOCK_STREAM)
	# makes it so you can reuse the port afterwards
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	# bind the socket
	serverSocket.bind(('',serverPort))
	# start listening
	serverSocket.listen(1)
	print ("Listening on port", serverPort)
	# true while listening
	Listening = True

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

main()
