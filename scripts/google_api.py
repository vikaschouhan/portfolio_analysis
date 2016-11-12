#!/usr/bin/env python
#
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
#
import argparse
import random
import csv
import urllib2
import pprint
import datetime, time
import zipfile, json
import contextlib
import multiprocessing
from   multiprocessing import Process
import pymongo
from   pymongo import MongoClient
import sys, os
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO
# endtry

def unixdate_to_datetime(unix_date):
    return datetime.datetime.fromtimestamp(int(unix_date))
# enddef
def unixdate_to_strdate(unix_date, extended=True):
    if extended:
        fmt = "%a, %d %b %Y %H:%M:%S"
    else:
        fmt = "%Y-%m-%d"
    # endif
    return unixdate_to_datetime(unix_date).strftime(fmt)
# enddef
def datetime_to_strdate(date, extended=True):
    if extended:
        fmt = "%a, %d %b %Y %H:%M:%S"
    else:
        fmt = "%Y-%m-%d"
    # endif
    return date.strftime(fmt)
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

# Download latest bhavcopy
# NOTE : BSE changed date format for bhavcopy CSV some time in year 2016
def bse_latest_bhavcopy_info():
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ{:02d}{:02d}{:02d}_CSV.ZIP".format(date_y.day, date_y.month, date_y.year % 2000)
    print "Fetching BSE Bhavcopy from {}".format(url_this)
    d_data   = urllib2.urlopen(url_this)
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

# Get google url for bse code
def g_google_api_bse_url(bse_code, res='1W'):
    if res == '1W':
        return 'https://www.google.com/finance/getprices?q={}&x=BOM&i=604800&p=40Y&f=d,c,v,k,o,h,l'.format(bse_code)
    else:
        assert(False)
    # endif
# enddef

# Pull historical data via google api
# Proxy should be in format 'ip:port'
# Protocol will be assumed as http
def g_google_api_bse_historical_date(bse_code, proxy=None):
    url   = g_google_api_bse_url(bse_code)
    cfile = None

    # Install proxy
    if proxy:
        protocol    = 'http'
        proxy_ip    = proxy
        proxy_hndlr = urllib2.ProxyHandler({protocol: proxy_ip})
        opener = urllib2.build_opener(proxy_hndlr)
        urllib2.install_opener(opener)
    # endif

    with contextlib.closing(urllib2.urlopen(url)) as res:
        cfile = csv.reader(res)
        x = []
        for item in cfile:
            x.append(item)
        # endfor
        
        start_date = None
        y = []
        
        # Close, High, Low, Open, Volume
        for item in x[7:]:
            d_list = [float(item[1]), float(item[2]), float(item[3]), float(item[4]), int(item[5])]
        
            if item[0][0] == 'a':
                start_date      = unixdate_to_datetime(item[0][1:])
                start_date_str0 = unixdate_to_strdate(item[0][1:])
                start_date_str1 = unixdate_to_strdate(item[0][1:], extended=False)
                y.append([start_date_str1, start_date_str0] + d_list)
            else:
                new_date       = start_date + datetime.timedelta(int(item[0]) * 7)
                new_date_str0  = datetime_to_strdate(new_date)
                new_date_str1  = datetime_to_strdate(new_date, extended=False)
                y.append([new_date_str1, new_date_str0] + d_list)
            # endif
        # endfor

        return y
    # endwith
# enddef

# Fetch google price data via a specified proxy server
def g_google_fetch_multi(bse_codes_list, bse_bhavcopy_d, proxy, out_dir, thread_num):
    for k in bse_codes_list:
        try:
            p_list = g_google_api_bse_historical_date(k, proxy)
            print "Fetching {} from google via proxy {} with thread {}".format(k, proxy, thread_num)
            d_dict_t  = {
                            'bse_code'            : k,
                            'bse_name'            : bse_bhavcopy_d[k]['bse_name'],
                            'weekly_price_data'   : p_list,
                        }
            file_name = "{}.json".format(k)
            f_out     = open(out_dir + '/' + file_name, 'w');
            f_out.write(json.dumps(d_dict_t, indent=8));
            f_out.close();
        except:
            print " !!!!!!!!!!!! Couldn't fetch from {} !!!!!!!!!!".format(k)
            continue
        # endtry
    # endfor
# enddef


# Main function
if __name__ == '__main__':
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

    proxy_file        = args.__dict__["proxyfile"]
    out_dir           = args.__dict__["outdir"]

    # Populate bse bhavcopy
    bse_bhavcopy_d    = filter_bse_bhavcopy_by_groups(bse_latest_bhavcopy_info())
    bse_codes_list    = bse_bhavcopy_d.keys()
    n_companies       = len(bse_codes_list)

    # Initialize proxy list
    proxy_list        = populate_proxy_list1(proxy_file)
    random.shuffle(proxy_list)                   # Shuffle proxy_list
    n_threads         = len(proxy_list)
    companies_per_thr = n_companies/n_threads + 1
    procs_list        = []
    
    # Print some data
    print "proxy_list               = {}".format(proxy_list)
    print "proxy_count              = {}".format(n_threads)
    print "total_companies          = {}".format(n_companies)
    print "companies_per_px         = {}".format(companies_per_thr)

    # Write to db
    #mongo_client  = MongoClient()
    #db            = mongo_client.fscreener

    # Create output directory
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # endif

    # Start all processes
    for indx_this in range(0, n_threads):
        start_indx    = indx_this * companies_per_thr
        end_indx      = (indx_this + 1) * companies_per_thr
        if end_indx >= n_companies:
            clist_t   = bse_codes_list[start_indx : ]
        else:
            clist_t   = bse_codes_list[start_indx : end_indx]
        # endif

        process_this  = Process(target=g_google_fetch_multi, args=(clist_t, bse_bhavcopy_d, proxy_list[indx_this], out_dir, indx_this))
        procs_list.append(process_this)
        process_this.start()
    # endfor

    ## Wait on all processes to stop
    #for process_this in procs_list:
    #    process_this.stop()
    ## endfor

    #for k in bse_bhavcopy_d.keys():
    #    try:
    #        p_list    = g_google_api_bse_historical_date(k)
    #    except:
    #        print "Couldn't fetch from {}".format(k)
    #        continue
    #    # endtry
    #    p_dict    = {
    #                    'bse_code'            : k,
    #                    'bse_name'            : bse_bhavcopy_d[k]['bse_name'],
    #                    'weekly_price_data'   : p_list,
    #                }
    #    db.weekly_price.insert(p_dict)
    #    sys.stdout.write('\r')
    #    sys.stdout.flush()
    #    sys.stdout.write('{}'.format(cntr))
    #    sys.stdout.flush()
    #    cntr = cntr + 1
    ## endfor

    #mongo_client.close()
# endif
