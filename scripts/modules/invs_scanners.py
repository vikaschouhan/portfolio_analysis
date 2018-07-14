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
import datetime as datetime
import numpy as np
import logging
from   subprocess import call, check_call
import requests
from   bs4 import BeautifulSoup
from   modules import invs_utils

try:
    import ta # ta library for techincal analysis
except:
    print 'ta library is required for this to work !!'
    sys.exit(-1)
# endtry

####################################################
# SCANNERS
#
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
    rmean   = invs_utils.g_rmean_f(type='e')
    of_copy['v_ma'] = rmean(of_copy['v'], period_list[0])
    return of_copy
# enddef

# Strategy
def run_ema(o_frame, mode='c', period_list=[14, 21], lag=30):
    if len(period_list) != 2:
        print 'period_list should have only two elements (p0, p1). p0 is smaller time-period & p1 is larger one.'
        sys.exit(-1)
    # endif
    d_s     = invs_utils.s_mode(o_frame, mode)
    rmean   = invs_utils.g_rmean_f(type='e')

    ## Get values
    ma_p0   = rmean(d_s, period_list[0])
    ma_p1   = rmean(d_s, period_list[1])

    return c_f_1(ma_p0, ma_p1, lag=lag)
# enddef

# A ema crossover strategy for detecting crossovers on the frame passed
def run_ema2(o_frame, mode='c', lag=30, period_list=[9, 14, 21], sig_mode=None):
    d_s     = invs_utils.s_mode(o_frame, mode)
    rmean   = invs_utils.g_rmean_f(type='e')
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

# Donchian channel breakout
def run_donch_breakout(o_frame, lag=20, channel_period=20):
    o_fr_copy = o_frame.copy()
    status  = False
    trend_switch = None

    # Get donch channnel lines
    o_fr_copy['donch_high'] = ta.volaitlity.donchian_channel_hband(o_fr_copy['h'], channel_period)
    o_fr_copy['donch_low']  = ta.volaitlity.donchian_channel_lband(o_fr_copy['l'], channel_period)

    # Generate signals
    o_fr_copy['break_high'] = (o_fr_copy['c'] > o_fr_copy['donch_high'])
    o_fr_copy['break_low']  = (o_fr_copy['c'] < o_fr_copy['donch_low'])
    
    ## Get time different between last position switch and now
    #tdelta = pandas.Timestamp(datetime.datetime.now()) - o_copy.iloc[-1]['t']

    ## Last trend switch
    #if o_copy.iloc[-1]['pos'] == 1.0:
    #    trend_switch = 1
    #else:
    #    trend_switch = 0
    ## endif

    ## Check if lag > tdelta
    #if lag > tdelta.days:
    #    status = True
    ## endif

    ## Return only date/time, close price and position switches
    #return status, tdelta.days, trend_switch, o_copy[['t', 'c', 'pos']][-10:]
# enddef
