#! /usr/bin/env python3

from socket import * 
import _thread
import pathlib
import sys
import time

IP = "127.0.0.1"

def ARP_interpret(lock):
	




if __name__ == "__main___":
	lock = _thread.allocate_lock()
	a = lock.aquire()
	
	_thread.start_new_thread(ARP_intercept,lock)
	_thread.start_new_thread(gate,lock)