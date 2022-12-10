#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"

MY_IP = "HOST"
GATE_IP = "GATE"

arp_table = {}
broadcast = 7777
arpport = 9888

def proxy(lock):

	proxy_port = 7889
	websocket=socket(AF_INET,SOCK_STREAM)
	websocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	websocket.bind((IP,proxy_port))
	
	print("waiting on webpage")
	websocket.listen(5)
	
	(clientsock, addr) = websocket.accept()
	
	while(1):
		lock.acquire()
		if(GATE_IP not in arp_table):
			lock.release()
	
			print("Requesting Gate ARP")
			request = "" + str(broadcast) + str(arpport) + "86" + "0001" + "0800" + "0604" + "0001" + str(arpport) + MY_IP + "0000" + GATE_IP + "0"*16
		
			sock =  socket(AF_INET,SOCK_DGRAM)
			sock.sendto(request.encode(), (IP,int(broadcast)))
			sock.close()
			time.sleep(1)
		else:
			lock.release()
			print("GATE port found")
			break
	
	
	gatesock = socket(AF_INET,SOCK_DGRAM)
	gatesock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	while(1):
		
		lock.acquire()
		gport = arp_table[GATE_IP] - 1
		lock.release()
		data = " "
# 		while(data):
# 			data = clientsock.recv(1024)
	
		input("Ready to send")
		print("send to host")
		data = "HOST"
		gatesock.sendto(data.encode(),(IP,gport))
		gatesock.close()
		
		gatesock.bind((IP,arpport-1))
		data, saddr = gatesock.recvfrom(1024)
		
		print("data received\n",data.decode())
		clientsock.send(data)
		
		time.sleep(1)
		


def ARP_receive(lock,data):
	
	# udpsock = socket(AF_INET,SOCK_DGRAM)
# 	udpsock.bind((IP,arpport))
	
# 	while(1):
# 		data, addr = updsock.recvfrom(1024)
	data = data.decode()

	print(data)
	
	e_dport = data[:4]
	e_sport = data[4:8]
	e_type = data[8:10]
	if(e_type != "86"): 
		print("no arp")
		return
	
	enet = data[10:14]
	opp = data[14:22]
	arp_type = data[22:26]
	sport = data[26:30]
	sip = data[30:34]
	dport = data[34:38]
	dip = data[38:42]
	
	
	if(arp_type == "0001"):
	
		print("request")
	
		if(dip != MY_IP): 
			print("not for me")
			return
		
		response = "" + e_sport + e_dport + e_type + enet + opp + "0002" + str(arpport) + MY_IP + sport + sip + "000000000000"
		
		sock =  socket(AF_INET,SOCK_DGRAM)
		sock.sendto(response.encode(), (IP,int(sport)))
		sock.close()			
		
	elif(arp_type == "0002"):
		print("response received")
		lock.acquire()
		arp_table[sip] = int(sport)
		lock.release()
		
		
	else:
		print("Unknown ARP type")
	





if __name__ == "__main__":

		
	lock = _thread.allocate_lock()
	
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,arpport))
	
	_thread.start_new_thread(proxy,(lock,))
	while(1):
		data, addr = udpsock.recvfrom(1024)
		_thread.start_new_thread(ARP_receive,(lock,data))
	
	