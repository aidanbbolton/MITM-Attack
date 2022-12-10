#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"
MY_IP = "BCST"
GATE_IP = "GATE"
HOST_IP = "HOST"
ATCK_IP = "ATCK"

gatePort = 9999
hostPort = 9888
atckPort = 9666
broadcast = 7777



def bcast(data):
	
	print("Broadcast: {}",data.decode())
	
	sock = socket(AF_INET,SOCK_DGRAM)
	sock.sendto(data,(IP,gatePort))
	sock.sendto(data,(IP,hostPort))
	sock.sendto(data,(IP,atckPort))
	sock.close()



if __name__ == "__main__":

	udpsock = socket(AF_INET,SOCK_DGRAM)
	udpsock.bind((IP,broadcast))
	
	while(1):
		print("waiting on data")
		data, addr = udpsock.recvfrom(1024)
	
		_thread.start_new_thread(bcast, (data,))