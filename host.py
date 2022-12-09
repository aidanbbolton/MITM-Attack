#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"

ARP_IP = "HOST"
GATE_IP = "GATE"

arp_table = {}
broadcast = 7777
arpport = 9888

def proxy(lock):

	proxy_port = 7889
	tcpsocket=socket(AF_INET,SOCK_STREAM)
	tcpsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	tcpsocket.bind((IP,proxy))
	tcpsocket.listen(5)
	
	(clientsock, addr) = tcpsocket.accept()
	
	lock.aquire()
	if(GATE_IP not in arp_table):
		lock.release()
	
		request = "" + broadcast + str(arpport) + "0806" + "0001" + "0800" + "0604" + "0001" + str(arpport) + ARP_IP + "0000" + GATE_IP + "0"*16
		
		sock =  socket(AF_INET,SOCK_DGRAM)
		sock.sendto(request, (IP,int(broadcast)))
		s.close()
	else:
		lock.release()


	print("waitng on reponse")
	while(1):
		lock.aquire()
		if(GATE_IP not in arp_table):
			lock.release()
			time.sleep(1)
		else:
			lock.release()
			break
	
	while(1):
	
		gatesock = socket(AF_INET,SOCK_STREAM)
		lock.aquire()
		gatesock.connect((IP,arp_table[GATE_IP]))
		lock.release()
	
		data = clientsock.recv(1024)
	
		gatesock.send("HOST".encode())
		data = gatesock.recv(1024)
		clientsock.send(data)
		
		time.sleep(5)
		gatesock.close()


def ARP_receive(lock):
	
	print("Current ARP Thread {}"_thread.get_native_id())
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,arpport))
	
	while(1):
		data, addr = updsock.recvfrom(1024)
		print(data)
		
		e_dport = data[:4]
		e_sport = data[4:8]
		e_type = data[8:10]
		if(e_type != "0806"): 
			continue
		
		opp = data[10:16]
		arp_type = data[16:18]
		sport = data[18:22]
		sip = data[22:26]
		dport = data[26:30]
		dip = data[30:34]
		
		
		if(arp_type == "0001"):
		
			print("request")
		
			if(sip != ARP_IP): 
				continue
			
			response = "" + e_sport + e_dport + e_type + opp + "0002" + arpport + ARP_IP + sport + sip + "000000000000"
			
			print("request response: \n{}",response)
			
			sock =  socket(AF_INET,SOCK_DGRAM)
			sock.sendto(response, (IP,int(sport)))
			s.close()			
			
		elif(arp_type == "0002"):
			print("response received: Port {} is at {}",sport,smac)
			lock.aquire()
			arp_table[sip] = int(sport)
			lock.release()
			
			
		else:
			print("Unknown ARP type")
			continue
	





if __name__ == "__main__":

		
	lock = _thread.allocate_lock()
	a = lock.aquire()
	
	_thread.start_new_thread(ARP_receive,lock)
	_thread.start_new_thread(proxy,lock)
	