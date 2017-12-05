#!/usr/bin/env python
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# Right now it uses ema crossover but anything can be applied.
#
# The goal is to find out the right timings for entry in the stocks selected via
# a fundamental screener.
# Say for example you get a list of top 30 companies satisfying magic formula criteria
# (Joel Greenblatt), but still to maximize your returns you also want to apply some
# form of moving average crossover. This script is supposed to achieve things like
# that (Thus a sort of techno-fundamental screener).

import json
import pprint
import sys
import re
import urllib, urllib2, json
import socket
import datetime
import pandas
import argparse
import copy
import time
import os
import math
import csv
import contextlib, warnings
import shutil
from   colorama import Fore, Back, Style
from   matplotlib.finance import candlestick2_ohlc, volume_overlay
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime as datetime
import numpy as np
import logging
from   subprocess import call, check_call
import requests
from   bs4 import BeautifulSoup

# Switch backend
plt.switch_backend('agg')

#################################################################
# GLOBALS
headers = {'User-agent' : 'Mozilla/5.0'}
sleep_time = 4

##################################################################
# MARKETSMOJO.COM functions
def pull_info_from_marketsmojo(scrip):
    url_search = 'https://www.marketsmojo.com/portfolio-plus/frontendsearch?SearchPhrase={}'
    url_front  = 'https://www.marketsmojo.com'
    company_l  = []

    req_this   = requests.get(url_search.format(scrip))
    if req_this.json() == []:
        print 'Nothing found for {} !!'.format(scrip)
        return None
    # endif

    # Go over all of them
    for item_this in req_this.json():
        url_page = url_front + item_this[u'url']
        company  = item_this[u'Company'].replace('<b>', '').replace('</b>', '')
        bse_code = int(item_this[u'ScriptCode'])
        nse_code = item_this[u'Symbol']
        pg_this  = requests.get(url_page)

        # Parse using beautifulsoup
        html_page = BeautifulSoup(pg_this.text, 'html.parser')
        ##
        valuation = html_page.find('div', {'class' : 'valuation cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')
        quality   = html_page.find('div', {'class' : 'quality cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')
        fin_trend = html_page.find('div', {'class' : 'financials cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')

        company_l.append({
                             "name"         : company,
                             "bsecode"      : bse_code,
                             "nse_code"     : nse_code,
                             "valuation"    : valuation,
                             "quality"      : quality,
                             "fintrend"     : fin_trend,
                        })
    # endfor

    return company_l
# enddef

##################################################################
# INVESTING.COM FUNCTIONS
#

sock = "bcbf3d08f70aaf07b860dc2f481beee5/1473605026"
res_tbl = {
              "1m"     : 1,
              "5m"     : 5,
              "15m"    : 15,
              "30m"    : 30,
              "1h"     : 60,
              "4h"     : 240,
              "5h"     : 300,
              "1D"     : "D",
              "1W"     : "W",
              "1M"     : "M",
          }

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

def strdate_to_unixdate(str_date):
    return int(time.mktime(datetime.datetime.strptime(str_date, '%d/%m/%Y').timetuple()))
# enddef

def unixdate_now():
    return int(time.mktime(datetime.datetime.now().timetuple()))
# enddef
def strdate_now():
    return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
# enddef

# Fetch from investing.com
def fetch_data(ticker, resl, t_from=None, t_timeout=4):
    if t_from == None:
        t_from = strdate_to_unixdate("01/01/1992")
    # endif
    ftch_tout = 5
    t_indx    = 0

    assert(resl in res_tbl.keys())

    while t_indx < ftch_tout:
        t_to     = unixdate_now()
        this_url = g_burl(sock) + "symbol={}&resolution={}&from={}&to={}".format(ticker, res_tbl[resl], t_from, t_to)

        logging.debug("{} : Fetching {}".format(strdate_now(), this_url))
        try:
            this_req = urllib2.Request(this_url, None, headers)
            response = urllib2.urlopen(this_req, timeout=t_timeout)
            j_data   = json.loads(response.read())
            if not bool(j_data):
                logging.debug("{} : Not able to fetch.".format(strdate_now()))
                logging.debug("{} : Returned {}".format(strdate_now(), j_data))
            else:
                break
            # endif
        except socket.error:
            # Just try again after a pause if encountered an 104 error
            logging.debug('Encountered socket error. Retrying after {} seconds..'.format(sleep_time))
            time.sleep(sleep_time)
        except urllib2.URLError:
            logging.debug('Encountered timeout error. Retrying after {} seconds..'.format(sleep_time))
            time.sleep(sleep_time)
        # endtry
        t_indx   = t_indx + 1
    # endwhile

    if (t_indx >= ftch_tout):
        logging.debug("{} : Retries exceeded !!".format(strdate_now()))
        # Exit
        sys.exit(-1)
    # endif

    # Get basic pb_frame
    def g_pdbase(j_data):
        x_alt_a  = range(0, len(j_data['c']))
        t_data   = [ datetime.datetime.fromtimestamp(int(x)) for x in j_data['t'] ]
        d_frame  = pandas.DataFrame(index=x_alt_a)
    
        d_frame['c'] = j_data['c']
        d_frame['o'] = j_data['o']
        d_frame['h'] = j_data['h']
        d_frame['l'] = j_data['l']
        d_frame['t'] = t_data
        d_frame['T'] = j_data['t']

        if 'v' in j_data:
            d_frame['v']  = j_data['v']
        # endif
        if 'vo' in j_data:
            d_frame['vo'] = j_data['vo']
        # endif
    
        return d_frame
    # enddef

    #print "{} : Fetched data. done !!".format(strdate_now())
    return g_pdbase(j_data)
# enddef


################################################
# GENERIC

# Function to parse checkpoint file
def parse_dict_file(file_name=None):
    if file_name == None:
        return {}
    else:
        return eval(open(file_name, 'r').read())
    # endif
# endif

# Function to populate sec csv file in mentioned format to symbol list
def populate_sec_list(sfile):
    sec_list      = []
    l_ctr         = 0
    file_type     = None
    file_type_l   = ['nse_eqlist', 'nse_eqlist_m', 'bse_eqlist', 'nse_fo_mktlots']
    with open(sfile, 'r') as file_h:
        for l_this in file_h:
            l_ctr = l_ctr + 1
            if l_ctr == 1:
                # Get file_type header (1st line)
                file_type = l_this.replace('\n', '').replace('\r', '').replace(' ', '')
                if file_type in file_type_l:
                    print Fore.MAGENTA + 'File type seems to be {} !!'.format(file_type) + Fore.RESET
                else:
                    print Fore.MAGENTA + 'Unsupported file type {}. Ensure that first line of csv file specifies file_type !!'.format(file_type) + Fore.RESET
                    sys.exit(-1)
                # endif
                continue
            # endif
            if re.match('^\s*#', l_this):
                continue
            # endif

            if file_type == 'bse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[2],
                               })
            elif file_type == 'nse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[2],
                                    'name' : s_arr[0],
                               })
            elif file_type == 'nse_eqlist_m':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[1],
                               })
            elif file_type == 'nse_fo_mktlots':
                if re.match('UNDERLYING', l_this) or re.match('Derivatives in', l_this):
                    continue
                # endif
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[1].replace(' ', ''),
                                    'name' : s_arr[0],
                               })
            elif file_type == None:
                continue
            # endif
        # endfor
    # endwith
    return sec_list
