#!/usr/bin/env python
import os,sys
import datetime
import json
import logging
import argparse
log = logging.getLogger()

def enable_debug():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.setLevel(logging.DEBUG)
    log.info("enable_debug.")

def read_topology(path):
    fp=open(path,'r')
    data=json.load(fp)
    fp.close()
    return data

def get_link(topo):
    link={}
    for lname in topo:
        for rname in topo[lname]:
            if type(topo[lname][rname])!=dict or not topo[lname][rname].has_key("cdp"):
                continue
            for cdp in topo[lname][rname]["cdp"]:
                link["%s-%s cdp-> %s-%s"%(lname,cdp["local_interface"],rname,cdp["port_id"])]={
                    lname:topo.get(rname,{}).get(lname,None) ,
                    rname:topo[lname][rname]
                }
    return link
    
def check_topology(old,new):
    #log.debug(json.dumps(get_link(new),indent=4))
    ol = get_link(old)
    nl = get_link(new)
    ok = set(ol.keys())
    nk = set(nl.keys())
    diff =  dict([
                ("-lnik %s" % (k),ol[k])
                for k in (ok-nk)
            ]+[
                ("+link %s" % (k),nl[k])
                for k in (nk-ok)
            ])
    return diff

def main():
    parser = argparse.ArgumentParser(description='check topology diff.')
    parser.add_argument('-d','--debug',action='store_true',default=None,
                   help='enable debug.')
    parser.add_argument("file1", type=str,
                    help="topology file1 path")
    parser.add_argument("file2", type=str,
                    help="topology file2 path")
    args = parser.parse_args()
    if args.debug:
        enable_debug()
    old_fn=args.file1
    new_fn=args.file2
    old=read_topology(old_fn)
    new=read_topology(new_fn)

    diff=check_topology(old,new)
    if len(diff)==0:
        sys.exit(0)

    ot=os.path.getmtime(old_fn)
    nt=os.path.getmtime(new_fn)
    print "--- %s %s"%(old_fn,datetime.datetime.fromtimestamp(ot))
    print "+++ %s %s"%(new_fn,datetime.datetime.fromtimestamp(nt))
    details = {}
    for dl in diff:
        details.update(diff[dl])
        print dl

    print "====detail===="
    print json.dumps(details,indent=4)
    sys.exit(0)

if __name__=="__main__":
    main()
