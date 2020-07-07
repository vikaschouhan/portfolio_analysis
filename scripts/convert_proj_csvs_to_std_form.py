#!/usr/bin/env python3
import numpy as np
import sys, os
import argparse
import glob
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *

if __name__ == '__main__':
    prsr = argparse.ArgumentParser()
    prsr.add_argument("--in_dir",    help="Input csv dir",      type=str, default=None)
    prsr.add_argument("--out_dir",   help="Output csv dir",    type=str, default=None)
    args = prsr.parse_args()

    if args.__dict__['in_dir'] == None or args.__dict__['out_dir'] == None:
        print('All arguments are required. Please check --help.')
        sys.exit(-1)
    # endif

    in_dir   = rp(args.__dict__['in_dir'])
    out_dir  = rp(args.__dict__['out_dir'])

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

    # Create output dir
    mkdir(out_dir)
    col_map = {'c': 'Close', 'o': 'Open', 'h': 'High', 'l': 'Low', 'v': 'Volume'}

    for csv_file_t in csv_list:
        print('Analysing {}..............................................'.format(csv_file_t), end='\r')
        in_file_path    = '{}/{}'.format(in_dir, csv_file_t)
        dframe_t        = pd.read_csv(in_file_path, index_col=0)
        dframe_t        = dframe_t[['o', 'h', 'l', 'c', 'v']].rename(columns=col_map)
        dframe_t.index.name = 'Date'
        dframe_t.to_csv('{}/{}'.format(out_dir, csv_file_t))
    # endfor
# enddef
