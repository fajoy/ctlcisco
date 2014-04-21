#!/usr/bin/env python
from time import sleep
import socket
import re
import logging
log = logging.getLogger()

bs=40960
delay=1

#ref https://docs.python.org/2/library/socket.html#example
def get_sock(host=None,port=None,user=None,password=None,epassword=None,*args,**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,int(port)))
    s.sendall("{user}\n{password}\n".format(**locals()))
    if epassword:
        s.sendall("enable\n{epassword}\n".format(**locals()))
    sleep(delay)
    log.debug(s.recv(bs))
    return s

def dev_cmd(sock=None,cmd=None):
    sock.sendall(cmd)
    sleep(delay)
    data = sock.recv(bs)
    log.debug(data)
    return data

def show_cdp_entry(sock=None,device_id=None):
    return dev_cmd(sock,"show cdp entry %s\n  "%device_id)

def show_cdp_neighbors(sock=None):
    return dev_cmd(sock,"show cdp neighbors\n  ")

def get_cdp_neighbors(sock=None):
    data = show_cdp_neighbors(sock)
        
