#!/usr/bin/env python3

import datetime
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os, sys
import glob
from   modules.invs_utils import cdir, rp

# Check python version
sys.version_info >= (3, )

def run_algo(pd_data, algo_name, scrip_name):
    if algo_name == 'stats_basic':
        s_rets = (pd_data['c'] - pd_data['o'])/pd_data['o']
        curr_std = abs(s_rets.tail(1).mean() - s_rets.mean())
        return {
                    'values'   : [ scrip_name, s_rets.mean(), s_rets.std(), curr_std ],
                    'headers'  : [ 'scrip', 'mean', 'std', 'curr_std' ],
               }
    else:
        print('Algo name {} not supported !!'.format(algo_name))
        sys.exit(-1)
    # endif
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csvdir',    help='Csv files directory', type=str, default=None)
    parser.add_argument('--repfile',   help='Report file', type=str, default=None)
    parser.add_argument('--algo_name', help='Algorithm name.', type=str, default=None)
    parser.add_argument('--latestn',   help='Only analyse latest n samples.', type=int, default=None)
    args = parser.parse_args()

    if not args.__dict__['csvdir']:
        print('--csvdir is required !!')
        sys.exit(-1)
    # endif
    if not args.__dict__['algo_name']:
        print('--algo_name is required !!')
        sys.exit(-1)
    # endif

    csv_dir  = rp(args.__dict__['csvdir'])
    csv_dir  = cdir(csv_dir)
    csv_file = args.__dict__['repfile']
    al_name  = args.__dict__['algo_name']
    latest_n = args.__dict__['latestn']

    if csv_file == None:
        csv_file = '~/stats_{}_'.format(al_name)
        csv_file = rp(csv_file + '_{}.csv'.format(datetime.datetime.now().strftime('%s')))
    # endif

    files = glob.glob('{}/*.csv'.format(csv_dir))
    if len(files) == 0:
        print('No csv files found.')
        sys.exit(-1)
    # endif

    ##
    ret_dict  = {}
    file_ctr  = 1
    num_files = len(files)
    csv_tbl   = []

    print('Using algo {}'.format(al_name))
    for file_t in files:
        print('[{:<4}:{:<4}] Analysing {}'.format(file_ctr, num_files, file_t), end='\r')
        pd_data  = pd.read_csv(file_t, index_col='t', parse_dates=['t'])

        # drop all rows with close=0,open=0,high=0,low=0
        pd_data  = pd_data.drop(pd_data[(pd_data.c == 0.0) & (pd_data.o == 0.0) & (pd_data.h == 0.0) & (pd_data.l == 0.0)].index)

        if latest_n:
            pd_data = pd_data.tail(latest_n)
        # endif

        ret_v = run_algo(pd_data, al_name, file_t)
        if len(csv_tbl) == 0:
            csv_tbl.append(ret_v['headers'])
        # endif
        csv_tbl.append(ret_v['values'])

        file_ctr += 1
    # endfor

    # Write csv file
    print('\n')
    print('Writing report file {}'.format(csv_file))
    with open(csv_file, 'w') as f_out:
        for item_t in csv_tbl:
            f_out.write(','.join([str(x) for x in item_t]) + '\n')
        # endfor
    # endwith
# enddef
