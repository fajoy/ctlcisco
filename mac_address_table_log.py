#!/usr/bin/env python
from ctlcisco import get_mac_address_table,get_cli
import os,sys
import json
import ConfigParser
import argparse
import logging
import socket
from datetime import datetime
log = logging.getLogger()
CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))

def enable_verbose():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.setLevel(logging.INFO)

def enable_debug():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

def read_topology(path):
    fp=open(path,'r')
    data=json.load(fp)
    fp.close()
    return data

def get_recursively(search_dict, field):
    fields_found = []
    for key, value in search_dict.iteritems():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found

def get_entry_address(topo):
    entrys=get_recursively(topo,"entry")
    addr={}
    for entry in entrys:
        txts = entry.get("entry_address(es)","").split(" ",2)
        if len(txts)>2:
            addr[txts[2]]=entry.get("device_id",txts[2])
            
    #log.debug(json.dumps(entrys,indent=4))
    return addr

def save_mac(arp,fdir,fname):
    if not os.path.exists(fdir):
        os.makedirs(fdir)
    filename=os.path.join(fdir,fname)
    fp=open(filename,'w')
    row=[
            json.dumps(r)
            for r in arp
        ]
    fp.write("["+"\n,".join(row)+"]")
    fp.close()

def generate_mac_file(host,device_id,fdir):
    conf=CONF.defaults()
    if CONF.has_section(device_id):
        conf=dict(CONF.items(device_id))
    conf["host"]=host
    cli=None
    if conf["host"] in conf.get("skip_hosts",None) :
        log.info("device %s[%s] skip socket connect."%(device_id,conf["host"]))
        return 
    try:
        cli=get_cli(**conf)
        log.info("device %s[%s] socket connect ok."%(device_id,conf["host"]))
    except socket.error:
        log.warning("device %s[%s] socket connect error."%(device_id,conf["host"]))    
        return
    mac=get_mac_address_table(cli=cli)
    save_mac(mac,fdir,device_id+".json")
    cli.close()

def main():
    #load CONFig
    parser = argparse.ArgumentParser(description='log arp json.')
    parser.add_argument('-v','--verbose',action='store_true',default=None,
                   help='enable verbose.')
    parser.add_argument('-d','--debug',action='store_true',default=None,
                   help='enable debug.')

    args = parser.parse_args()
    if args.verbose:
        enable_verbose()
    if args.debug:
        enable_debug()

    CONF = ConfigParser.ConfigParser()
    CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))
    conf = CONF.defaults()
    if CONF.has_section("log"):
        conf = dict(CONF.items("log"))
    logdir= conf.get("logdir",os.path.join(os.path.dirname(__file__),"var/log"))
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logging.basicConfig(filename=os.path.join(logdir,'mac.log'), level=logging.WARNING , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    now=datetime.now()
    jsonfile=os.path.join(logdir,'last.topo.json')
    fdir=os.path.join(logdir,'mac',now.strftime('%y%m/%d/%H%M%S'))
    topo=read_topology(jsonfile)
    addrs = get_entry_address(topo)
    for addr in addrs:
        generate_mac_file(addr,addrs[addr],fdir)

if __name__=="__main__":
    main()