# enddef

def populate_sym_list(invs_dict_file, sec_list):
    # Convert inv_dot_com_db_list to dict:
    inv_dot_com_db_dict = parse_dict_file(invs_dict_file)
    # Generate nse dict
    nse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'nse_code' in item_this and item_this[u'nse_code']:
            nse_dict[item_this[u'nse_code']] = item_this
        # endif
    # endfor
    # Generate bse dict
    bse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'bse_code' in item_this and item_this[u'bse_code']:
            bse_dict[item_this[u'bse_code']] = item_this
        # endif
    # endfor

    # code list
    nse_keys = nse_dict.keys()
    bse_keys = [unicode(x) for x in bse_dict.keys()]

    # Search for tickers
    sec_dict = {}
    not_f_l  = []
    for sec_this in sec_list:
        sec_code = unicode(sec_this['code'], 'utf-8')
        sec_name = sec_this['name']
        # Search
        if sec_code in nse_keys:
            sec_dict[sec_code] = {
                                     'ticker' : nse_dict[sec_code][u'ticker'],
                                     'name'   : nse_dict[sec_code][u'description'],
                                 }
        elif sec_code in bse_keys:
            sec_dict[sec_code] = {
                                     'ticker' : bse_dict[sec_code][u'ticker'],
                                     'name'   : bse_dict[sec_code][u'description'],
                                 }
        else:
            not_f_l.append(sec_this)
        # endif
    # endfor
    print Back.RED + '{} not found in investing.com db'.format(not_f_l) + Back.RESET

    return sec_dict
