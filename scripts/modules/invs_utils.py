# Author : Vikas Chouhan (presentisgood@gmail.com)
#
import math
import csv
import locale
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
import url_normalize
import uuid

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
        print("mode should be one of {}".format(m_list))
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

def parse_csv_file(csv_file, encoding='iso-8859-1'):
    encoding   = locale.getpreferredencoding() if encoding == None else encoding
    csv_reader = csv.reader(open(csv_file, 'r', encoding=encoding))
    row_list   = [ x for x in csv_reader ]
    return row_list
# enddef

def parse_sarg(x, cast_to=str, arg_mod_fn=None, delimiter=','):
    if x:
        if arg_mod_fn:
            return [arg_mod_fn(cast_to(y.rstrip().lstrip())) for y in x.split(',')]
        else:
            return [cast_to(y.rstrip().lstrip()) for y in x.split(delimiter)]
        # endif
    # endif
    return None
# enddef

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
        return float(x)
    except:
        return x
    # endtry
# enddef

def cint(x):
    try:
        return int(x)
    except:
        return x
    # endtry
# enddef

def vprint(msg, verbose=True):
    if verbose:
        print(msg)
    # endif
# enddef

def cdir(d_path):
    d_path = rp(d_path)
    if not os.path.isdir(d_path):
        os.mkdir(d_path)
    # endif
    return d_path
# enddef

def precision(x, n=2):
    return int(x * 10.0**n)/(10.0**n)
# enddef

def get_colorama_color_fore(color):
    color_map = {
            'red'          : Fore.RED,
            'blue'         : Fore.BLUE,
            'black'        : Fore.BLACK,
            'green'        : Fore.GREEN,
            'magenta'      : Fore.MAGENTA,
            'yellow'       : Fore.YELLOW,
            'cyan'         : Fore.CYAN,
            'white'        : Fore.WHITE,
            'lightblack'   : Fore.LIGHTBLACK_EX,
            'lightblue'    : Fore.LIGHTBLUE_EX,
            'lightcyan'    : Fore.LIGHTCYAN_EX,
            'lightgreen'   : Fore.LIGHTGREEN_EX,
            'lightmagenta' : Fore.LIGHTMAGENTA_EX,
            'lightred'     : Fore.LIGHTRED_EX,
            'lightwhite'   : Fore.LIGHTWHITE_EX,
            'lightyellow'  : Fore.LIGHTYELLOW_EX,
        }
    assert color in color_map
    return color_map[color]
# enddef

def get_colorama_color_back(color):
    color_map = {
            'red'          : Back.RED,
            'blue'         : Back.BLUE,
            'black'        : Back.BLACK,
            'green'        : Back.GREEN,
            'magenta'      : Back.MAGENTA,
            'yellow'       : Back.YELLOW,
            'cyan'         : Back.CYAN,
            'white'        : Back.WHITE,
            'lightblack'   : Back.LIGHTBLACK_EX,
            'lightblue'    : Back.LIGHTBLUE_EX,
            'lightcyan'    : Back.LIGHTCYAN_EX,
            'lightgreen'   : Back.LIGHTGREEN_EX,
            'lightmagenta' : Back.LIGHTMAGENTA_EX,
            'lightred'     : Back.LIGHTRED_EX,
            'lightwhite'   : Back.LIGHTWHITE_EX,
            'lightyellow'  : Back.LIGHTYELLOW_EX,
        }
    assert color in color_map
    return color_map[color]
# enddef

def coloritf(message, color):
    return get_colorama_color_fore(color) + message + Fore.RESET
# enddef

def coloritb(message, color):
    return get_colorama_color_back(color) + message + Back.RESET
# enddef

def url_norm(url):
    return url_normalize.url_normalize(url.rstrip('/'))
# enddef

###############################################################
def download_kite_instruments():
    api_url = 'https://api.kite.trade/instruments'
    resp    = requests.get(api_url)
    if resp.status_code != 200:
        print('ERROR:: Encountered error while downloading kite instruments file from {}'.format(api_url))
        return None
    # endif

    out_file = '/tmp/' + str(uuid.uuid4()) + '.csv'
    print('Downloading kite instruments file to {}'.format(out_file))
    with open(out_file, 'w') as f_out:
        f_out.write(resp.text)
    # endwith

    return out_file
# enddef
