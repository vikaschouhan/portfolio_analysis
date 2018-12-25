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
import pandas
import os

###########################################################################################
# File system handling

# Resolve path
def rp(x):
    return os.path.expanduser(x)
# enddef


############################################################################################

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

def d_ema(f_frame, ema_period, mode='c'):
    d_fr   = s_mode(f_frame, mode)
    ema_fn = g_rmean_f(type='e')
    return ema_fn(d_fr, ema_period)
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


def get_arg(args_dict, key, default_value):
    if key not in args_dict:
        print('{} not found in {}. Picking default value of {}'.format(key, args_dict, default_value))
        return default_value
    else:
        print('Using {} for {}'.format(args_dict[key], key))
        return args_dict[key]
    # endif
# enddef

def parse_opt_args(arg_string):
    opt_args = {}
    if arg_string:
        opt_list = arg_string.split(',')
        for item_t in opt_list:
            item_l = item_t.split('=')
            if len(item_l) != 2:
                print('Wrong args format on {}.'.format(arg_string))
                sys.exit(-1)
            # endif
            try:
                opt_args[item_l[0]] = int(item_l[1])         # try cast to integer
            except:
                try:
                    opt_args[item_l[0]] = float(item_l[1])   # try cast to float
                except:
                    opt_args[item_l[0]] = item_l[1]          # accept as string
                # endtry
            # endtry
        # endfor
    # endif
    return opt_args
# enddef

# Get data at index in pandas frame
def dindx(data_frame, key, index):
    return data_frame.iloc[index][key]
# enddef

def dropzero(data_frame, columns=['c', 'o', 'h', 'l']):
    col_logic = True
    for col_t in columns:
        col_logic = col_logic & (data_frame[col_t] == 0.0)
    # endfor
    return data_frame.drop(data_frame[col_logic].index)
# enddef

# Cast to float
def cfloat(x):
    try:
        return float(int(x))
    except:
        return x
    # endtry
# enddef
