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

# Misc options
nlr         = 30
pcndl       = False
smail       = False
ptime       = 15
gpfile      = "gplot.gplot"
max_cols    = 50.0
time_d      = { "mins" : 60, "secs" : 1 }
#t_unit      = 'mins'
t_unit      = 'secs'
ema_mode    = 'c'
macd_mode   = 'c'

# pandas display options
pandas.set_option('display.max_rows',    999)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.height',      500)
pandas.set_option('display.width',       500)

# User info
# NOTE:
#       EMAIL is the email address of the sender
#       EMAIL_PWD is the password for the above
gm_sender   = ""
gm_receiver = ""
gm_passwd   = ""

# Glb ds
sock = "bcbf3d08f70aaf07b860dc2f481beee5/1473605026"
sym_tbl = {
              "nifc1"          : 101817,
              "ind50"          : 8985,
              "nsei"           : 17940,
              "sinq6"          : 101810,
              "dji"            : 169,
              "indvix"         : 17942,
              "nifmdcp100"     : 17946,
          }
res_tbl = {
              "1m"     : 1,
              "5m"     : 5,
              "15m"    : 15,
              "30m"    : 30,
              "1h"     : 60,
              #"2h"     : 120,
              #"4h"     : 240,
              #"5h"     : 300,
              "1D"     : "D",
              "1W"     : "W",
              "1M"     : "M",
          }
intr_dy = [ "1m", "5m", "15m", "30m", "1h" ]

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

def init_credentials():
    if "EMAIL" not in os.environ:
        print "export EMAIL=youremail@host"
        sys.exit(-1)
    # endif
    if "EMAIL_PWD" not in os.environ:
        print "export EMAIL_PWD=youremailpassword"
        sys.exit(-1)
    # endif
    global gm_sender, gm_receiver, gm_passwd
    gm_sender   = os.environ["EMAIL"]
    gm_receiver = gm_sender
    gm_passwd   = os.environ["EMAIL_PWD"]
# enddef

def send_email(user, pwd, recipient, body, subject="Sent from sim_stk_ind.py"):
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
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print "Mail sent to {}".format(recipient)
    except:
        print "Failed to send the mail !!"
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

def fetch_data(sym, resl, t_from=None):
    if t_from == None:
        t_from = strdate_to_unixdate("01/01/1992")
    # endif
    ftch_tout = 5
    t_indx    = 0

    assert(sym in sym_tbl.keys())
    assert(resl in res_tbl.keys())

    while t_indx < ftch_tout:
        t_to     = unixdate_now()
        this_url = g_burl(sock) + "symbol={}&resolution={}&from={}&to={}".format(sym_tbl[sym], res_tbl[resl], t_from, t_to)

        print "{} : Fetching {}".format(strdate_now(), this_url)
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
        print "{} : Retries exceeded !!".format(strdate_now())
        # Alert user by sending mail
        send_email(gm_sender, gm_passwd, gm_receiver, "Unable to fetch sym info. Killing process !!")
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

    print "{} : Fetched data. done !!".format(strdate_now())
    return g_pdbase(j_data)
# enddef

def minmax_pdbase(pdbase):
    c_list = list(pdbase['l']) + list(pdbase['o']) + list(pdbase['c']) + list(pdbase['h'])
    return (min(c_list), max(c_list))
# enddef

# generate cnflestk (scaled) on console
def gen_cndlstk(pdbase, l_len=50):
    len_data   = len(pdbase['c'])
    s_indx     = (0 if (l_len == None or l_len == -1) else (len_data - l_len))
    (mi, ma)   = minmax_pdbase(pdbase[s_indx:])
    mrng       = (ma - mi)
    #max_cols   = 100.0
    bu_pttrn   = '|'
    br_pttrn   = '*'
    tl_pttrn   = '-'
    
    f_fact     = max_cols/mrng
    one_by_f   = mrng/max_cols
    
    m_strm     = ''
    assert(len_data - l_len >= 0)

    def y2x(y):
        return int((y - mi) * f_fact)
    # enddef

    for r_this in range(s_indx, len_data):
        lo     = y2x(pdbase['l'][r_this])
        hi     = y2x(pdbase['h'][r_this])
        op     = y2x(pdbase['o'][r_this])
        cl     = y2x(pdbase['c'][r_this])
        strm   = [ str(pdbase['t'][r_this]), ' : ' ]
        strm   = strm + [' ']*lo
        pttrn  = (bu_pttrn if ((cl - op) > 0) else br_pttrn)
        l_bnd  = (op if (cl - op > 0) else cl)
        h_bnd  = (cl if (cl - op > 0) else op)
        abs_d  = ((h_bnd - l_bnd) if ((h_bnd - l_bnd) > 0) else 1)
        strm   = ((strm + [tl_pttrn]*(l_bnd - lo)) if ((l_bnd - lo) > 0) else strm)
        strm   = strm + [pttrn]*abs_d
        strm   = ((strm + [tl_pttrn]*(hi - h_bnd)) if ((hi - h_bnd) > 0) else strm)
        m_strm = m_strm + ''.join(strm) + '\n'
    # endfor
    m_strm = m_strm + 'div = {}\n'.format(one_by_f)
    return m_strm
