#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time


IP = "127.0.0.1"

# Fake IP address for this python script to interpret
ATCK_IP = "ATCK"
GATE_IP = "GATE"
HOST_IP = "HOST"

# Port to use for sending data to intercepted host
arphport = 9611
# Port to use for sending data to intercepted gateway
arpgport = 9622

# port to receive data on (broadcast)
atckport = 9666

# Dictionary to serve as ARP table
arp_table = {}

'''
mitm executes the MITM attack on HOST and GATE. It intercepts packets intended for the 
other hosts by poisoning ARP tables when receiving requests not meant for it. It opens 
sockets for each connection and acts as a middle man, passing information between. This 
could be used for any sort of further deception to get user information, but for the 
purpose of this demonstration I just send a message confirming the attack
	- lock : thread lock to access shared resources
'''
def mitm(lock):
	
	# sockets for host and gateway
	hostsock = socket(AF_INET,SOCK_DGRAM)
	gatesock = socket(AF_INET,SOCK_DGRAM)
	
	print("waiting on arp_table")
	while(1):
	
		
		lock.acquire()
		
		# check if ARP_intercept has successfully acquired addresses for Host and Gate
		if(HOST_IP in arp_table and GATE_IP in arp_table):
			lock.release()
			
			# build sockets for data transmission 
			hostsock = socket(AF_INET,SOCK_DGRAM)
			gatesock = socket(AF_INET,SOCK_DGRAM)
			gatesock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
			hostsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	
			# Due to limitations of this program, derive from port from table
			fromHost = arpgport -1
			fromGate = arphport -1
		
			lock.acquire()
			toHost = arp_table[HOST_IP]-1
			toGate = arp_table[GATE_IP]-1
			lock.release()
		
			hostsock.bind((IP,fromHost))
			gatesock.bind((IP,fromGate))
		
			print("thread 2 wating on packet")
			
			# Receive data from host
			data, addr = hostsock.recvfrom(1024)
			print("data from host: ",data.decode())
			
			# Modify the data
			data = "Attacked"
			
			# send to the gate
			gatesock.sendto(data.encode(),(IP,toGate))
			
			data, addr = gatesock.recvfrom(1024)
			print("data from gate: ",data.decode())
			
			# modify the data again from the Gate
			data = "<html><h1>Bad Response</h1></html>\r\n"
			response = "HTTP/1.1 500 Document Follows\r\nContent-Type:text/html\r\nContent-Length:" + str(len(data)-1) + "\r\n\r\n" + data
			hostsock.sendto(response.encode(),(IP,toHost))
			
			hostsock.close()
			gatesock.close()
		
		# wait intill attacker has enough information to execute the attack
		else:
			lock.release()
			time.sleep(1)
		

'''
ARP_intercept takes in a received network packet and processes it. It ignores everything 
except ARP packets, and floods the sender with fake responses in order to poison the 
sender's ARP table
	- lock : thread lock to access shared resources
	- data : received packet from socket
'''
def ARP_intercept(lock,data):

	print("Current ARP Thread {}",_thread.get_native_id())

	data = data.decode()
	print(data)
	
	# Packets are expected to be properly formated ARP requests
	
	# Ethernet header
	e_dport = data[:4]      # destination port
	e_sport = data[4:8]     # source port
	e_type = data[8:10]     # ethernet packet type
	
	# Ignore non-ARP packets
	if(e_type != "86"): 
		print("no arp")
		return
	
	# Packet
	enet = data[10:14]      # Hardware address type
	opp = data[14:22]		# Protocol type, HW address len. Proto. len
	arp_type = data[22:26]  # ARP packet type, request or response
	sport = data[26:30]		# source port
	sip = data[30:34]		# source IP address
	dport = data[34:38]		# destination port
	dip = data[38:42]		# destination IP address
	
	# If packet is request
	if(arp_type == "0001"):
	
		print("request")
		
		# determine who sent the packet and feed the right port
		# for this example I am only expecting data from 2 sources
		sendport = atckport
		if(dip == GATE_IP): 
			sendport = arpgport
		elif(dip == HOST_IP):
			sendport = arphport
		
		# Use the lock to add the IP and port received to the ARP table
		lock.acquire()
		arp_table[sip] = int(sport)
		lock.release()
		
		# Send 10 responses to the sender to overwhelm their ARP table
		for i in range(10):
		
			# properly format the ARP response
			response = "" + e_sport + e_dport + e_type + enet + opp + "0002" + \
				str(sendport) + dip + sport + sip + "000000000000"
		
			print("request response: \n{}",response)
		
			# send the response to the sender
			sock =  socket(AF_INET,SOCK_DGRAM)
			sock.sendto(response.encode(), (IP,int(sport)))
			sock.close()			
	
	# If the attacker receives an ARP response, update the table. This shouldn't happen a
	# because it never sends resquests
	elif(arp_type == "0002"):
		print("response received")
		lock.acquire()
		arp_table[sip] = int(sport)
		lock.release()
		
		
	else:
		print("Unknown ARP type")
		


if __name__ == "__main__":

	# Create a lock to restrict arp_table access
	lock = _thread.allocate_lock()
	
	# create a UDP port to receive packets
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,atckport))
	
	# spin up a thread to execute the MITM attack
	_thread.start_new_thread(mitm,(lock,))
	
	# Loop while waiting on inbound packages
	while(1):
		print("Thread 2 waiting on data")
		data, addr = udpsock.recvfrom(1024)
		
		# Spin up a thread to process received packets
		_thread.start_new_thread(ARP_intercept,(lock,data))
	