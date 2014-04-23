#!/usr/bin/env python
from time import sleep
import socket
import re
import logging
import json
log = logging.getLogger()

SOCKET_TIMEOUT=0.5
bs=40960
delay=0.1
def recv(sock,delay_rate=1):
    data = ""
    while True:
        try:
            sleep(delay*delay_rate)
            data += sock.recv(bs)
        except socket.timeout:
            break
    return data

#ref https://docs.python.org/2/library/cliet.html#example
def get_cli(host=None,port=None,user=None,password=None,epassword=None,*args,**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,int(port)))
    s.settimeout(SOCKET_TIMEOUT)
    s.sendall("{user}\n{password}\nterminal length 0\n".format(**locals()))
    log.debug(recv(s))
    if epassword:
        s.sendall("enable\n{epassword}\n".format(**locals()))
    log.debug(recv(s,10))
    return s


def dev_cmd(cli=None,cmd=None,delay_rate=1):
    cli.sendall(cmd)
    data=recv(cli)
    log.debug(data)
    return data

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
 
    #json_data=dict((r["device_id"],r) for r in row)
    #log.debug(json.dumps(json_data,indent=4))
    return json_data

def show_cdp_entry(cli=None,device_id=None):
    return dev_cmd(cli,"show cdp entry %s\n"%device_id,delay_rate=5)

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

    #log.debug(raw)
    #log.debug(json.dumps(json_data,indent=4))
    return json_data