# enddef

####################################################
# PLOTTING FUNCTIONS
#
def gen_candlestick(d_frame, mode='c', period_list=[], title='', file_name=None, plot_period=None):
    logging.debug('Generating candlestick chart for {}'.format(title))

    # Make a clone
    d_frame_c_c = d_frame.copy()

    # Slice the frame which needs to be plotted
    d_frame_c = d_frame_c_c[-plot_period:].copy()

    # Get date list and rmean function
    xdate     = [datetime.datetime.fromtimestamp(t) for t in d_frame_c['T']]
    rmean     = g_rmean_f(type='e')

    def mydate(x,pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
        # endtry
    # enddef

    # Pre-processing
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    plt.xticks(rotation = 45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(title)

    # Plot candlestick
    candlestick2_ohlc(ax, d_frame_c['o'], d_frame_c['h'], d_frame_c['l'], d_frame_c['c'], width=0.6)
    ## Plot mas
    for period_this in period_list:
        label = 'ema_' + str(period_this)
        d_s   = s_mode(d_frame_c, mode)
        d_frame_c[label] = rmean(d_s, period_this)
        d_frame_c.reset_index(inplace=True, drop=True)
        d_frame_c[label].plot(ax=ax)
    # endfor
    # Plot volume
    v_data = [ 0 if j == 'n/a' else j for j in d_frame_c['v'] ]
    ax2 = ax.twinx()
    bc = volume_overlay(ax2, d_frame_c['o'], d_frame_c['c'], v_data, colorup='g', alpha=0.2, width=0.6)
    ax2.add_collection(bc)

    # Post-processing
    plt.grid()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    fig.autofmt_xdate()
    #fig.tight_layout()

    # Check if file_name was passed. If passed, save the plot to this file
    # else just plot the figure right now
    if file_name:
        plt.savefig(os.path.expanduser(file_name))
    else:
        plt.show()
    # endif

    # Close figure to save memory
    plt.close()
# enddef

####################################################
# SCANNERS
#
# Get mean generating f
def g_rmean_f(**kwargs):
    se_st = kwargs.get('type', 's')    # "s" or "e"
    if se_st == 's':
        return lambda s, t: pandas.rolling_mean(s, t)
    elif se_st == 'e':
        return lambda s, t: pandas.Series.ewm(s, span=t, adjust=False).mean()
    else:
        assert(False)
    # endif
# enddef

# EMA

def s_mode(f_frame, mode='c'):
    m_list = ['o', 'c', 'h', 'l', 'hl2', 'hlc3', 'ohlc4']
    if not mode in m_list:
        print "mode should be one of {}".format(m_list)
        sys.exit(-1)
    # endif

    if mode == 'o':
        return f_frame['o']
    elif mode == 'c':
        return f_frame['c']
    elif mode == 'h':
        return f_frame['h']
    elif mode == 'l':
        return f_frame['l']
    elif mode == 'hl2':
        return (f_frame['h'] + f_frame['l'])/2.0
    elif mode == 'hlc3':
        return (f_frame['h'] + f_frame['l'] + f_frame['c'])/3.0
    elif mode == 'ohlc4':
        return (f_frame['o'] + f_frame['h'] + f_frame['l'] + f_frame['c'])/4.0
    else:
        assert(False)
    # endif
# enddef

def v_i(s, indx):
    return s.values[indx]
# enddef

# Comparator functions
def c_f_0(ma_p0, ma_p1, ma_p2, lag=30):
    if ma_p0.shape[0] <= lag or ma_p1.shape[0] <= lag or ma_p2.shape[0] <= lag:
        return False
    # endif
    if (v_i(ma_p0, -1) >= v_i(ma_p1, -1) >= v_i(ma_p2, -1)) and \
            (v_i(ma_p0, -1-lag) <= v_i(ma_p1, -1-lag) <= v_i(ma_p2, -1-lag)):
        return True
    # endif
    return False
# endif
def c_f_1(ma_p0, ma_p1, lag=30):
    if ma_p0.shape[0] <= lag or ma_p1.shape[0] <= lag:
        return False
    # endif
    if (v_i(ma_p0, -1) >= v_i(ma_p1, -1)) and \
            (v_i(ma_p0, -1-lag) <= v_i(ma_p1, -1-lag)):
        return True
    # endif
    return False
# endif

# Add volume moving average to the data frame
def add_vol_ma(o_frame, period_list):
    of_copy = o_frame.copy()
    rmean   = g_rmean_f(type='e')
    of_copy['v_ma'] = rmean(of_copy['v'], period_list[0])
    return of_copy
# enddef

# Strategy
def run_ema(o_frame, mode='c', period_list=[14, 21], lag=30):
    if len(period_list) != 2:
        print 'period_list should have only two elements (p0, p1). p0 is smaller time-period & p1 is larger one.'
        sys.exit(-1)
    # endif
    d_s     = s_mode(o_frame, mode)
    rmean   = g_rmean_f(type='e')

    ## Get values
    ma_p0   = rmean(d_s, period_list[0])
    ma_p1   = rmean(d_s, period_list[1])

    return c_f_1(ma_p0, ma_p1, lag=lag)
# enddef

# A ema crossover strategy for detecting crossovers on the frame passed
def run_ema2(o_frame, mode='c', lag=30, period_list=[9, 14, 21], sig_mode=None):
    d_s     = s_mode(o_frame, mode)
    rmean   = g_rmean_f(type='e')
    o_copy  = o_frame.copy()   # Make a copy
    status  = False
    trend_switch = None

    # Generate signals according to chosen indicator mode
    def _g_signal(df, s_mode="12_or_23"):
        ## Get values for diff emas
        df['s_ema']   = rmean(d_s, period_list[0])
        df['m_ema']   = rmean(d_s, period_list[1])
        
        if s_mode == "12":
            df['pos'] = (df['s_ema'] > df['m_ema']).astype(int).diff()
            return df[df['pos'] != 0]
        elif s_mode == "12_or_23":
            df['l_ema']   = rmean(d_s, period_list[2])
            df['pos'] = ((df['s_ema'] > df['m_ema']) | (df['m_ema'] > df['l_ema'])).astype(int).diff()
            return df[df['pos'] != 0]
        elif s_mode == "12_and_23":
            df['l_ema']   = rmean(d_s, period_list[2])
            df['pos'] = ((df['s_ema'] > df['m_ema']) & (df['m_ema'] > df['l_ema'])).astype(int).diff()
            return df[df['pos'] != 0]
        else:
            print 'Unknown mode {} in _g_signal().'.format(s_mode)
            sys.exit(-1)
        # endif
    # enddef

    # Generate signals
    o_copy = _g_signal(o_copy, sig_mode)
    
    # Get time different between last position switch and now
    tdelta = pandas.Timestamp(datetime.datetime.now()) - o_copy.iloc[-1]['t']

    # Last trend switch
    if o_copy.iloc[-1]['pos'] == 1.0:
        trend_switch = 1
    else:
        trend_switch = 0
    # endif

    # Check if lag > tdelta
    if lag > tdelta.days:
        status = True
    # endif

    # Return only date/time, close price and position switches
    return status, tdelta.days, trend_switch, o_copy[['t', 'c', 'pos']][-10:]
# enddef

# Common Wrapper over all strategies
def run_stretegy_over_all_securities(sec_dict, lag=30, res='1W', strategy_name="em2_x", period_list=[9, 14, 21],
                                     plots_dir=None, only_down2up=False, rep_file=None, plot_monthly=False, invoke_marketsmojo=True):
    csv_report_file = '~/csv_report_security_list_{}.csv'.format(datetime.datetime.now().date().isoformat()) if rep_file == None else rep_file
    csv_rep_list    = []

    # Headers
    header_l        = ['Name', 'Switch Direction', 'Time Delta', 'Peek to Trough %', 'Price', 'Volume Up']
    if invoke_marketsmojo:
        header_l    = header_l + ['Valuation', 'Quality', 'Fin Trend']
    # endif

    if plots_dir:
        plots_dir = os.path.expanduser(plots_dir)
        if not os.path.isdir(plots_dir):
            print "{} doesn't exist. Creating it now !!".format(plots_dir)
            os.makedirs(plots_dir)
        # endif
        print 'Plots dir = {}'.format(plots_dir)
    # endif

    # Start scan
    if strategy_name == "em2_x":
        sec_list    = []
        ctr         = 0
        ctr2        = 0
        # Add csv headers
        csv_rep_list.append(header_l)

        # Hyper parameters
        period_list = [9, 14, 21] if period_list == None else period_list
        sig_mode    = "12"

        print 'Running {} strategy using lag={}, sig_mode={} & period_list={}'.format(strategy_name, lag, sig_mode, period_list)
        print Fore.MAGENTA + 'Peak to trough percentage has meaning only when trend is down to up !!' + Fore.RESET
        print Fore.GREEN + '--------------------- GENERATING REPORT --------------------------------' + Fore.RESET

        # Iterate over all security dict
        for sec_code in sec_dict.keys():
            ctr2    = ctr2 + 1
            logging.debug("{} : Running {} strategy over {}".format(ctr2, strategy_name, sec_code))
            # NOTE: Don't know what the hell I am calculating using these.
            #       They need to be reviewed
            def _c_up(d):
                return (d['c'].max() - d.iloc[-1]['c'])/d.iloc[-1]['c']
            # enddef
            def _c_dwn(d):
                return (d.iloc[-1]['c'] - d['c'].min())/d.iloc[-1]['c']
            # enddef
            def _vol_up(d):
                try:
                    return (d.iloc[-1]['v_ma'] - d.iloc[-10]['v_ma'])/d.iloc[-10]['v_ma']
                except:
                    return 0
                # endif
            # enddef
            # Fetch data
            d_this = fetch_data(sec_dict[sec_code]['ticker'], res)
            # Run strategy
            logging.debug("{} : Running ema crossover function over {}".format(ctr2, sec_code))
            status, tdelta, trend_switch, d_new = run_ema2(d_this, lag=lag, period_list=period_list, sig_mode=sig_mode)
            # Add volume ma
            d_v_this = add_vol_ma(d_this, period_list=period_list)
            # Analyse data
            p2t_up   = _c_up(d_new)
            p2t_down = _c_dwn(d_new)
            vol_up   = _vol_up(d_v_this)
            # Print reports
            if (status==True):
                if trend_switch:
                    t_swt    = "Down2Up"
                    t_switch = Fore.GREEN + "Down to Up" + Fore.RESET
                    p2t      = int(p2t_up * 100)
                else:
                    t_swt    = "Up2Down"
                    t_switch = Fore.RED + "Up to Down" + Fore.RESET
                    p2t      = int(p2t_down * 100)
                # endif
                # If only down2up is to be shown and trend_switch is up to down, just continue
                # and don't show anything
                if only_down2up and not trend_switch:
                    continue
                else:
                    # Add rep list entry
                    row_this = [sec_dict[sec_code]['name'], t_swt, str(tdelta), str(p2t), d_this.iloc[-1]['c'], vol_up]
                    if invoke_marketsmojo:
                        info_this = pull_info_from_marketsmojo(sec_code)
                        # If nothing returned
                        if info_this == None:
                            row_this  = row_this + ['-', '-', '-']
                        else:
                            info_this = info_this[0]  # Pick only first element
                            # Add assertion
                            # FIXME : fix this assertion
                            #assert(row_this['bsecode'] == sec_code or row_this['nsecode'] == sec_code)
                            # Add to the main row
                            row_this  = row_this + [info_this['valuation'], info_this['quality'], info_this['fintrend']]
                        # endif
                    # endif
                    csv_rep_list.append(row_this)

                    # Print
                    sec_name = Fore.GREEN + sec_dict[sec_code]['name'] + Fore.RESET
                    sys.stdout.write('{}. {} switched trend from {}, {} days ago. Peak to trough % = {}%\n'.format(ctr, sec_name, t_switch, tdelta, p2t))
                    sys.stdout.flush()
                    ctr = ctr + 1
                # endif

                # Save plot
                if plots_dir:
                    pic_name = plots_dir + '/' + sec_dict[sec_code]['name'].replace(' ', '_') + '.png'
                    gen_candlestick(d_this, period_list=period_list, title=sec_dict[sec_code]['name'], plot_period=100, file_name=pic_name)
                    # Plot monthly chart if required
                    if plot_monthly:
                        d_mon    = fetch_data(sec_dict[sec_code]['ticker'], '1M')
                        pic_name = plots_dir + '/' + sec_dict[sec_code]['name'].replace(' ', '_') + '_monthly.png'
                        gen_candlestick(d_this, title=sec_dict[sec_code]['name'], plot_period=200, file_name=pic_name)
                    # endif
                # endif
            # endif
        # endfor
    else:
        print "Strategy : {}, not implemented yet !!".format(strategy_name)
    # endif

    # Write to csv file
    print Fore.GREEN + '--------------------- REPORT END --------------------------------' + Fore.RESET
    print 'Writing report file to {}'.format(csv_report_file)
    with open(os.path.expanduser(csv_report_file), 'w') as f_out:
        csv_writer = csv.writer(f_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item_this in csv_rep_list:
            csv_writer.writerow(item_this)
        # endfor
    # endwith

    return csv_report_file
# enddef

#########################################################
# Main

if __name__ == '__main__':
    # Logging init
    logging.basicConfig(filename='/tmp/scan_security_list_technical.py.log', filemode='w', level=logging.DEBUG)

    dot_invs_py = '~/.investing_dot_com_security_dict.py'
    dot_invs_py_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_invs_py)) and os.path.isfile(os.path.expanduser(dot_invs_py)):
        dot_invs_py_exists = True
    # endif

    parser  = argparse.ArgumentParser()
    parser.add_argument("--invs",    help="Investing.com database file (populated by eq_scan_on_investing_dot_com.py)", type=str, default=None)
    parser.add_argument("--lag",     help="Ema/Sma Crossover lag (in days)", type=int, default=10)
    parser.add_argument("--res",     help="Resolution", type=str, default='1W')
    parser.add_argument("--ma_plist",help="Moving average period list", type=str, default=None)
    parser.add_argument("--sfile",   help="Security csv file. Can be list file or bhavcopy file.", type=str, default=None)
    parser.add_argument("--down2up", help="Only should securities with down to up trend switch.", action="store_true")
    parser.add_argument("--plots_dir", \
            help="Directory where plots are gonna stored. If this is not passed, plots are not generated at all.", type=str, default=None)
    parser.add_argument("--plot_mon",help="Plot monthly charts.", action='store_true')
    args    = parser.parse_args()

    if not args.__dict__["invs"]:
        if dot_invs_py_exists:
            print 'Using {} as Investing.com database file.'.format(dot_invs_py)
            invs_db_file = dot_invs_py
        else:
            print "--invs is required !!"
            sys.exit(-1)
        # endif
    else:
        print 'Using {} as Investing.com database file.'.format(args.__dict__["invs"])
        invs_db_file = args.__dict__["invs"]

        # Copy the passed file to dot_invs_py
        print 'Copying {} to {} ..'.format(invs_db_file, dot_invs_py)
        shutil.copyfile(os.path.expanduser(invs_db_file), os.path.expanduser(dot_invs_py))
    # endif
    if not args.__dict__["sfile"]:
        print "--sfile is required !!"
        sys.exit(-1)
    # endif
    if not args.__dict__["ma_plist"]:
        ma_plist = [9, 14, 21]
    else:
        ma_plist = [ int(x) for x in args.__dict__["ma_plist"].split(',') ]
    # endif

    # Vars
    invs_db_f  = os.path.expanduser(invs_db_file)
    sec_file   = args.__dict__["sfile"]
    ma_lag     = args.__dict__["lag"]
    res        = args.__dict__["res"]
    down2up    = args.__dict__["down2up"]
    plot_m     = args.__dict__["plot_mon"]

    # Get security list from screener.in using default screen_no=17942
    sec_list   = populate_sec_list(sfile=sec_file)

    print 'Found {} securities.'.format(len(sec_list))
    sec_tick_d = populate_sym_list(invs_db_f, sec_list)
    print 'Found {} securities in investing_com database.'.format(len(sec_tick_d))

    # Run strategy function
    rep_file = '~/csv_report_security_list_{}_{}.csv'.format(os.path.basename(sec_file).split('.')[0], datetime.datetime.now().date().isoformat())
    rep_file = run_stretegy_over_all_securities(sec_tick_d, lag=ma_lag, res=res, strategy_name="em2_x", \
                   period_list=ma_plist, plots_dir=args.__dict__["plots_dir"], only_down2up=down2up, rep_file=rep_file, \
                   plot_monthly=plot_m)

    # Upload to google-drive (just a temporary solution. Will change it later)
    status = check_call(['gdrive-linux-x64', 'upload', os.path.expanduser(rep_file)])

    # DEBUG
    #d_this = fetch_data(sec_tick_d[sec_tick_d.keys()[0]]['ticker'], '1W')
# endif
