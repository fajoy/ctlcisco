#!/usr/bin/env python
from ctlcisco import *
import os,sys
import ConfigParser
import logging
#ref http://docs.python.org/2/library/argparse.html#module-argparse
import argparse
log = logging.getLogger()
CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(os.path.dirname(__file__),'etc','config.ini'))

def enable_debug():
    log.info("enable_debug.")
    log.setLevel(logging.DEBUG)

def main():
    logging.basicConfig( stream=sys.stderr , level=logging.INFO , format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description='query device cdp.')
    parser.add_argument('-d','--debug',action='store_true',default=None,
                   help='enable debug.')
    parser.add_argument("host", metavar='HOST',nargs='?',default=None,
                   help='device ip address.')

    args = parser.parse_args()

    debug=args.debug
    if debug:
        enable_debug()

    kwargs=CONF.defaults()
    if args.host:
        kwargs["host"]=args.host

    cli=get_cli(**kwargs)
    arp=get_arp(cli=cli)
    cli.close()
    row=[
            json.dumps(r)
            for r in arp 
        ]
    print "["+"\n,".join(row)+"]"

if __name__=="__main__":
    main()
