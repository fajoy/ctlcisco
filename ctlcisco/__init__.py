#!/usr/bin/env python
from time import sleep
import socket
import re
import logging
import json
log = logging.getLogger()

bs=40960
delay=0.3

#ref https://docs.python.org/2/library/cliet.html#example
def get_cli(host=None,port=None,user=None,password=None,epassword=None,*args,**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((host,int(port)))
    s.sendall("{user}\n{password}\nterminal length 0\n".format(**locals()))
    if epassword:
        s.sendall("enable\n{epassword}\n".format(**locals()))
    sleep(delay*20)
    log.debug(s.recv(bs))
    return s

def dev_cmd(cli=None,cmd=None,delay_rate=1):
    cli.sendall(cmd)
    sleep(delay)
    data = cli.recv(bs)
    log.debug(data)
    return data

def show_cdp_neighbors(cli=None):
    return dev_cmd(cli,"show cdp neighbors\n",delay_rate=10)

def get_cdp_neighbors(cli=None):
    raw = show_cdp_neighbors(cli)
    regx=r"\n(?P<device_id>\S+)\s+(?P<local_interface>\S+\s[\d/]+)\s+(?P<holdtme>\d+)\s+(?P<capability>(\S\s)*\S)\s+(?P<platform>\S+)\s*(?P<port_id>(Fas|Gig)\s[\d/]+)"
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
    return dev_cmd(cli,"show cdp entry %s\n"%device_id,delay_rate=2)

def get_cdp_entry(cli=None,device_id=None):
    raw = show_cdp_entry(cli,device_id)
    #regx=r"\n\s*(?P<key>\w[^:]+):\s+(?P<value>[^\r]+)"
    regx=r"\n(?P<key>\w[^\r:]+):\s+(?P<value>[^\r]+)\r"
    row = [   
            m.groupdict()
            for m in re.finditer(regx , raw)
          ]
    json_data={}
    for r in row:
        k=r["key"].strip(' ').lower().replace(" ","_")
        v=r["value"].strip(' \n')
        json_data[k]=v

    #log.debug(raw)
    #log.debug(json.dumps(json_data,indent=4))
    return json_data
