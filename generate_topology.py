#!/usr/bin/env python
from ctlcisco import get_cli,get_cdp_neighbors,get_cdp_entry
import os,sys
import json
import ConfigParser
import argparse
import logging
import socket
log = logging.getLogger()
CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))

def enable_debug():
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

def save_cdp(neighbors,curdir):
    if not os.path.exists(curdir):
        os.makedirs(curdir)
    filename=os.path.join(curdir,'cdp')
    fp=open(filename,'w')
    json.dump(neighbors,fp,indent=4)

def save_entry(entry,curdir):
    if not os.path.exists(curdir):
        os.makedirs(curdir)
    for p in entry:
        filename=os.path.join(curdir,p)
        fp=open(filename,'w+')
        if type(entry[p])==str:
            fp.write(entry[p])
            fp.close()
            continue
        json.dump(neighbor[p],fp,indent=4)
        fp.close()

def generate_topology_file(device_id,curdir,host=None,searched_node={}):
    conf=CONF.defaults()
    if CONF.has_section(device_id):
        conf=dict(CONF.items(device_id))
    if host:
        conf["host"]=host
    cli=None
    if conf["host"] in conf.get("skip_hosts",None) :
        log.info("device %s[%s] skip socket connect."%(device_id,conf["host"]))
        return {}
    try:
        cli=get_cli(**conf)
        log.info("device %s[%s] socket connect ok."%(device_id,conf["host"]))

    except socket.error:
        log.warning("device %s[%s] socket connect error."%(device_id,conf["host"]))    
        return {}
    neighbors=get_cdp_neighbors(cli)
    for did in neighbors:
        neighbor = neighbors[did]
        neighbor_dir=os.path.join(curdir,did)
        entry=get_cdp_entry(cli,did)
        neighbors[did]["entry"]=entry
        if searched_node.get(did,None):
            continue
        if len(entry)==0:
            log.warning("%s[%s] show cdp entry %s parse error."%(device_id,conf["host"],did))
            return neighbors
        save_entry(entry,neighbor_dir)

    if len(neighbors)==0:
        log.warning("%s[%s] show cdp neighbors parse error."%(device_id,conf["host"]))
        return neighbors
    save_cdp(neighbors,curdir)
    cli.close()
    return neighbors

def bfs_generate_topology_file(device_id,curdir,host=None,searched_node={},unsearch_queue=[],recursive=True):
    neighbors=generate_topology_file(device_id,curdir,host=host,searched_node=searched_node)
    searched_node[device_id]=neighbors
    for did in neighbors:
        neighbor=neighbors[did]
        entry=neighbor.get("entry",None)
        if not entry :
            continue
        if entry.get("entry_address(es)",None):
            host=None 
            addr=entry["entry_address(es)"].split(" ",2)
            if len(addr)>2:
                unsearch_queue.append({"device_id":did,"curdir":curdir,"host":addr[2]})
    if not recursive:     
        return neighbors

    while len(unsearch_queue):
        n=unsearch_queue.pop(0)
        if searched_node.get(n['device_id'],{}).get('is_search',None):
            continue
        bfs_generate_topology_file(
                n["device_id"]
                ,os.path.join(n['curdir'],n['device_id'])
                ,host=n["host"]
                ,searched_node=searched_node
                ,unsearch_queue=unsearch_queue
                ,recursive=False
                )
        searched_node[n['device_id']]['is_search']=True
    return searched_node

def get_topology():
    device_id=CONF.defaults().get("device_id","root")
    root_dir=os.path.join(os.path.dirname(__file__),device_id)
    return bfs_generate_topology_file(device_id,root_dir)

def main():
    logging.basicConfig(stream=sys.stderr , level=logging.INFO , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description='genereate topology file.')
    parser.add_argument('-d','--debug',action='store_true',default=None,
                   help='enable debug.')
    args = parser.parse_args()
    if args.debug:
        enable_debug()
    get_topology()

if __name__=="__main__":
    main()
