#!/usr/bin/env python
#
# Author  : Vikas Chouhan (presentisgood@gmail.com)
# License : GPLv2

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
from   email.mime.multipart import MIMEMultipart
from   email.mime.text import MIMEText
from   email.mime.application import MIMEApplication
import matplotlib
from   matplotlib.finance import candlestick2_ohlc, volume_overlay
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime as datetime
import numpy as np
from   textwrap import wrap
import pprint

# Switch matplotlib backend
matplotlib.pyplot.switch_backend('agg')

##############################################################
# Glb ds
sock = "bcbf3d08f70aaf07b860dc2f481beee5/1473605026"
res_tbl = {
              "1m"     : 1,
              "5m"     : 5,
              "15m"    : 15,
              "30m"    : 30,
              "1h"     : 60,
              "2h"     : 120,
              "4h"     : 240,
              "5h"     : 300,
              "1D"     : "D",
              "1W"     : "W",
              "1M"     : "M",
          }
intr_dy = [ "1m", "5m", "15m", "30m", "1h" ]
# 20 seconds timeout for urllib
f_timeout = 20

########################################################
# For EMAIL
def send_email(user, pwd, recipient, body='', subject="Sent from sim_stk_ind.py", attachments=[]):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = user
    msg['To']      = recipient
    msg.attach(MIMEText(TEXT, 'plain'))

    # Add all attachments 
    for a_this in attachments:
        with open(a_this,'rb') as fp:
            att = MIMEApplication(fp.read())
            att.add_header('Content-Disposition', 'attachment', filename=a_this)
            msg.attach(att)
        # endwith
    # endfor
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print "Mail sent to {} at {}".format(recipient, datetime.datetime.now())
    except:
        print "Failed to send the mail !!"
# enddef

###############################################################
# Helper functions for Investing.com access
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
    return g_burlb() + "/{}/1/1/8/symbols?".format(soc_idf)
def g_surl(soc_idf):
    return g_burlb() + "/{}/1/1/8/search?".format(soc_idf)

def strdate_to_unixdate(str_date):
    return int(time.mktime(datetime.datetime.strptime(str_date, '%d/%m/%Y').timetuple()))
# enddef

def unixdate_now():
    return int(time.mktime(datetime.datetime.now().timetuple()))
# enddef
def strdate_now():
    return datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

def scan_security_by_symbol(sym):
    this_url = g_surl(sock) + "query={}".format(sym)

    #print "{} : Fetching {}".format(strdate_now(), this_url)
    response = urllib.urlopen(this_url)
    j_data   = json.loads(response.read())
    if not bool(j_data):
        print "{} : Not able to fetch. Returned data = {}".format(strdate_now(), j_data)
        sys.exit(-1)
    else:
        return j_data[0]["description"]
    # endif
# enddef

def scan_security_by_name(name, exchg_list=['NS', 'BO', 'MCX', 'NCDEX']):
    this_url_fmt = g_surl(sock) + "query={}&exchange={}"
    j_data_f     = []

    # Iterate over all exchanges
    for exchg_this in exchg_list:
        this_url = this_url_fmt.format(name, exchg_this)
        #print "{} : Fetching {}".format(strdate_now(), this_url)
        response = urllib.urlopen(this_url)
        j_data   = json.loads(response.read())
        if not bool(j_data):
            continue
        else:
            j_data_f = j_data_f + j_data
        # endif
    # endfor
    return j_data_f
# enddef

# Process watchlist
def process_watchlist_file(wfile):
    w_list = []
    with open(os.path.expanduser(wfile), 'r') as f_in:
        for l_this in f_in:
            e_a = l_this.replace('\n', '').split(':')
            sym_name = e_a[0]
            sym_res  = e_a[1].replace(' ', '')
            try:
                ma_list =  [ int(x) for x in e_a[2].split(',') ]
            except:
                print '{} does not look like a period list seperated by commas.'.format(e_a[2].split(','))
                sys.exit(-1)
            # endtry
            try:
                num_bars = int(e_a[3])
            except:
                print '{} does not look like an integer.'.format(e_a[3].replace(' ', ''))
                sys.exit(-1)
            # endtry
            w_list.append({
                              'name'      : sym_name,
                              'res'       : sym_res,
                              'ma_l'      : ma_list,
                              'nbars'     : num_bars,
                         })
        # endfor
    # endwith
    return w_list
# enddef

