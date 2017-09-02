#!/usr/bin/env python

import urllib2
from   bs4 import BeautifulSoup
from   tabulate import tabulate
import datetime
from   dateutil.relativedelta import relativedelta, TH

def last_thu():
    todayte = datetime.datetime.today()
    cmon = todayte.month
    t    = None
    
    for i in range(1, 6):
        t = todayte + relativedelta(weekday=TH(i))
        if t.month != cmon:
            # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
            t = t + relativedelta(weekday=TH(-2))
            break
        # endif
    # endfor
    return t
# enddef

def last_thu_str():
    mon_l   = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    exp_day = last_thu()
    return '{}{}{}'.format(exp_day.day, mon_l[exp_day.month-1], exp_day.year)
# enddef
    
def option_table(symbol='NIFTY'):
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

    act_url  = url_this.format(symbol, last_thu_str())
    #print 'Fetching from {}'.format(act_url)
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

    return new_tbl_l, header_l
# enddef

if __name__ == '__main__':
    option_tbl_data, option_tbl_hdr = option_table(symbol='NIFTY')
    print tabulate(option_tbl_data, headers=option_tbl_hdr)
# endif
