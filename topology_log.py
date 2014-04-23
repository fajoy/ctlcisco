#!/usr/bin/env python
from generate_topology import get_topology
import os,sys
import json
import ConfigParser
import argparse
import logging
from datetime import datetime

log = logging.getLogger()

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

def save_topology(path,topo):
    fp=open(path,'w')
    json.dump(topo,fp,indent=4)
    fp.close()
    return

def main():
    #load CONFig
    parser = argparse.ArgumentParser(description='log topology json.')
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
    logging.basicConfig(filename=os.path.join(logdir,'topo.log'), level=logging.WARNING , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    now=datetime.now()
    topo=get_topology()

    fpath=now.strftime('topo/%y%m/%d')
    fname=now.strftime('%H%M%S.json')
    fdir=os.path.join(logdir,fpath)
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    save_topology(os.path.join(fdir,fname),topo)
    save_topology(os.path.join(logdir,'last.topo.json'),topo)

if __name__=="__main__":
    main()