def fetch_data(sym, resl, t_from=None, sym_name=None):
    # Scan for the security with symbol 'sym'. Get it's name.
    # This acts as second level check
    if sym_name == None:
        sym_name = scan_security_by_symbol(sym)
    # endif
    #print 'Security with sym_name={} found with description={}'.format(sym, sym_name)

    if t_from == None:
        t_from = strdate_to_unixdate("01/01/1992")
    # endif
    ftch_tout = 5
    t_indx    = 0

    # Assert resolution check
    assert(resl in res_tbl.keys())
    

    while t_indx < ftch_tout:
        # 1st pass
        #t_to     = unixdate_now()
        t_to     = strdate_to_unixdate("01/01/2037")
        t_now    = unixdate_now()
        this_url = g_burl(sock) + "symbol={}&resolution={}&from={}&to={}".format(sym, res_tbl[resl], t_from, t_to)

        #print "{} : Fetching {}".format(strdate_now(), this_url)
        response = urllib.urlopen(this_url)
        j_data   = json.loads(response.read())
        if not bool(j_data):
            print "{} : Not able to fetch. Returned data = {}".format(strdate_now(), j_data)
            t_indx   = t_indx + 1
            continue
        # endif

        # 2nd pass
        t_to_r   = j_data['t'][-1]
        t_lag    = t_now - t_to_r
        t_from   = j_data['t'][0] + t_lag
        this_url = g_burl(sock) + "symbol={}&resolution={}&from={}&to={}".format(sym, res_tbl[resl], t_from, t_to)

        #print "{} : Fetching {}".format(strdate_now(), this_url)
        response = urllib.urlopen(this_url)
        j_data   = json.loads(response.read())
        break
    # endwhile

    if (t_indx >= ftch_tout):
        msg_err = "{} : Retries exceeded !!".format(strdate_now())
        print msg_err
        # Alert user by sending mail
        #send_email(gm_sender, gm_passwd, gm_receiver, "Unable to fetch sym info. Killing process !!")
        # Exit
        return None, msg_err
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
    return g_pdbase(j_data), sym_name
# enddef

####################################################
# PLOTTING FUNCTIONS
#
def gen_candlestick(d_frame, mode='c', period_list=[], title='', file_name='~/tmp_plot.png', plot_period=None, plot_volume=True):
    # Vars
    l_bar          = ''.join(['-']*60)
    def_fig_dim    = plt.rcParams['figure.figsize']
    def_font_size  = plt.rcParams['font.size']

    # Check period list
    if period_list == None:
        period_list = []
    # endif

    # Make a copy
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
    def r_ns_tr(p_f, indx=-1, rnd=2):
        return str(round(p_f.iloc[indx], rnd))
    # enddef

    # Process n_bars
    def_bars       = 50
    def_n_locs     = 6
    fig_ratio      = int(plot_period * 1.0/def_bars) + 1
    new_fig_dim    = [ fig_ratio * x for x in def_fig_dim ]

    # Pre-processing
    fig = plt.figure(figsize=new_fig_dim)
    ax  = fig.add_subplot(111)
    plt.xticks(rotation = 45)
    plt.xlabel("Date")
    plt.ylabel("Price")
    #plt.title(title)

    # Title for close
    title2 = '{}:{}'.format('C', r_ns_tr(d_frame_c['c']))

    # Plot candlestick
    candlestick2_ohlc(ax, d_frame_c['o'], d_frame_c['h'], d_frame_c['l'], d_frame_c['c'], width=0.6)
    ## Plot mas
    for period_this in period_list:
        label = 'ema_' + str(period_this)
        d_s   = s_mode(d_frame_c, mode)
        d_frame_c[label] = rmean(d_s, period_this)
        d_frame_c.reset_index(inplace=True, drop=True)
        d_frame_c[label].plot(ax=ax)
        title2 = title2 + ' {}:{}'.format(label, r_ns_tr(d_frame_c[label]))
    # endfor
    if plot_volume:
        # Plot volume
        v_data = [ 0 if j == 'n/a' else j for j in d_frame_c['v'] ]
        ax2 = ax.twinx()
        bc = volume_overlay(ax2, d_frame_c['o'], d_frame_c['c'], v_data, colorup='g', alpha=0.2, width=0.6)
        ax2.add_collection(bc)
    # endif

    # Post-processing
    # Set grid
    plt.grid()

    # Set titles
    font_size = int(fig_ratio*def_font_size*0.7)
    plt.title(title + '\n{}\n'.format(l_bar) + '\n'.join(wrap(title2, 60)), fontsize=font_size)

    # Set axes
    ax.xaxis.set_major_locator(ticker.MaxNLocator(def_n_locs * fig_ratio))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    fig.autofmt_xdate()
    #fig.tight_layout()

    # Plot figure
    plt.savefig(os.path.expanduser(file_name))
    # Clear plot to save memory
    plt.close()
