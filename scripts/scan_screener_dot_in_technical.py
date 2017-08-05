#!/usr/bin/env python
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# This script pulls data from screener.in using one of the user's screen or any
# other public screen or just the query string itself & using screened companies to
# scan for techincal analysis.
# Right now it uses ema crossover but anything can be applied.
#
# The goal is to find out the right timings for entry in the stocks selected via
# a fundamental screener.
# Say for example you get a list of top 30 companies satisfying magic formula criteria
# (Joel Greenblatt), but still to maximize your returns you also want to apply some
# form of moving average crossover. This script is supposed to achieve things like
# that (Thus a sort of techno-fundamental screener).

import spynner
import json
import pprint
import sys
import re
import urllib, urllib2, json
import datetime
import pandas
import argparse
import copy
import time
import os
import math
import contextlib, warnings
import pprint
import shutil
from   colorama import Fore, Back, Style

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
def fetch_data(ticker, resl, t_from=None):
    if t_from == None:
        t_from = strdate_to_unixdate("01/01/1992")
    # endif
    ftch_tout = 5
    t_indx    = 0

    assert(resl in res_tbl.keys())

    while t_indx < ftch_tout:
        t_to     = unixdate_now()
        this_url = g_burl(sock) + "symbol={}&resolution={}&from={}&to={}".format(ticker, res_tbl[resl], t_from, t_to)

        #print "{} : Fetching {}".format(strdate_now(), this_url)
        response = urllib.urlopen(this_url)
        j_data   = json.loads(response.read())
        if not bool(j_data):
            print "{} : Not able to fetch.".format(strdate_now())
        else:
            break
        # endif
        t_indx   = t_indx + 1
    # endwhile

    if (t_indx >= ftch_tout):
        #print "{} : Retries exceeded !!".format(strdate_now())
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

##############################################################
# SCREENER.IN functions

# @args
#     user      : screener.in username
#     passwd    : screener.in password
#     screen_no : screen no
def screener_pull_screener_results(user, passwd, screen_info=17942):
    screen_info_type = None # 0 for no, 1 for query
    sinfo_color = Fore.MAGENTA + str(screen_info) + Fore.RESET

    # Check for Appropriate screen_info passed
    if isinstance(screen_info, int):
        print 'screen_info = {} is of type int. Assuming it to be a screen no.'.format(sinfo_color)
        screen_info_type = 0
    else:
        try:
            screen_info = int(screen_info)
            print 'screen_info = {} is of type int passed via string. Assuming it to be a screen no.'.format(sinfo_color)
            screen_info_type = 0
        except ValueError:
            print 'screen_info = {} is of type string. Assuming it to be query string.'.format(sinfo_color)
            screen_info_type = 1
        # endtry
    # endif

    # Screener.in API builders
    def screener_screener_page(page_this, screen_no=17942):
        return 'https://www.screener.in/api/screens/{}/?page={}'.format(screen_no, curr_page)
    # enddef
    def screener_screener_page_query(page_this, query_string):
        q_str = query_string.replace('\n', ' ').replace(' ', '+')
        return 'https://www.screener.in/api/screens/query/?query={}&&page={}'.format(q_str, curr_page)
    # enddef

    # Screener function to run
    screener_info_fun = (screener_screener_page if screen_info_type == 0 else screener_screener_page_query)
    
    sec_list = []
    ratios_l = []
    sec_dict = {}
    url_this = 'https://www.screener.in/login/'
    browser  = spynner.Browser()
    browser.load(url_this)
    
    # Login to screener.in
    browser.wk_fill('input[name=username]', user)
    browser.wk_fill('input[name=password]', passwd)
    browser.wk_click('button[type=submit]', wait_load=True)
    
    # Pull data
    curr_page = 1
    while True:
        sys.stdout.write('\r>> Querying page {:03}'.format(curr_page))
        sys.stdout.flush()
        sdict_this = json.loads(browser.download(screener_info_fun(curr_page, screen_info)))
        n_pages    = sdict_this['page']['total']
        ratios_l   = sdict_this['page']['ratios']
        sec_list   = sec_list + sdict_this['page']['results']
    
        # Increment
        curr_page = curr_page + 1
    
        # Check
        if curr_page > n_pages:
            break
        # endif
    # endwhile
    
    sec_dict = {
                   "results" : sec_list,
                   "ratios"  : ratios_l,
               }
    
    sys.stdout.write("\nDone !!\n")
    sys.stdout.flush()
    return sec_dict
# endif

## Return only list of company codes
def get_sec_name_list(sec_dict):
    sec_list = sec_dict["results"]
    sec_list = [ re.search(r'/company/([\d\w\-]+)/*', x[0]).groups()[0] for x in sec_list]
    return sec_list
# enddef
## Return list of company codes along with their names
def get_sec_info_list(sec_dict):
    sec_list = sec_dict["results"]
    sec_list = [ { 'code' : re.search(r'/company/([\d\w\-]+)/*', x[0]).groups()[0], 'name' : x[1]} for x in sec_list]
    return sec_list
# enddef

