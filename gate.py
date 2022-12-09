#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"
GATE_IP = "GATE"
HOST_IP = "HOST"

arp_table = {}
broadcast = 7777
gateport = 9999


def gate(lock):

	lock.aquire()
	if(HOST_IP not in arp_table):
		lock.release()
	
		request = "" + broadcast + str(gateport) + "0806" + "0001" + "0800" + "0604" + "0001" + str(gateport) + GATE_IP + "0000" + HOST_IP + "0"*16
		
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
		hostsock =  socket(AF_INET,SOCK_DGRAM)

		lock.aquire()
		port = arp_table[HOST_IP]
		lock.release()
		
		hostsock.bind((IP,port))
		data = hostsock.recv(1024)
		print(data.decode())
		response = "<html><h1>Good Response</h1></html>\r\n\r\n"
		
		sock =  socket(AF_INET,SOCK_DGRAM)
		sock.sendto(response, (IP,port))
		sock.close()	

		time.sleep(5)
		hostsock.close()		



def ARP_receive(lock):
	
	print("Current ARP Thread {}"_thread.get_native_id())
	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,gateport))
	
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
		
			if(sip != GATE_IP): 
				continue
			
			response = "" + e_sport + e_dport + e_type + opp + "0002" + gateport + GATE_IP + sport + sip + "000000000000"
			
			print("request response: \n{}",response)
			
			sock =  socket(AF_INET,SOCK_DGRAM)
			sock.sendto(response, (IP,int(sport)))
			sock.close()			
			
		elif(arp_type == "0002"):
			print("response received: Port {} is at {}",sport,smac)
			lock.aquire()
			arp_table[sip] = int(sport)
			lock.release()
			
			
		else:
			print("Unknown ARP type")
			continue
	




if __name__ == "__main___":
	lock = _thread.allocate_lock()
	a = lock.aquire()
	
	_thread.start_new_thread(ARP_receive,lock)
	_thread.start_new_thread(gate,lock)
	