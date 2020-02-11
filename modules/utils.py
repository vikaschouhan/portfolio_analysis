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
import os
import url_normalize
import uuid
from   PIL import Image
import glob
import os
import pandas as pd
import multiprocessing
import itertools
import xlsxwriter

def islist(x):
    return isinstance(x, list)
# enddef
def istuple(x):
    return isinstance(x, tuple)
# enddef
def isdict(x):
    return isinstance(x, dict)
# enddef
def isstring(x):
    return isinstance(x, str)
# enddef

###########################################################################################
# File system handling

def mkdir(dir):
    if dir == None:
        return None
    # endif
    if not os.path.isdir(dir):
        os.makedirs(dir, exist_ok=True)
    # endif
# enddef

def rp(dir):
    if dir == None:
        return None
    # endif
    if dir[0] == '.':
        return os.path.normpath(os.getcwd() + '/' + dir)
    else:
        return os.path.normpath(os.path.expanduser(dir))
# enddef

def filename(x, only_name=True):
    n_tok = os.path.splitext(os.path.basename(x))
    return n_tok[0] if only_name else n_tok
# enddef

def chkdir(dir):
    if not os.path.isdir(dir):
        print('{} does not exist !!'.format(dir))
        sys.exit(-1)
    # endif
# enddef

def chkfile(file_path, exit=False):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return True
    # endif
    if exit:
        print('{} does not exist !!'.format(file_path))
        sys.exit(-1)
    # endif
        
    return False
# enddef

def npath(path):
    return os.path.normpath(path) if path else None
# enddef


############################################################################################

# Get mean generating f
def g_rmean_f(**kwargs):
    se_st = kwargs.get('type', 's')    # "s" or "e"
    if se_st == 's':
        return lambda s, t: pd.rolling_mean(s, t)
    elif se_st == 'e':
        return lambda s, t: pd.Series.ewm(s, span=t, adjust=False).mean()
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

################################################
# Pandas functions
# Get data at index in pandas frame
def dindx(data_frame, key, index):
    return data_frame.iloc[index][key]
# enddef

def dropna(data_frame, how='all'):
    return data_frame.dropna(axis=0, how=how).dropna(axis=1, how=how)
# enddef

def dropzero(data_frame, columns=['c', 'o', 'h', 'l']):
    col_logic = True
    for col_t in columns:
        col_logic = col_logic & (data_frame[col_t] == 0.0)
    # endfor
    return data_frame.drop(data_frame[col_logic].index)
# enddef

# Write dictionary of dataframes to one single excel workbook
def df_to_excel(dfs, filename):
    assert isdict(dfs), 'Input (dfs) should be a dictionary of sheets !!'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            worksheet.set_column(idx+1, idx+1, max_len)  # set column width
        # endfor
        # Fix index
        worksheet.set_column(0, 0, max((df.index.astype(str).map(len).max(), len(str(df.index.name)))))
    # endfor
    writer.save()
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

def incr_days(dt, days=1, op='+'):
    assert isinstance(dt, datetime.datetime), 'dt={} should be an instance of datetime.datetime'.format(dt)
    assert op in ['+', '-'], 'op={} should be either + or -'.format(op)
    if op == '+':
        return dt + datetime.timedelta(days=days)
    elif op == '-':
        return dt - datetime.timedelta(days=days)
    # endif
# enddef

def incr_days_str(dt, dt_fmt='%Y-%m-%d', days=1, op='+'):
    assert isinstance(dt, str), 'dt={} should be a string.'.format(dt)
    dt = datetime.datetime.strptime(dt, dt_fmt)
    dt_new = incr_day(dt, days=days, op=op)
    return dt_new.strftime(dt_fmt)
# enddef

