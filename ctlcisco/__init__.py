#!/usr/bin/env python
from time import sleep
import socket
import re
import logging
import json
log = logging.getLogger()

bs=40960
delay=1

#ref https://docs.python.org/2/library/cliet.html#example
def get_cli(host=None,port=None,user=None,password=None,epassword=None,*args,**kwargs):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,int(port)))
    s.sendall("{user}\n{password}\nterminal length 0\n".format(**locals()))
    if epassword:
        s.sendall("enable\n{epassword}\n".format(**locals()))
    sleep(delay)
    log.debug(s.recv(bs))
    return s

def dev_cmd(cli=None,cmd=None):
    cli.sendall(cmd)
    sleep(delay)
    data = cli.recv(bs)
    log.debug(data)
    return data


def show_cdp_neighbors(cli=None):
    return dev_cmd(cli,"show cdp neighbors\n")

def get_cdp_neighbors(cli=None):
    raw = show_cdp_neighbors(cli)
    regx=r"\n(?P<device_id>\S+)\s+(?P<local_interface>\S+\s[\d/]+)\s+(?P<holdtme>\d+)\s+(?P<capability>[RTBSHIrPDCM]*[RTBSHIrPDCM ]*[RTBSHIrPDCM])\s+(?P<platform>[\w-]+)\s+(?P<port_id>\S+\s[\d/]+)"
    row=[   
            m.groupdict()
            for m in re.finditer(regx , raw)
        ]
    json_data=dict((r["device_id"],r) for r in row)
    #log.debug(json.dumps(json_data,indent=4))
    return json_data

def show_cdp_entry(cli=None,device_id=None):
    return dev_cmd(cli,"show cdp entry %s\n"%device_id)

def get_cdp_entry(cli=None,device_id=None):
    raw = show_cdp_entry(cli,device_id)
    regx=r"\n(?P<key>\S*\s*\S+):\s+(?P<value>[^\r]+)"
    json_data=dict([   
              (m.groupdict()["key"].lower().replace(" ","_")
              ,m.groupdict()["value"])
            for m in re.finditer(regx , raw)
        ])
    #log.debug(json.dumps(json_data,indent=4))
    return json_data
