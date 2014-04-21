#!/usr/bin/env python
from ctlcisco import *
import os,sys
import ConfigParser
import logging
log = logging.getLogger()
logging.basicConfig( stream=sys.stderr , level=logging.INFO , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def enable_debug():
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

if __name__=="__main__":
    #load CONFig
    CONF = ConfigParser.ConfigParser({'DEBUG': False})
    CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))
    #print CONF._sections
    for k in CONF.defaults():
        locals()[k]=CONF.defaults()[k]
    if debug:
        enable_debug()
    cli=get_cli(**CONF.defaults())
    kwargs={"cli":cli}
    neighbors=get_cdp_neighbors(**kwargs)
    for device_id in neighbors:
        entry=get_cdp_entry(cli,device_id)
        neighbors[entry["device_id"]]["entry"]=entry
    print json.dumps(neighbors,indent=4)
