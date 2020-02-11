#!/usr/bin/env python3
import numpy as np
import sys, os
import argparse
import glob
import pandas as pd

if __name__ == '__main__':
    prsr = argparse.ArgumentParser()
    prsr.add_argument("--in_dir",    help="Input csv dir",      type=str, default=None)
    prsr.add_argument("--out_csv",   help="Output csv file",    type=str, default=None)
    args = prsr.parse_args()

    if args.__dict__['in_dir'] == None or args.__dict__['out_csv'] == None:
        print('All arguments are required. Please check --help.')
        sys.exit(-1)
    # endif

    in_dir   = args.__dict__['in_dir']
    out_csv  = args.__dict__['out_csv']

    # Check dir
    if not os.path.isdir(in_dir):
        print('{} doesnot exist.'.format(in_dir))
        sysexit(-1)
    # endif
    # Get list of all files in in_dir
    csv_list = glob.glob1(in_dir, '*.csv')
    if len(csv_list) == 0:
        print('{} is empty'.format(in_dir))
        sys.exit(-1)
    # endif

    np_date  = np.empty(0)
    np_close = np.empty(0)
    np_open  = np.empty(0)
    np_high  = np.empty(0)
    np_low   = np.empty(0)
    np_vol   = np.empty(0)
    np_tick  = []
    for csv_file_t in csv_list:
        print('Analysing {}..............................................'.format(csv_file_t), end='\r')
        in_file_path    = '{}/{}'.format(in_dir, csv_file_t)
        dframe_t        = pd.read_csv(in_file_path, index_col=0)
        np_date         = np.append(np_date, dframe_t.index)
        np_close        = np.append(np_close, dframe_t['c'].values)
        np_open         = np.append(np_open, dframe_t['o'].values)
        np_high         = np.append(np_high, dframe_t['h'].values)
        np_low          = np.append(np_low, dframe_t['l'].values)
        np_vol          = np.append(np_vol, dframe_t['v'].values)
        np_tick         = np_tick + [os.path.splitext(os.path.basename(csv_file_t))[0]] * len(dframe_t.index)
    # endfor

    # Create a new dataframe
    dframe_new = pd.DataFrame()
    dframe_new['Ticker'] = np_tick
    dframe_new['Date']   = np_date
    dframe_new['Open']   = np_open
    dframe_new['High']   = np_high
    dframe_new['Low']    = np_low
    dframe_new['Close']  = np_close
    dframe_new['Volume'] = np_vol

    # Save
    dframe_new.set_index('Ticker', inplace=True)
    dframe_new.to_csv(out_csv)
# enddef
