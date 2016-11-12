#!/usr/bin/env python
#
# Author : Vikas Chouhan
# email  : presentisgood@gmail.com
#
# screener_in.py is an automated script for downloading financial data from
# http://www.screener.in. It takes company database in a special json format
# (generated from BSE bhavcopy by a customized script) and downloads financial
# data corrresponding to all companies in the bhavcopy.
# It also accepts a proxyfile parameter wherein we can specify different proxy
# servers. The script automatically divides the work into a specific number of worker
# processes and each process uses one proxy from the list of proxy servers.
# This helps to avoid getting kicked out by the server, if there are too many requests.

# NOTE : This script uses spynner python module to function properly.
import time
import os
import json
import sys
import zipfile
import csv
import urllib
import argparse
import multiprocessing
from   multiprocessing import Process
from   StringIO import StringIO
import datetime
import spynner
import random

def assertm(cond, msg):
    if not cond:
        print msg
        sys.exit(-1)
    # endif
# enddef

# Populate proxy list
def populate_proxy_list(proxy_file):
    proxy_list    = []
    f_in          = open(proxy_file, "r")
    for line_this in f_in:
        proxy_list.append(line_this[0:-1])  # Removing '\n'
    # endfor
    return proxy_list
# enddef

def populate_proxy_list1(proxy_file):
    proxy_list    = []
    f_in          = open(proxy_file, "r")
    for line_this in f_in:
        proxy_list.append(":".join(line_this.rstrip("\n").rstrip(" ").replace("\t", " ").split(" ")[0:2]))
    # endfor
    return proxy_list
# enddef

# Populate proxy list
def populate_proxy_list2(proxy_file):
    proxy_list    = []
    f_in          = open(proxy_file, "r")
    for line_this in f_in:
        proxy_list.append(line_this[0:-1])  # Removing '\n'
    # endfor
    return proxy_list
# enddef

# Filter bse bhavcopy via groups
def filter_bse_bhavcopy_by_groups(bse_bhavcopy_d, incl_groups=['A', 'B', 'D', 'XC', 'XT', 'XD']):
    bse_bhavcopy_dn = {}
    for k in bse_bhavcopy_d.keys():
        if bse_bhavcopy_d[k]['bse_group'] in incl_groups:
            bse_bhavcopy_dn[k] = bse_bhavcopy_d[k]
        # endif
    # endfor
    return bse_bhavcopy_dn
# enddef

# Download latest bhavcopy
def bse_latest_bhavcopy_info():
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ{:02d}{:02d}{:02d}_CSV.ZIP".format(date_y.day, date_y.month, date_y.year % 2000)
    print "Fetching BSE Bhavcopy from {}".format(url_this)
    d_data   = urllib.urlopen(url_this)
    l_file   = StringIO(d_data.read())
    
    # Read zip file
    zip_f    = zipfile.ZipFile(l_file)
    csv_f    = csv.reader(zip_f.open(zip_f.namelist()[0]))
    bse_dict = {}
    ctr      = 0

    for item_this in csv_f:
        # Convert strings to integers/floats
        if ctr != 0:
            cc_dict = {
                "bse_code"        : int(item_this[0]),
                "bse_name"        : item_this[1].rstrip(),
                "bse_group"       : item_this[2].rstrip(),
                "bse_type"        : item_this[3].rstrip(),
                "open"            : float(item_this[4]),
                "high"            : float(item_this[5]),
                "low"             : float(item_this[6]),
                "close"           : float(item_this[7]),
                "last"            : float(item_this[8]),
                "prev_close"      : float(item_this[9]),
                "no_trades"       : int(item_this[10]),
                "no_shares"       : int(item_this[11]),
                "net_turnover"    : float(item_this[12]),
            }
            bse_dict[cc_dict['bse_code']] = cc_dict
            #db.screener_in.update({ 'bse_code' : cc_dict['bse_code'] }, { '$set' : { 'bse_bhavcopy' : cc_dict } })
        # endif
        ctr = ctr + 1
    # endfor
    return bse_dict
# enddef

# companydb    : company database in json format
# proxy_this   : proxy in ip:port format
# out_dir      : output dir
def main_thread(companydb, proxy_this, out_dir):
    api_path      = "http://www.screener.in/api/company/"

    # Create output directory
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # endif

    # Browser
    browser = spynner.Browser()
    
    for index_this in range(0, len(companydb)):
    #for index_this in range(0, 5):
        item_this     = companydb[index_this]
        bse_code      = item_this["bse_code"]
        company_name  = item_this["bse_name"]
        file_name     = out_dir + "/" + str(bse_code) + ".json"
        url_this      = api_path + str(bse_code) + "/"
    
        # Check if output file already exists
        if os.path.exists(file_name):
            print "{} already exists !!".format(file_name)
            continue
        # endif
    
        # Get JSON content
        try:
            print "fetching {} via proxy {}".format(url_this, proxy_this)
            content_this  = browser.download(url_this, proxy_url=proxy_this)
            content_json  = json.loads(content_this)
        except ValueError:
            print "Error encountered while fetching {} via proxy {}.".format(url_this, proxy_this)
            continue
        # endtry

        # Check
        if "detail" in content_json and content_json["detail"] == "Not found.":
            print "Wrong URL {}. Page returned with content not found !!".format(url_this)
            continue
        # endif
   
        # Write ouput json to file
        f_out         = open(file_name, 'w');
        f_out.write(json.dumps(content_json, indent=8));
        f_out.close();
    # endfor
    
    # Close browser
    browser.close()
# enddef


# Main
if __name__ == "__main__":
    parser  = argparse.ArgumentParser()
    parser.add_argument("--proxyfile", help="file containing list of proxy servers to use", type=str, default=None)
    parser.add_argument("--outdir", help="output directory for downloaded data", type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["proxyfile"]:
        print "--proxyfile is required !!"
        sys.exit(-1)
    # endif
    if not args.__dict__["outdir"]:
        print "--outdir is required !!"
        sys.exit(-1)
    # endif

    # Vars
    proxy_file        = args.__dict__["proxyfile"]
    out_dir           = args.__dict__["outdir"]
    bse_bhavcopy      = filter_bse_bhavcopy_by_groups(bse_latest_bhavcopy_info())

    # Initialize proxy list
    proxy_list        = populate_proxy_list1(proxy_file)
    # Shuffle proxy list
    random.shuffle(proxy_list)
    proxy_count       = len(proxy_list)
    # Initialize json dbase, companydb is a list actually
    companydb         = bse_bhavcopy.values()
    companies_per_px  = len(companydb)/proxy_count + 1
    
    # Print some data
    print "proxy_list               = {}".format(proxy_list)
    print "proxy_count              = {}".format(proxy_count)
    print "total_companies          = {}".format(len(companydb))
    print "companies_per_px         = {}".format(companies_per_px)

    # Start all processes
    for indx_this in range(0, len(proxy_list)):
        proxy_this    = proxy_list[indx_this]
        start_indx    = indx_this * companies_per_px
        end_indx      = (indx_this + 1) * companies_per_px
        if end_indx >= len(proxy_list):
            cdb       = companydb[start_indx : ]
        else:
            cdb       = companydb[start_indx : end_indx]
        # endif

        process_this  = Process(target=main_thread, args=(cdb, proxy_this, out_dir))
        process_this.start()
    # endfor

# endif