# enddef

# For use by external server
def gen_candlestick_wrap(sym, res='1D', mode='c', period_list=[9, 14, 21], plot_period=40, plot_dir='~/outputs/', plot_volume=True):
    if res not in res_tbl:
        return "Resolution should be one of {}".format(res_tbl.keys())
    # endif
    sym_name = scan_security_by_symbol(sym)
    j_data, sec_name = fetch_data(sym, res, sym_name=sym_name)
    if j_data is None:
        return sec_name
    # endif
    file_name = '{}/{}_{}_{}_{}.png'.format(plot_dir, sym, res, plot_period, '-'.join([str(x) for x in period_list]))
    gen_candlestick(j_data, period_list=period_list, title=sec_name, file_name=file_name, plot_period=plot_period, plot_volume=plot_volume)
    return file_name
# enddef

################################################################
# For EMA calculations
# Get mean generating f
def g_rmean_f(**kwargs):
    se_st = kwargs.get('type', 's')    # "s" or "e"
    if se_st == 's':
        return lambda s, t: pandas.rolling_mean(s, t)
    elif se_st == 'e':
        return lambda s, t: pandas.ewma(s, span=t, adjust=False)
    else:
        assert(False)
    # endif
# enddef

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

#########################################################
# Main func
if __name__ == '__main__':
    # ignore warnings
    warnings.filterwarnings("ignore")
    send_mail = False

    prsr = argparse.ArgumentParser()
    prsr.add_argument("--wfile",            help="watchlist file name (name,res,ema_l,nbars) format",
                                                                           type=str, default=None)
    prsr.add_argument("--pdir",             help="plot file",              type=str, default=None)
    args = prsr.parse_args()

    ### Symbol
    if args.__dict__["wfile"] == None:
        print '--wfile is required !!'
        sys.exit(-1)
    else:
        # Check if file exists
        if os.path.isfile(os.path.expanduser(args.__dict__["wfile"])):
            wfile = args.__dict__["wfile"]
        else:
            print '--wfile is not a file !!'
            sys.exit(-1)
        # endif
    # endif

    # get socket
    sock = g_sock()
    print "sock = {}".format(sock)

    wlist_l  = process_watchlist_file(wfile)
    pdir     = '~/candles' if not args.__dict__["pdir"] else args.__dict__["pdir"]

    # Generate a list of all securities
    sec_full_l = []
    for item_this in wlist_l:
        sec_l  = scan_security_by_name(item_this['name'])
        for i_this in sec_l:
            # Modify this node
            i_this_tmp = copy.copy(i_this)
            i_this_tmp['symbol']               = i_this_tmp['symbol'].split(':')[0]
            i_this_tmp['resolution']           = item_this['res']
            i_this_tmp['ema_period_list']      = item_this['ma_l']
            i_this_tmp['num_bars']             = item_this['nbars']
            # Add node to main dict
            sec_full_l.append(i_this_tmp)
        # endfor
    # endfor

    # Print all symbols found
    pprint.pprint('Symbols found = {}'.format([ '{} -> {}'.format(x['full_name'], x['description']) for x in sec_full_l ]))

    # Create directory if not present
    if not os.path.isdir(os.path.expanduser(pdir)):
        os.mkdir(os.path.expanduser(pdir))
    # endif

    ## Iterate over all symbols
    for i_this in sec_full_l:
        sym_desc = i_this['description'].replace(' ', '_') + '_{}_{}'.format(i_this['resolution'], i_this['num_bars'])
        pfile = pdir + '/' + sym_desc + '.png'
        print 'Plotting {} for resolution {} to {}. Using {} bars'.format(i_this['description'], i_this['resolution'], pfile, i_this['num_bars'])
        # Fetch data and generate plot file
        j_data, sec_name = fetch_data(i_this['symbol'], i_this['resolution'], sym_name=sym_desc)
        # Check for any error
        if j_data is None:
            print 'Could not fetch {}.'.format(sec_name)
            sys.exit(-1)
        # endif
        gen_candlestick(j_data, period_list=i_this['ema_period_list'], title=sec_name, file_name=pfile, plot_period=i_this['num_bars'])
    # endfor
# enddef
