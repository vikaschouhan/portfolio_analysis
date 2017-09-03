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
import socket
import re
import os
import math
import contextlib, warnings
from   StringIO import StringIO
import zipfile, csv
import pprint
from   email.mime.multipart import MIMEMultipart
from   email.mime.text import MIMEText

# Glb ds
sock = "bcbf3d08f70aaf07b860dc2f481beee5/1473605026"

def assertm(cond, msg):
    if not cond:
        print msg
        sys.exit(-1) 
    # endif
# enddef

def month_str(m_n):
    assertm(m_n <= 12 and m_n >= 1, "Month number should be between 1 & 12")
    m_str = [ "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" ]
    return m_str[m_n-1]

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

# BSE bhavcopy data
def bse_latest_bhavcopy_info(incl_groups=['A', 'B', 'D', 'XC', 'XT', 'XD']):
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_{:02d}{:02d}{:02d}.ZIP".format(date_y.day, date_y.month, date_y.year % 2000)
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
                "bse_code"        : item_this[0].rstrip(),
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
                "isin"            : item_this[14].rstrip(),
            }

            # Check if the security is in incl_groups
            if cc_dict['bse_group'] in incl_groups:
                bse_dict[cc_dict['bse_code']] = cc_dict
            # endif
        # endif
        ctr = ctr + 1
    # endfor
    return bse_dict
# enddef


# NSE bhavcopy data
def nse_latest_bhavcopy_info(incl_series=['EQ']):
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    month_y  = month_str(date_y.month)
    day_y    = date_y.day
    year_y   = date_y.year
    #url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ{:02d}{:02d}{:02d}_CSV.ZIP".format(date_y.day, date_y.month, date_y.year % 2000)
    url_this  = "https://www.nseindia.com/content/historical/EQUITIES/{}/{}/cm{:02d}{}{}bhav.csv.zip".format(year_y, month_y, day_y, month_y, year_y)
    print "Fetching NSE Bhavcopy from {}".format(url_this)
    #print "Fetching BSE Bhavcopy from {}".format(url_this)
    u_req    = urllib2.Request(url_this)
    u_req.add_header('User-agent', 'Mozilla 5.10')
    d_data   = urllib2.urlopen(u_req)
    l_file   = StringIO(d_data.read())
    
    # Read zip file
    zip_f    = zipfile.ZipFile(l_file)
    csv_f    = csv.reader(zip_f.open(zip_f.namelist()[0]))
    nse_dict = {}
    ctr      = 0

    for item_this in csv_f:
        if ctr != 0:
            # Convert strings to integers/floats
            cc_dict = {
                "nse_code"        : item_this[0],
                "nse_group"       : item_this[1].rstrip(),
                "open"            : float(item_this[2]),
                "high"            : float(item_this[3]),
                "low"             : float(item_this[4]),
                "close"           : float(item_this[5]),
                "last"            : float(item_this[6]),
                "prev_close"      : float(item_this[7]),
                "no_trades"       : int(item_this[11]),
                "isin"            : item_this[12].rstrip(),
            }
            if item_this[1] in incl_series:
                nse_dict[cc_dict['nse_code']] = cc_dict 
            # endif
        # endif
        ctr = ctr + 1
    # endfor
    return nse_dict
# enddef

# Scan for securities
def scan_securities(name, exchange, n_sleep=4, n_timeout=4, n_tryouts=5):
    if exchange not in ['NS', 'BO']:
        print "Exchange could only be {}".format(['NS', 'BO'])
        sys.exit(-1)
    # endif
    this_url = g_bsurl(sock) + "query={}&type=Stock&exchange={}".format(name, exchange)

    #print "{} : Fetching {}".format(strdate_now(), this_url)
    for to_this in range(n_tryouts):   # n tryouts
        try:
            response = urllib2.urlopen(this_url, timeout=n_timeout)
            break
        except socket.timeout:
            print ' >>Request timed out !! Sleeping for {} seconds.'.format(n_sleep)
            time.sleep(n_sleep)
            to_this = to_this + 1
            continue
        # endtry
    # endfor

    # Check for timeouts
    if to_this == n_tryouts:
        print 'Retried timed out. Skipping !!'
        return None
    # endif

    j_data   = json.loads(response.read())
    if not bool(j_data):
        #print "\n{} : Not able to fetch.".format(strdate_now())
        pass
    # endif
    return j_data
# enddef

# Function to parse checkpoint file
def parse_ckpt_file(file_name=None):
    if file_name == None:
        return {}
    else:
        return eval(open(file_name, 'r').read())
    # endif
# endif