# enddef

# Generate gnuplot data
def gen_gplot_file(x_l, **kwargs):
    x_len   = len(x_l)
    y_lb_l  = []
    y_vl_l  = []

    for key, value in kwargs.iteritems():
        y_lb_l.append(str(key))
        y_vl_l.append(value)
    # endfor

    strm = ''
    pc_l = []
    for i_c in range(0, len(y_vl_l)):
        pc_l.append("'-' using 1:2 title 'Plot_{}' with lines".format(y_lb_l[i_c]))
        for r_t in range(0, x_len):
            strm = strm + "{}    {}\n".format(x_l[r_t], y_vl_l[i_c][r_t])
        # endfor
        strm = strm + "\ne\n"
    # endfor

    with open(gpfile, "w") as f_o:
        f_o.write("set key outside\n")
        if os.name == "posix":
            f_o.write("set term x11 1 noraise\n")
        # endif
        f_o.write("set grid\n")
        f_o.write("set datafile missing 'nan'\n")
        f_o.write("plot {}\n".format(','.join(pc_l)))
        f_o.write(strm)
        f_o.write("pause 30\n")
        f_o.write("reread\n")
    # endwith
# enddef

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

def run_ema(o_frame, mode='c'):
    d_s     = s_mode(o_frame, mode)
    rmean   = g_rmean_f(type='e')
    d_frame = pandas.DataFrame(index=o_frame.index)
    # Insert elements
    d_frame['ds']    = rmean(d_s, 8) - rmean(d_s, 20)
    d_frame['dss']   = [-1 if x >=0 else 1 for x in d_frame['ds']]
    d_frame['dsss']  = d_frame['dss'].diff()

    return d_frame
# enddef

# MACD
def run_macd(o_frame, mode='c'):
    # New dframe
    d_frame  = pandas.DataFrame(index=o_frame.index)
    x_alt_a  = d_frame.index
    # Init elements
    #d_frame['c'] = o_frame['c']
    #d_frame['t'] = o_frame['t']
    #d_frame['v'] = o_frame['v']
    # Funcs
    rmean    = g_rmean_f(type='e')
    th_now   = datetime.datetime.now().hour
    # New elements
    d_data   = s_mode(o_frame, mode)
    ewma_l   = rmean(d_data, 9)
    ewma_h   = rmean(d_data, 14)
    ewma_m   = ewma_l - ewma_h
    ewma_s   = rmean(ewma_m, 3)
    ewma_m_d = ewma_m.diff()
    ewma_s_d = ewma_s.diff()
    ewma_m_s = ewma_m - ewma_s

    ewma_m_d_r = rmean(ewma_m_d, 3)
    ewma_s_d_r = rmean(ewma_s_d, 3)
    ewma_m_s_r = rmean(ewma_m_s, 3)

    #d_frame['m_diff']   = pandas.rolling_mean(ewma_m_d, 4)
    d_frame['s']        = ewma_s
    d_frame['s_diff']   = ewma_s_d
    d_frame['s_ddiff']  = ewma_s_d.diff()
    d_frame['m-s']      = ewma_m_s
    d_frame['momentm']  = ewma_l.diff()
    d_frame['B_s_d']    = [ '+' if x > 0 else '-' for x in ewma_s_d ]
    d_frame['B_m-s']    = [ '+' if x > 0 else '-' for x in ewma_m_s ]
    d_frame['B_m-s_e']  = [ 'e' if math.fabs(x) < 0.5 else '-' for x in ewma_m_s ]
    d_frame['B_m-s_E']  = [ 'E' if math.fabs(x) < 1.5 else '-' for x in ewma_m_s ]
    d_frame['C_MA']     = [ '+' if x > 10.0 else '-' if x < -10.0 else 'p' if x >= 0.0 else 'n' for x in (d_data - ewma_h) ]

    # Gen conds for switch
    switch_cond  = ((d_frame['B_s_d'].iloc[-1] != d_frame['B_s_d'].iloc[-2]) or \
                   (d_frame['B_m-s'].iloc[-1] != d_frame['B_m-s'].iloc[-2])  or \
                   (d_frame['B_m-s_e'].iloc[-1] == 'e'))
    
    # Gen plot files
    gen_gplot_file(x_alt_a, m=ewma_m, s=ewma_s)
  
    # Only send if time is between 8AM and 4PM 
    if th_now >= 8 and th_now <= 16:
        # Email me the string (only when the indicator changes sign)
        if smail and switch_cond:
            send_email(gm_sender, gm_passwd, gm_receiver,
                dtrm, "Sent from sim_stk_ind.py at {}".format(strdate_now()))
            #print d_frame[-25:].to_string(col_space=10)
        # endif
    else:
        print "Not sending mail as market is closed !!"
    # endif

    return d_frame
