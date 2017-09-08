#!/usr/bin/env python
#
# Author   : Vikas Chouhan
# email    : presentisgood@gmail.com
# License  : GPLv2
# NOTE     : This script pulls ticker information for all nse &/or bse stocks from http://www.investing.com.

import urllib, urllib2, json
import datetime
import pandas
import argparse
import copy
import time
import sys
import smtplib
import re
import os
import math
import contextlib, warnings
from   StringIO import StringIO
import zipfile, csv
import pprint

# Glb ds
sock = "bcbf3d08f70aaf07b860dc2f481beee5/1473605026"

# List
itype_l = ['Stock', 'Commodity']
exchg_l = ['NS', 'BO', 'MCX']

def assertm(cond, msg):
    if not cond:
        print msg
        sys.exit(-1) 
    # endif
# enddef

def chk_rng(v, nv, std_dev):
    if (nv >= v * (1.0 - std_dev/100.0)) and (nv <= v * (1.0 + std_dev/100.0)):
        return True
    return False
# enddef

def chk_rng2(v, nv, pts):
    if (nv >= (v - pts)) and (nv <= (v + pts)):
        return True
    return False
# endif

def g_sock():
    urlt = g_burlb()
    with contextlib.closing(urllib2.urlopen(urlt)) as s:
        return '/'.join(re.search('carrier=(\w+)&time=(\d+)&', s.read()).groups())
    # endwith
    assert(False)
# enddef


def g_burlb():
    return "http://tvc4.forexpros.com"
def g_burl(soc_idf):
    return g_burlb() + "/{}/1/1/8/history?".format(soc_idf)
def g_bsurl(soc_idf):
    return g_burlb() + "/{}/1/1/8/search?".format(soc_idf)

def strdate_to_unixdate(str_date):
    return int(time.mktime(datetime.datetime.strptime(str_date, '%d/%m/%Y').timetuple()))
# enddef

def unixdate_now():
    return int(time.mktime(datetime.datetime.now().timetuple()))
# enddef
def strdate_now():
    return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

# Scan for securities
def scan_securities(name, itype='', exchange='', limit=60):
    if exchange not in exchg_l:
        return 'Exchange not in {}'.format(exchg_l)
    # endif
    if itype not in itype_l:
        print 'Type not in {}'.format(itype_l)
        itype = ''
    # endif

    this_url = g_bsurl(sock) + "limit={}&query={}&type={}&exchange={}".format(limit, name, itype, exchange)

    #print "{} : Fetching {}".format(strdate_now(), this_url)
    response = urllib.urlopen(this_url)
    j_data   = json.loads(response.read())
    return j_data
# enddef

# Main func
if __name__ == '__main__':
    # ignore warnings
    warnings.filterwarnings("ignore")
    # Get socket
    sock    = g_sock()

    parser  = argparse.ArgumentParser()
    parser.add_argument("--name",   help="Name to query", type=str, default=None)
    parser.add_argument("--type",   help="Instrument type", type=str, default=None)
    parser.add_argument("--exchg",  help="Exchange", type=str, default=None)
    parser.add_argument("--list",   help="List supported options.", action='store_true')
    args    = parser.parse_args()

    if args.__dict__['list']:
        print 'Exchange List : {}'.format(exchg_l)
        print 'Type List     : {}'.format(itype_l)
        sys.exit(0)
    # endif
    if not args.__dict__['name']:
        print '--name is required !!'
        sys.exit(-1)
    # endif

    sec_data = scan_securities(args.__dict__['name'], itype=args.__dict__['type'], exchange=args.__dict__['exchg'])
    pprint.pprint(sec_data)
# enddef
