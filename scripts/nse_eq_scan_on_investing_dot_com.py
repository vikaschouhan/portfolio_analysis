#!/usr/bin/env python
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

# NSE bhavcopy data
def nse_latest_bhavcopy_info():
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
            if item_this[1] == 'EQ':
                # Convert strings to integers/floats
                nse_dict[item_this[0]] = item_this
            # endif
        # endif
        ctr = ctr + 1
    # endfor
    return nse_dict
# enddef

# Scan for securities
def scan_securities(name):
    exchange = 'NS'
    this_url = g_bsurl(sock) + "query={}&type=Stock&exchange={}".format(name, exchange)

    #print "{} : Fetching {}".format(strdate_now(), this_url)
    response = urllib.urlopen(this_url)
    j_data   = json.loads(response.read())
    if not bool(j_data):
        print "{} : Not able to fetch.".format(strdate_now())
    # endif
    return j_data
# enddef


# Main func
if __name__ == '__main__':
    # ignore warnings
    warnings.filterwarnings("ignore")

    invs_l   = []
    output_f = os.path.expandvars('$HOME') + '/investing_dot_com_security_dict.py'
    nse_bvc  = nse_latest_bhavcopy_info()
    nse_cl   = nse_bvc.keys()
    nse_cn   = len(nse_cl)
    cn_indx  = 1

    # get socket
    sock = g_sock()
    print "sock = {}".format(sock)

    # Iterate over all keys
    for sec_name in nse_cl:
        sec_data = scan_securities(sec_name)
        if len(sec_data) > 0:
            invs_l.append(scan_securities(sec_name)[0])
        # endif
        sys.stdout.write('\r>> Querying..  {}/{}'.format(cn_indx, nse_cn))
        sys.stdout.flush()
        cn_indx = cn_indx + 1
    # endfor

    print "Done !!"

    # write to file
    with open(output_f, "w") as fout:
        pprint.pprint(invs_l, fout)
    # endwith
# enddef