# Main func
if __name__ == '__main__':
    # ignore warnings
    warnings.filterwarnings("ignore")

    parser  = argparse.ArgumentParser()
    parser.add_argument("--ckpt", help="Checkpoint file", type=str, default=None)
    parser.add_argument("--query", help="Query Exchange (bse, nse etc)", type=str, default='bse,nse')
    args    = parser.parse_args()

    # Output file
    output_f = os.path.expandvars('$HOME') + '/investing_dot_com_security_dict.py'

    # Vars
    ckpt_f    = args.__dict__['ckpt']
    qe_excg   = args.__dict__['query'].replace(' ', '').split(',')

    # Exchange enable/disable
    fetch_nse = False
    fetch_bse = False
    if 'bse' in qe_excg:
        fetch_bse = True
    # endif
    if 'nse' in qe_excg:
        fetch_nse = True
    # endif
    
    # get socket
    sock = g_sock()
    # Get checkpoint list
    invs_d    = parse_ckpt_file(ckpt_f)
    isin_list = invs_d.keys()

    # Info
    print "sock = {}".format(sock)
    print "Found {} ISINs in checkpoint file.".format(len(isin_list))

    # Iterate over all keys of nse
    if fetch_nse:
        cn_indx = 1
        fn_indx = 0
        nse_bvc = nse_latest_bhavcopy_info()
        nse_cl  = nse_bvc.keys()
        nse_cn  = len(nse_cl)
        for sec_name in nse_cl:
            ## Fetch from nse
            ## Only fetch when isin_this is not present in invs_d or
            ## 'nse_code' is not present in invs_d[isin_this] otherwise
            isin_this = nse_bvc[sec_name]['isin']
            if (isin_this not in isin_list) or (u'nse_code' not in invs_d[isin_this]):
                sec_data  = scan_securities(sec_name, 'NS')
                if sec_data == None:
                    cn_indx = cn_indx + 1
                    continue
                elif len(sec_data) > 0:
                    sec_data_this                  = sec_data[0]
                    sec_data_this[u'nse_code']     = sec_name
                    sec_data_this[u'isin']         = nse_bvc[sec_name]['isin']
                else:
                    cn_indx = cn_indx + 1
                    continue
                # endif
            else:
                cn_indx = cn_indx + 1
                continue
            # endif
            ## Check if isin is already there. If not present add the full entry into the dictionary
            ## else check if nse code is there. If not, just add the nse_code
            if isin_this not in isin_list:
                invs_d[isin_this]     = sec_data_this
                fn_indx               = fn_indx + 1
                isin_list.append(isin_this)
            else:
                if u'nse_code' not in invs_d[isin_this]:
                    invs_d[isin_this][u'nse_code'] = sec_name
                    fn_indx                        = fn_indx + 1
                # endif
            # endif
            ## Print
            sys.stdout.write('\r>> Querying NSE ..  {}/{}/{}'.format(cn_indx, nse_cn, fn_indx))
            sys.stdout.flush()
            cn_indx = cn_indx + 1
        # endfor
        sys.stdout.write("\n")
        sys.stdout.flush()
    # endif

    # Iterate over all keys of bse
    if fetch_bse:
        cn_indx = 1
        fn_indx = 0
        bse_bvc = bse_latest_bhavcopy_info()
        bse_cl  = bse_bvc.keys()
        bse_cn  = len(bse_cl)
        for sec_code in bse_cl:
            ## Fetch data from bse
            ## Check if isin is already there. If not present add the full entry into the dictionary
            ## else check if bse_code is there. If not, just add the bse_code
            isin_this = bse_bvc[sec_code]['isin']
            if (isin_this not in isin_list) or (u'bse_code' not in invs_d[isin_this]):
                sec_data = scan_securities(sec_code, 'BO')
                if sec_data == None:
                    cn_indx = cn_indx + 1
                    continue
                elif len(sec_data) > 0:
                    sec_data_this                  = sec_data[0]
                    sec_data_this[u'bse_code']     = sec_code
                    sec_data_this[u'isin']         = bse_bvc[sec_code]['isin']
                else:
                    cn_indx = cn_indx + 1
                    continue
                # endif
            else:
                cn_indx = cn_indx + 1
                continue
            # endif
            ## Check if isin is already there. If not present add the full entry into the dictionary
            ## else check if bse code is there. If not, just add the bse_code
            if isin_this not in isin_list:
                invs_d[isin_this]     = sec_data_this
                fn_indx               = fn_indx + 1
                isin_list.append(isin_this)
            else:
                if u'bse_code' not in invs_d[isin_this]:
                    invs_d[isin_this][u'bse_code'] = sec_code
                    fn_indx                        = fn_indx + 1
                # endif
            # endif 
            sys.stdout.write('\r>> Querying BSE ..  {}/{}/{}'.format(cn_indx, bse_cn, fn_indx))
            sys.stdout.flush()
            cn_indx = cn_indx + 1
        # endfor
        sys.stdout.write("\n")
        sys.stdout.flush()
    # endif

    # write to file
    print "Writing to file {}".format(output_f)
    with open(output_f, "w") as fout:
        pprint.pprint(invs_d, fout)
    # endwith

    print "Done !!"
# enddef