# enddef

def str_dbase(d_frame, nlr_):
    strm = ''
    strm = strm + "************************************************************\n"
    strm = strm + "sample len = {}\n".format(len(d_frame.index))
    strm = strm + "************************************************************\n"
    strm = strm + str(d_frame[-nlr_:]) + '\n'
    strm = strm + "************************************************************\n"

    return strm
# enddef

def str_cndlstk(d_frame, nlr_):
    dtrm = ''
    dtrm = dtrm + "cndlstk chart\n"
    dtrm = dtrm + gen_cndlstk(d_frame, nlr_) + '\n'
    dtrm = dtrm + "************************************************************\n"

    return dtrm
# enddef

# time sig
def time_sig_loop(res, sym, p_data):
   #assert(res in intr_dy)
   #min_gp = res_tbl[res]
   pau_tm = ptime
   pau_ts = pau_tm * time_d[t_unit]
   while True:
       #tm_now = datetime.datetime.now().minute
       #if tm_now % pau_tm:
       print "{} : Sleeping for {} {}.".format(strdate_now(), pau_tm, t_unit)
       time.sleep(pau_ts)
       # endif
       j_ndata = fetch_data(sym, res)
       l_cp    = float(j_ndata['c'].iloc[-1])
       l_ct    = int(j_ndata['T'].iloc[-1])
       p_cp    = float(p_data['c'].iloc[-1])
       p_ct    = int(p_data['T'].iloc[-1])
       ## Data changed !!
       #d_chngd = (l_ct >= p_ct) and not chk_rng2(p_cp, l_cp, 20)
       d_chngd = (l_ct >= p_ct)
       if d_chngd:
           return j_ndata
       # endif
       p_data  = j_ndata
   # endwhile
   assert(False)
# enddef


def i_cndlestk(c_open, c_close, c_low, c_high):
    pass
# endif

# Main func
if __name__ == '__main__':
    # Initialize Credentials
    init_credentials()

    prsr = argparse.ArgumentParser()
    prsr.add_argument("--loop",    help="Loop mode",            action='store_true')
    prsr.add_argument("--sym",     help="symbol",               type=str)
    prsr.add_argument("--nlr",     help="n last rows",          type=int)
    prsr.add_argument("--cndl",    help="Print candles",        action='store_true')
    prsr.add_argument("--res",     help="resolution",           type=str)
    prsr.add_argument("--smail",   help="send mail",            action='store_true')
    prsr.add_argument("--stime",   help="sleep time",           type=int)
    prsr.add_argument("--tunit",   help="time unit",            type=str)
    prsr.add_argument("--gfile",   help="gnu plot file",        type=str)
    prsr.add_argument("--mcols",   help="max cols (cndlstk)",   type=int)
    args = prsr.parse_args()

    # Symbl, resol
    sym = "nifc1"
    res = "1h"

    if args.__dict__["sym"]:
        sym  = args.__dict__["sym"]
    # endif
    if args.__dict__["nlr"]:
        nlr  = args.__dict__["nlr"]
    # endif
    if args.__dict__["cndl"]:
        pcndl = args.__dict__["cndl"]
    # endif
    if args.__dict__["res"]:
        assert(args.__dict__["res"] in res_tbl.keys())
        res  = args.__dict__["res"]
    # endif
    if args.__dict__["smail"]:
        smail = args.__dict__["smail"]
    # endif
    if args.__dict__["stime"]:
        ptime = args.__dict__["stime"]
    # endif
    if args.__dict__["tunit"]:
        if args.__dict__["tunit"] not in time_d.keys():
            print "--tunit should be {}".format(time_d.keys())
            sys.exit(-1)
        # endif
        t_unit = args.__dict__["tunit"]
    # endif
    if args.__dict__["gfile"]:
        gpfile = args.__dict__["gfile"]
    # endif
    if args.__dict__["mcols"]:
        max_cols = args.__dict__["mcols"]
    # endif

    # ignore warnings
    warnings.filterwarnings("ignore")

    # get socket
    sock = g_sock()
    print "sock = {}".format(sock)

    # RUN macd
    j_data = fetch_data(sym, res)
    while True:
        # Calculate ratios
        macd_data = run_macd(j_data, macd_mode)
        ema_data  = run_ema(j_data, ema_mode)
        # Extra
        prc_data       = pandas.DataFrame(index=j_data.index)
        prc_data['c']  = j_data['c']
        prc_data['v']  = j_data['v']
        prc_data['t']  = j_data['t']
        # Concatenate them
        m_data    = macd_data.join(ema_data).join(prc_data)
        # Display table
        print str_dbase(m_data, nlr)
        if pcndl:
            # Display cndlstk
            print str_cndlstk(j_data, nlr)
        # endif
        # Check for loop cond.
        if not args.__dict__["loop"]:
            sys.exit(0)
        # endif
        j_data = time_sig_loop(res, sym, j_data)
    # endwhile
# enddef
