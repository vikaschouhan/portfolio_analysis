#!/usr/bin/env python3
# Author : Vikas Chouhan (presentisgood@gmail.com)
import argparse
import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *
##

def logr_to_r(x):
    return np.exp(x) - 1
# enddef

def analyse_mean_returns(csv_dir):
    asset_data = read_all_asset_csvs(csv_dir)
    # Iterate over all data, calculate % rets
    rets_data  = {}
    for ticker_t in asset_data:
        data_t = asset_data[ticker_t]
        rets   = np.log(data_t['Close']) - np.log(data_t['Close'].shift())
        rngs   = np.log(data_t['Close']) - np.log(data_t['Open'])

        # Create new dataframe joining returns and volume
        # Store
        rets_data[ticker_t] = {'r_mean'     : rets.mean(),
                               'r_std'      : rets.std(),
                               'rng_mean'   : rngs.mean(),
                               'rng_std'    : rngs.std(),
                              }
    # endfor

    # Convert to pandas dataframe
    rets_data = pd.DataFrame.from_dict(rets_data).T
    # Add columns
    rets_data['abs_r_mean'] = abs(logr_to_r(rets_data['r_mean']))
    rets_data['abs_r_std']  = abs(logr_to_r(rets_data['r_std']))
    rets_data['abs_rng_mean'] = abs(logr_to_r(rets_data['rng_mean']))
    rets_data['abs_rng_std']  = abs(logr_to_r(rets_data['rng_std']))

    return rets_data
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csv_dir',     help='Directory with all csv files', type=str, default=None)
    parser.add_argument('--xls',         help='Output xls file', type=str, default=None)
    args    = parser.parse_args()

    csv_dir = args.__dict__['csv_dir']
    xls_f   = args.__dict__['xls']

    if csv_dir is None or xls_f is None:
        print('--csv_dir & --xls are mandatory.')
        sys.exit(-1)
    # endif

    rets = analyse_mean_returns(csv_dir)
    df_to_excel({'sheet1': rets}, xls_f)
# endif
