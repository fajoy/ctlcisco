#!/usr/bin/env python
from ctlcisco import *
from generate_topology import main as get_topology
import os,sys
import json
import ConfigParser
import logging
import socket
from datetime import datetime

import smtplib
from email.mime.text import MIMEText

log = logging.getLogger()

def enable_debug():
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

def sendmail():
    msg = MIMEText("hello this is mail.")
    fo="wuminfajoy@gmail.com"
    to="wuminfajoy@gmail.com"
    msg['Subject'] = 'hello subject.'
    msg['From'] = fo
    msg['To'] = to
    s = smtplib.SMTP('localhost')
    s.sendmail(fo, [to], msg.as_string())
    s.quit()

def read_topology(path):
    fp=open(path,'r')
    data=json.load(fp)
    fp.close()
    return data

def save_topology(path,topo):
    fp=open(path,'w')
    json.dump(devices,fp,indent=4)
    fp.close()

def main():
    #load CONFig
    CONF = ConfigParser.ConfigParser({'DEBUG': False})
    CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))
    logdir='var/log'
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logging.basicConfig(filename='var/log/mon.log' , level=logging.WARNING , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    debug=CONF.defaults().get('DEBUG',False)
    if debug:
        enable_debug()

    topo=get_topology()
    
    now=datetime.now().strftime('%y%m%d%H%M%S')
    save_topology('var/log/%s.json'%now,topo)
    old_topo=read_topology('var/log/last.json')
    save_topology('var/log/last.json',topo)

if __name__=="__main__":
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.setLevel(logging.DEBUG)
    main()
