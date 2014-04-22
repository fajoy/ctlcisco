#!/usr/bin/env python
from ctlcisco import *
import os,sys
import ConfigParser
import logging
#ref http://docs.python.org/2/library/argparse.html#module-argparse
import argparse
log = logging.getLogger()

def enable_debug():
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

def usage():
    prog=os.path.basename(sys.argv[0])
    print "usage: {prog} [-h host]".format(prog=prog)

def main():
    global CONF,device_id
    #load CONFig
    CONF = ConfigParser.ConfigParser({'DEBUG': False})
    CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))
    logging.basicConfig( stream=sys.stderr , level=logging.INFO , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description='query device cdp.',add_help=False)
    parser.add_argument('-h','--host',metavar='host',nargs='?',default=None,
                   help='device ip address.')

    parser.add_argument('-d','--debug',action='store_true',default=None,
                   help='enable debug.')
    args = parser.parse_args()

    debug=args.debug
    if debug:
        enable_debug()

    kwargs=CONF.defaults()
    if args.host:
        kwargs["host"]=args.host

    cli=get_cli(**kwargs)
    kwargs={"cli":cli}
    neighbors=get_cdp_neighbors(**kwargs)
    for device_id in neighbors:
        entry=get_cdp_entry(cli,device_id)
        neighbors[device_id]["entry"]=entry
    print json.dumps(neighbors,indent=4)

if __name__=="__main__":
    main()