def split_date_range_into_chunks(date_range, date_fmt=None, range_days=300, order='dec'):
    assert order in ['inc', 'dec'], 'order={} should be one of ["inc", "dec"]'.format(order)
    assert (islist(date_range) or istuple(date_range)) and len(date_range) == 2, \
            'date_range={} should be a list or tuple of 2 elements.'.format(date_range)
    if date_fmt is None:
        assert [isinstance(x, datetime.datetime) for x in date_range]
    else:
        date_range = [datetime.datetime.strptime(x, date_fmt) for x in date_range]
    # endif

    to_date     = max(date_range)
    from_date   = min(date_range)
    to_date_t   = to_date

    days_list   = []
    while True:
        from_date_t = incr_days(to_date_t, days=range_days, op='-')
        days_list.append((from_date_t, to_date_t))
        to_date_t   = incr_days(from_date_t, days=1, op='-')
        if to_date_t < from_date:
            break
        # endif
    # endwhile

    # Sort the order if in increasing order
    if order == 'inc':
        days_list   = list(reversed(days_list))
    # endif
    # Convert to string format if applicable
    if date_fmt:
        days_list = [(x[0].strftime(date_fmt), x[1].strftime(date_fmt)) for x in days_list]
    # endif

    return days_list
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

#################################################################
# Utils
def merge_images(file_list, out_file):
    im_size_list = []

    for f_this in file_list:
        im_size_list.append(Image.open(f_this).size)
    # endfor

    result_width  = max([x[0] for x in im_size_list])
    result_height = sum([x[1] for x in im_size_list])
    h_ptr_t = 0
    result  = Image.new('RGB', (result_width, result_height))

    # Iterate
    for f_this in file_list:
        im_this = Image.open(f_this)
        result.paste(im=im_this, box=(0, h_ptr_t))
        h_ptr_t = h_ptr_t + im_this.size[1]
    # endfor

    result.save(os.path.expanduser(out_file))
# enddef

def rev_map(x):
    return {v:k for k,v in x.items()}
# enddef

def search_for(dir_t, file_ext_list=None, full_path=False):
    file_ext_list = ['*'] if file_ext_list is None else \
            [file_ext_list] if not isinstance(file_ext_list, list) else file_ext_list
    file_list = []
    for ext_t in file_ext_list:
        file_l_t  = glob.glob1(dir_t, ext_t)
        # Add dir_t if full_path is required
        if full_path:
            file_l_t = ['{}/{}'.format(dir_t, x) for x in file_l_t]
        # endif
        file_list = file_list + file_l_t
    # endfor
    return file_list
# enddef

############################################################################
# Reading csvs of asset prices
col_map    = {'Open':'o', 'High':'h', 'Low':'l', 'Close':'c', 'Volume':'v'}
col_close  = 'Close'

def read_asset_csv(csv_file, columns_map=None, resample_period=None):
    # Reverse
    columns_map = rev_map(columns_map)
    # Read
    df = pd.read_csv(csv_file, index_col=0, infer_datetime_format=True, parse_dates=True)
    df = df.rename(columns=columns_map) if columns_map else df
    df = df.resample(resample_period).mean().dropna() if resample_period else df
    return df
# enddef

def read_asset_csvs(files_list, resample_period=None):
    # read all dataframes
    df_map     = {}
    for indx_t, file_t in enumerate(files_list):
        print('Loading file {:<4}/{:<4}..'.format(indx_t, len(files_list)), end='\r')
        df_t   = read_asset_csv(file_t, columns_map=col_map, resample_period=resample_period)
        df_map[os.path.basename(file_t)] = df_t
    # endfor

    return df_map
# enddef

def read_all_asset_csvs(csv_dir, column_map=col_map, resample_period=None):
    files_list = search_for(csv_dir, file_ext_list=['*.csv'], full_path=True)
    df_map     = spawn_workers(read_asset_csvs, 4,
                 **{ 'proc_id_key' : None,
                     'data_keys'   : ['files_list'],
                     'files_list'  : files_list,
                     'resample_period' : resample_period
                   })
    return df_map
# enddef

def resample_asset_data(dmap, resample_period=None):
    if resample_period is None:
        return None
    # endif

    dmap_t = {}
    for key_t in dmap.keys():
        dmap_t[key_t] = dmap[key_t].resample(resample_period).mean().dropna()
    # endfor
    return dmap_t
