#!/usr/bin/env python
from time import sleep
import socket
import re
import logging
import json
log = logging.getLogger()

SOCKET_TIMEOUT=0.1
bs=40960
delay=0.1
def recv(sock,delay_rate=1):
    raw = ""
    while True:
        try:
            sleep(delay*delay_rate)
            raw += sock.recv(bs)
        except socket.timeout:
            break
    return raw

#ref https://docs.python.org/2/library/cliet.html#example
def get_cli(host=None,port=None,user=None,password=None,epassword=None,*args,**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,int(port)))
    s.settimeout(SOCKET_TIMEOUT)
    s.sendall("{user}\n{password}\nterminal length 0\n".format(**locals()))
    raw=recv(s,3)
    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
    if epassword:
        s.sendall("enable\n{epassword}\n".format(**locals()))
    raw=recv(s,3)
    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
    return s

def dev_cmd(cli=None,cmd=None,delay_rate=1):
    cli.sendall(cmd)
    raw=recv(cli,delay_rate)
    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
    return raw

def show_cdp_neighbors(cli=None):
    return dev_cmd(cli,"show cdp neighbors\n",delay_rate=10)

def get_cdp_neighbors(cli=None):
    raw = show_cdp_neighbors(cli)
    regx=r"\n(?P<device_id>\S+)\s*(?P<local_interface>(Fas|Gig)\s[\d/]+)\s+(?P<holdtme>\d+)\s+(?P<capability>(\S\s)*\S)\s+(?P<platform>\S+)\s*(?P<port_id>(Fas|Gig)\s[\d/]+)"
    row=[   
            m.groupdict()
            for m in re.finditer(regx , raw)
        ]
    json_data={}
    for r in row:
        did=r["device_id"]
        cdp_col = ["local_interface","holdtme","port_id"]
        cdp=dict([
                (k,r[k] )
                for k in cdp_col
            ])

        cdps=json_data.get(did,{}).get("cdp",[])
        r["cdp"]=cdps+[cdp]
        for k in cdp_col:
            del r[k]
        json_data[did]= r
 
    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
        log.debug(json.dumps(json_data,indent=4))
    return json_data

def show_cdp_entry(cli=None,device_id=None):
    return dev_cmd(cli,"show cdp entry %s\n"%device_id,delay_rate=1)

def get_cdp_entry(cli=None,device_id=None):
    raw = show_cdp_entry(cli,device_id)
    regx1=r"\n(?P<key1>\w[^\r:]+[^\)]):\s+(?P<value1>[^\r]+)"
    regx2=r"\n(?P<key2>[^\r:]+\(es\)): \r\n(?P<value2>(  IP address: [^\r]+)*\r)"
    regx = r"(%s)|(%s)"%(regx1,regx2)
    row = [   
            m.groupdict()
            for m in re.finditer(regx , raw)
          ]
    json_data={}
    for r in row:
        #log.debug(r)
        k=(r.get("key1") or r.get("key2")).strip(' \r\n').lower().replace(" ","_")
        v=(r.get("value1") or r.get("value2")).strip(' \r\n')
        json_data[k]=v

    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
        log.debug(json.dumps(json_data,indent=4))
    return json_data

def show_arp(cli=None):
    return dev_cmd(cli,"show arp\n")

def get_arp(cli=None):
    raw = show_arp(cli)
    regx = r"\n(?P<protocol>\S+)\s+(?P<address>[\d\.]+)\s+(?P<age>\S+)\s+(?P<mac>[\dabcdef\.]+)\s+(?P<type>\S+)\s+(?P<interface>\S+)"
    row = [   
            m.groupdict()
            for m in re.finditer(regx , raw)
          ]
    json_data=row
    if log.isEnabledFor(logging.DEBUG):
        log.debug(raw)
        log.debug(json.dumps(json_data,indent=4))
    return json_data