def screener_dot_in_pull_screener_codes(user, passwd, screen_info=17942):
    sec_dict = screener_pull_screener_results(user, passwd, screen_info)
    return get_sec_info_list(sec_dict)
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
        sec_code = sec_this['code']
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
    d_frame_c = d_frame.copy()

    # Slice the frame which needs to be plotted
    #d_frame_c = d_frame_c[-plot_period:]

    xdate     = [datetime.datetime.fromtimestamp(t) for t in d_frame_c['T']]
    rmean     = g_rmean_f(type='e')

    def mydate(x,pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
        # endtry
    # enddef

    # Plot
    fig, ax = plt.subplots()
    plt.xticks(rotation = 45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(title)
    plt.grid()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))

    # Plot candlestick
    candlestick2_ohlc(ax, d_frame_c['o'], d_frame_c['h'], d_frame_c['l'], d_frame_c['c'], width=0.6)
    # Plot mas
    for period_this in period_list:
        label = 'ema_' + str(period_this)
        d_s   = s_mode(d_frame_c, mode)
        d_frame_c[label] = rmean(d_s, period_this)
        d_frame_c[label].plot(ax=ax)
    # endfor

    fig.autofmt_xdate()
    fig.tight_layout()

    # Check if file_name was passed. If passed, save the plot to this file
    # else just plot the figure right now
    if file_name:
        plt.savefig(os.path.expanduser(file_name))
    else:
        plt.show()
    # endif
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

    ## Get values for diff emas
    o_copy['s_ema']   = rmean(d_s, period_list[0])
    o_copy['m_ema']   = rmean(d_s, period_list[1])
    o_copy['l_ema']   = rmean(d_s, period_list[2])

    # Generate signals according to chosen indicator mode
    def _g_signal(df, s_mode="12_or_23"):
        if s_mode == "12":
            df['pos'] = (df['s_ema'] > df['m_ema']).astype(int).diff()
            return df[df['pos'] != 0]
        elif s_mode == "12_or_23":
            df['pos'] = ((df['s_ema'] > df['m_ema']) | (df['m_ema'] > df['l_ema'])).astype(int).diff()
            return df[df['pos'] != 0]
        elif s_mode == "12_and_23":
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
def run_stretegy_over_all_securities(sec_dict, lag=30, strategy_name="em2_x"):
    # Start scan
    if strategy_name == "em2_x":
        sec_list    = []
        ctr         = 0

        # Hyper parameters
        period_list = [9, 14, 21]
        sig_mode    = "12"

        print 'Running {} strategy using lag={}, sig_mode={} & period_list={}'.format(strategy_name, lag, sig_mode, period_list)
        print Fore.MAGENTA + 'Peak to trough percentage has meaning only when trend is down to up !!' + Fore.RESET
        print Fore.GREEN + '--------------------- GENERATING REPORT --------------------------------' + Fore.RESET

        # Iterate over all security dict
        for sec_code in sec_dict.keys():
            # NOTE: Don't know what the hell I am calculating using these.
            #       They need to be reviewed
            def _c_up(d):
                return (d['c'].max() - d.iloc[-1]['c'])/d.iloc[-1]['c']
            # enddef
            def _c_dwn(d):
                return (d.iloc[-1]['c'] - d['c'].min())/d.iloc[-1]['c']
            # enddef
            # Fetch data
            d_this = fetch_data(sec_dict[sec_code]['ticker'], '1W')
            # Run strategy
            status, tdelta, trend_switch, d_new = run_ema2(d_this, lag=lag, period_list=period_list, sig_mode=sig_mode)
            # Analyse data
            p2t_up   = _c_up(d_new)
            p2t_down = _c_dwn(d_new)
            # Print reports
            if (status==True):
                if trend_switch:
                    t_switch = Fore.GREEN + "Down to Up" + Fore.RESET
                    p2t      = int(p2t_up * 100)
                else:
                    t_switch = Fore.RED + "Up to Down" + Fore.RESET
                    p2t      = int(p2t_down * 100)
                # endif
                sec_name = Fore.GREEN + sec_dict[sec_code]['name'] + Fore.RESET
                sys.stdout.write('{}. {} switched trend from {}, {} days ago. Peak to trough % = {}%\n'.format(ctr, sec_name, t_switch, tdelta, p2t))
                sys.stdout.flush()
                ctr = ctr + 1
            # endif
        # endfor
    else:
        print "Strategy : {}, not implemented yet !!".format(strategy_name)
    # endif
# enddef

#########################################################
# Main

if __name__ == '__main__':
    dot_invs_py = '~/.investing_dot_com_security_dict.py'
    dot_invs_py_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_invs_py)) and os.path.isfile(os.path.expanduser(dot_invs_py)):
        dot_invs_py_exists = True
    # endif

    parser  = argparse.ArgumentParser()
    parser.add_argument("--auth",    help="Screener.in authentication in form user,passwd", type=str, default=None)
    parser.add_argument("--invs",    help="Investing.com database file (populated by eq_scan_on_investing_dot_com.py)", type=str, default=None)
    parser.add_argument("--query",   help="Query string for Screener.in (Just paste from Query Builder Box from screener.in)", type=str, default=None)
    parser.add_argument("--lag",     help="Ema/Sma Crossover lag (in periods)", type=int, default=10)
    args    = parser.parse_args()

    if not args.__dict__["auth"]:
        print "--auth is required !!"
        sys.exit(-1)
    # endif
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

    # Check for query string and set the screen_info to appropriate value
    # If no query string was passed, just use a default screen no = 17942
    if args.__dict__["query"]:
        screen_info = args.__dict__["query"]
    else:
        screen_info = 17942
    # endif

    # Vars
    auth_info  = args.__dict__["auth"].replace(' ', '').split(',')
    invs_db_f  = os.path.expanduser(invs_db_file)
    ma_lag     = args.__dict__["lag"]

    # Get security list from screener.in using default screen_no=17942
    sec_list   = screener_dot_in_pull_screener_codes(auth_info[0], auth_info[1], screen_info=screen_info)
    print 'Found {} securities from Screener.in matching criteria.'.format(len(sec_list))
    sec_tick_d = populate_sym_list(invs_db_f, sec_list)

    # Run strategy function
    run_stretegy_over_all_securities(sec_tick_d, lag=ma_lag, strategy_name="em2_x")

    # DEBUG
    #d_this = fetch_data(sec_tick_d[sec_tick_d.keys()[0]]['ticker'], '1W')
# endif