# enddef

def filter_asset_csvs(df_map, filter_col=col_close):
    # Read all close prices only
    df_close_list = []
    for file_t in df_map:
        df_close_list.append(df_map[file_t][filter_col].rename(file_t))
    # endfor
    com_df     = pd.concat(df_close_list, axis=1)
    return com_df
# enddef


###################################################
# @Decorators

def static(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    # enddef
    return decorate
# enddef

####################################################
# Multiprocessing helpers
# Create single manager
mp_manager = multiprocessing.Manager()

def split_chunks(l, n_chunks):
    n = int(len(l)/n_chunks)
    retv = [l[i*n:(i+1)*n] for i in range(int(len(l)/n)+1) if l[i*n:(i+1)*n] != []]
    return retv[0:n_chunks-1] + [list(itertools.chain(*retv[n_chunks-1:]))]
# enddef

def spawn_workers(worker_fn, num_threads, sanitize_results=True, **kwargs):
    if 'data_keys' not in kwargs:
        print('**kwargs in spawn_workers need to have named key "data_keys"')
        sys.exit(-1)
    # endif

    # Get list of named parameters which need to be divided
    data_keys = kwargs.pop('data_keys')
    if not isinstance(data_keys, list):
        print('kwargs["data_keys"] should be a list of keys which need to be divided across processes.')
        sys.exit(-1)
    # endif

    # Check if proc_id is to specified for the worker
    if 'proc_id_key' in kwargs:
        proc_id_key = kwargs.pop('proc_id_key')
    else:
        proc_id_key = None
    # endif

    # Divide payloads
    chunk_map   = {}
    count_map   = {}
    for data_key_t in data_keys:
        if data_key_t not in kwargs:
            print('FATAL::: {} not found in kwargs for spawn_workers.'.format(data_key_t))
        # endif
        # Check if keys are list or not
        if not isinstance(kwargs[data_key_t], list):
            print(kwargs[data_key_t], ' is not a list.')
            sys.exit(-1)
        # endif
        data_value_t = kwargs.pop(data_key_t)
        count_map[data_key_t] = len(data_value_t)  # Get length of this list
        chunk_map[data_key_t] = split_chunks(data_value_t, num_threads)
    # endfor

    if len(set(list(count_map.values()))) != 1:
        print('data_keys in spawn_workers have mismatch in length of parameters : {}'.format(count_map))
        sys.exit(-1)
    # endif

    # Define a new worker fn which wraps original worker fn with some customizations
    def __wrap_worker_fn(return_dict, proc_id, **xkwargs):
        ret_result = worker_fn(**xkwargs)
        return_dict[proc_id] = ret_result
    # enddef

    print('INFO::: Dividing {} jobs across {} threads.'.format(list(count_map.values())[0], num_threads))

    # Deploy
    result_list  = []
    process_list = []
    return_dict  = mp_manager.dict()
    for i in range(num_threads):
        # Populate kwargs
        for data_key_t in chunk_map:
            kwargs[data_key_t] = chunk_map[data_key_t][i]
        # endfor
        if proc_id_key:
            kwargs[proc_id_key] = i
        # endif
        # Spawn new process
        proc = multiprocessing.Process(target=__wrap_worker_fn, args=(return_dict,i,), kwargs=kwargs)
        process_list.append(proc)
        proc.start()
    # endfor

    # Wait for all processes to end
    for proc_t in process_list:
        proc_t.join()
    # endfor

    print('INFO:: All processes finished !!')

    # Collate all results
    all_results = []
    for i in range(num_threads):
        chunk_result = return_dict[i]
        all_results.append(chunk_result)
    # endfor

    # Sanitize all_results
    if sanitize_results:
        if isinstance(all_results[0], list):
            all_results = [x for z in all_results for x in z]
        elif isinstance(all_results[0], dict):
            all_results = {x:y for z in all_results for (x,y) in z.items()}
        # endif
    # endif

    return all_results
# enddef
