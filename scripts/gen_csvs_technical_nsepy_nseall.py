#!/usr/bin/env python3
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# csv generator

import os
import argparse
import sys
import shutil
import csv
import nsepy
import datetime
import time
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

def download_data(stock_symbol, start_date=datetime.datetime(1992, 1, 1), timeout=10):
    curr_timeout = 1
    sleep_time = 0
    while curr_timeout < timeout:
        try:
            if sleep_time:
                print(f'Sleeping for {sleep_time}s')
                time.sleep(sleep_time)
            # endif
            dframe = nsepy.get_history(stock_symbol, start_date, datetime.datetime.now())
            print(f'start_date={start_date}')
            print(dframe)
            break
        except AttributeError:
            curr_timeout += 1
            sleep_time = sleep_time * 2 if sleep_time else 1
    if curr_timeout == timeout:
        print(f'Timeout expired for {stock_symbol} !!')
        print(f'Stopping script. Please manually start again.')
        sys.exit(-1)
    else:
        return dframe
# enddef

def check_and_download_csv(stock_symbol, out_dir):
    # Check if file exists
    out_file = f'{out_dir}/{stock_symbol}.csv'
    dframe = None
    if os.path.isfile(out_file):
        dframe = pd.read_csv(out_file, index_col=0)
    # endif

    # Check last date
    if dframe is not None:
        last_date = pd.to_datetime(dframe.index[-1]).to_pydatetime()
        print(f'last_date={last_date}', flush=True)
        print(f'stock_symbol={stock_symbol}', flush=True)
        if last_date != datetime.datetime.now():
            next_df = download_data(stock_symbol, last_date)
            dframe = pd.concat([dframe, next_df], axis=0).drop_duplicates()
        # endif
    else:
        dframe = download_data(stock_symbol)
    # endif

    # Save data
    dframe.to_csv(out_file)
# enddef

def download_all_data(out_dir):
    stock_list = ['SBIN'] #nsepy.constants.symbol_list
    for index_t, stock_t in enumerate(stock_list):
        print(f'{index_t}. Downloading {stock_t}....', end='\r')
        check_and_download_csv(stock_t, out_dir)
    # endfor
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--cache_dir',    help='Directory for caching stock specific files', type=str, default='~/.cache/nsepy_cache')
    parser.add_argument('--out_file',     help='Final output file for Amibroker import', type=str, default='~/nsepy_amibroker_import.csv')
    args    = parser.parse_args()

    cache_dir = os.path.expanduser(args.__dict__['cache_dir'])
    out_file  = os.path.expanduser(args.__dict__['out_file'])

    os.makedirs(cache_dir, exist_ok=True)
    download_all_data(cache_dir)
# endif
