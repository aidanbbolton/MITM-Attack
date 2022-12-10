#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"
MY_IP = "GATE"
HOST_IP = "HOST"

arp_table = {}
broadcast = 7777
gateport = 9999


def gate(lock):

	while(1):
		lock.acquire()
		if(HOST_IP not in arp_table):
			lock.release()
	
			print("request Host arp")
			request = "" + str(broadcast) + str(gateport) + "86" + "0001" + "0800" + "0604" + "0001" + str(gateport) + MY_IP + "0000" + HOST_IP + "0"*16
		
			sock =  socket(AF_INET,SOCK_DGRAM)
			sock.sendto(request.encode(), (IP,int(broadcast)))
			sock.close()
			time.sleep(2)
		else:
			lock.release()
			print("HOST port found")
			break
	
	hostsock =  socket(AF_INET,SOCK_DGRAM)
	hostsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	while(1):
		
		lock.acquire()
		hport = arp_table[HOST_IP] -1
		lock.release()
		
		print("HPORT {}",hport)
		hostsock.bind((IP,gateport-1))
		data = hostsock.recvfrom(1024)
		
		response = "<html><h1>Good Response</h1></html>\r\n\r\n"
		
		hostsock.sendto(response.encode(), (IP,hport))
		
		time.sleep(1)
				



def ARP_receive(lock,data):
	
# 	udpsock = socket(AF_INET,SOCK_DGRAM)
# 	udpsock.bind((IP,gateport))
# 	
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
		
		response = "" + e_sport + e_dport + e_type + enet + opp + "0002" + str(gateport) + MY_IP + sport + sip + "000000000000"
		
		sock =  socket(AF_INET,SOCK_DGRAM)
		sock.sendto(response.encode(), (IP,int(sport)))
		sock.close()			
		
	elif(arp_type == "0002"):
		print("response received: Port {}")
		lock.acquire()
		arp_table[sip] = int(sport)
		lock.release()
		
		
	else:
		print("Unknown ARP type")





if __name__ == "__main__":
	lock = _thread.allocate_lock()
	
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,gateport))
	
	_thread.start_new_thread(gate,(lock,))
	while(1):
		print("THread 2 waiting on data")
		data, addr = udpsock.recvfrom(1024)
		_thread.start_new_thread(ARP_receive,(lock,data))
	