#!/usr/bin/env python

import urllib2
from   bs4 import BeautifulSoup
from   tabulate import tabulate
import datetime
from   dateutil.relativedelta import relativedelta, TH
import sys
import mibian

##
# This is pretty hacked up code. Need to clean it up !!
def last_thu(month_incr=0):
    if month_incr > 2:
        print 'month_incr should be between 0 & 2'
        sys.exit(-1)
    # endif
    todayte = datetime.datetime.today()
    if (todayte.month + month_incr) % 12 == 0:
        cmon = 12
        cyear = todayte.year
    else:
        cmon    = (todayte.month + month_incr) % 12
        if cmon < todayte.month:
            cyear = todayte.year + 1
        else:
            cyear = todayte.year
        # endif
    # endif
    #print 'cmon = {}'.format(cmon)
    t       = None
    
    for i in range(1, 24):
        t = todayte + relativedelta(weekday=TH(i))
        #print 't = {}'.format(t)
        #print 't.mon = {}'.format(t.month)
        #print 'cmon = {}'.format(cmon)
        if datetime.datetime(t.year, t.month, 1) > datetime.datetime(cyear, cmon, 1):
            # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
            t = t + relativedelta(weekday=TH(-2))
            break
        # endif
    # endfor
    return t
# enddef

def last_thu_str(month_incr=0):
    mon_l   = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    exp_day = last_thu(month_incr)
    return '{}{}{}'.format(exp_day.day, mon_l[exp_day.month-1], exp_day.year)
# enddef
    
def option_table(symbol='NIFTY', month_this=0):
    url_this = 'https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTIDX&symbol={}&date={}'
    hdr_this = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}
    header_l = [ 
                 'OI', 'Chng in OI', 'Volume', 'IV', 'LTP', 'Net Chng', 'Bid Qty', 'Bid Price', 'Ask Price', 'Ask Qty',
                 'Strike Price',
                 'Bid Qty', 'Bid Price', 'Ask Price', 'Ask Qty', 'Net Chg', 'LTP', 'IV', 'Volume', 'Chng in OI', 'OI'
               ]
    header_m = [
                 'Call_OI', 'Call_Chng_in_OI', 'Call_Volume', 'Call_IV', 'Call_LTP',
                 'Call_Net_Chng', 'Call_Bid_Qty', 'Call_Bid_Price', 'Call_AskPrice', 'Call_Ask_Qty',
                 'Strike_Price',
                 'Put_Bid_Qty', 'Put_Bid_Price', 'Put_Ask_Price', 'Put_Ask_Qty', 'Put_Net_Chg',
                 'Put_LTP', 'Put_IV', 'Put_Volume', 'Put_Chng_in_OI', 'Put_OI'
               ]

    act_url  = url_this.format(symbol, last_thu_str(month_this))
    print 'Fetching from {}'.format(act_url)
    req_this = urllib2.Request(act_url, headers=hdr_this)
    page     = urllib2.urlopen(req_this)
    s_this   = page.read()
    soup     = BeautifulSoup(s_this, 'lxml')
    tbl_l    = soup.findAll('table')
    tr_l     = tbl_l[2].findAll('tr')
    
    new_tbl_l = []
    for i in range(0, len(tr_l)):
        if i == 0 or i == 1 or i == (len(tr_l) - 1):
            continue
        # endif
        d_l = [ x.text.strip('\r\n\t ').replace(',', '') for x in tr_l[i].findAll('td')]
        # First and last columns are junk
        d_l = d_l[1:-1]
        new_tbl_l.append(d_l)
    # endfor

    return new_tbl_l, header_l, header_m
# enddef

#def analyse_option_chain(option_chain, header_m):
#    new_option_table = []
#
#    # Support functions
#    def hi(header):
#        return header_m[header]
#    # enddef
#    def chk_opt_row_valid(option_row, header_list):
#        for h_this in header_list:
#            if option_row[hi(h_this)] == '-':
#                return False
#            # endif
#        # endfor
#        return True
#    # enddef
#
#    for row_this in option_chain:
#        if chk_option_row_valid(row_this, ['Call_LTP', 'Put_LTP']) == False:
#            continue
#        else:
#            c = mibian.BS(
#            greeks = {
#                         
#        # endif
#    # enddef
## enddef

if __name__ == '__main__':
    option_tbl_data, option_tbl_hdr = option_table(symbol='NIFTY', month_this=2)
    print option_tbl_data
    #print tabulate(option_tbl_data, headers=option_tbl_hdr)
# endif
