#!/usr/bin/env python3
# Author : Vikas Chouhan (presentisgood@gmail.com)
import argparse
import sys, os
import subprocess
import collections

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *
from   tabulate import tabulate
##

def process_csvs(csv_dir):
    asset_data = read_all_asset_csvs(csv_dir)
    # Iterate over all data, calculate % rets
    rets_data  = {}
    for ticker_t in asset_data:
        data_t = asset_data[ticker_t]
        rets   = (data_t['Close'] - data_t['Close'].shift())/data_t['Close'].shift()

        # Create new dataframe joining returns and volume
        dframe = pd.DataFrame(index=rets.index)
        dframe['perc_change'] = rets
        dframe['volume']      = data_t['Volume']

        # Store
        rets_data[ticker_t] = dframe
    # endfor

    return rets_data
# enddef

def analyse_rets_data(rets, topn=5, last_candles=10):
    # Calculate return and volume matrices
    rets_mat = pd.concat([v['perc_change'].rename(k) for k,v in rets.items()], axis=1)
    vol_mat  = pd.concat([v['volume'].rename(k) for k,v in rets.items()], axis=1)
    
    rets_g   = []
    rets_l   = []
    dsize    = len(rets_mat)
    dsize    = dsize if dsize < last_candles else last_candles
    dmat     = pd.DataFrame(index=rets_mat.index[-dsize:])

    def __sort_rd(x):
        return collections.OrderedDict(sorted(x.items()))
    # enddef

    for indx_t in range(dsize):
        rets_topn = rets_mat.iloc[-indx_t-1].sort_values(ascending=False)[:topn].to_dict()
        rets_botn = rets_mat.iloc[-indx_t-1].sort_values()[:topn].to_dict()
        # add volume
        rets_topn = __sort_rd({k:precision(v) for k,v in rets_topn.items()})
        rets_botn = __sort_rd({k:precision(v) for k,v in rets_botn.items()})
        # Append
        rets_g.append(rets_topn)
        rets_l.append(rets_botn)
    # endfor

    def __rd_str(x):
        p_str = ''
        for k,v in x.items():
            p_str += '{} ({}%)\n'.format(k, v*100)
        # endfor
        return p_str
    # enddef

    dmat['gainers'] = list(reversed([__rd_str(x) for x in rets_g]))
    dmat['losers']  = list(reversed([__rd_str(x) for x in rets_l]))
    # Reverse in decreasing order of dates
    dmat            = dmat.iloc[::-1]

    return dmat
# enddef

def analyse_for_top_gainers_and_losers(csv_dir, xls_file, topn=5, last_candles=10):
    rets_data = process_csvs(csv_dir)
    gn_data   = analyse_rets_data(rets_data, topn=topn, last_candles=last_candles)
    # Write to excel sheet
    print('>> Writing historical top gainers and losers data to {}'.format(xls_file))
    gn_data.to_excel(xls_file)
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csv_dir',     help='Directory with all csv files', type=str, default=None)
    parser.add_argument('--xls',         help='Output xls file', type=str, default=None)
    parser.add_argument('--topn',        help='Number of securities to select for top gainers/losers.', type=int, default=5)
    parser.add_argument('--sessions',    help='Only generate data for last n sessions', type=int, default=10)
    args    = parser.parse_args()

    csv_dir = args.__dict__['csv_dir']
    xls_f   = args.__dict__['xls']
    topn    = args.__dict__['topn']
    sess_s  = args.__dict__['sessions']

    if csv_dir is None or xls_f is None:
        print('--csv_dir & --xls are mandatory.')
        sys.exit(-1)
    # endif

    analyse_for_top_gainers_and_losers(csv_dir, xls_f, topn, sess_s)
# endif
