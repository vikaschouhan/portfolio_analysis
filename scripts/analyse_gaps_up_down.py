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
    rets_data  = {}

    # Iterate over all data, get all gaps and downs
    for ticker_t in asset_data:
        data_t = asset_data[ticker_t]
        gapsup = (data_t['Open'] - data_t['High'].shift())/data_t['High'].shift()
        gapsdn = (data_t['Low'].shift() - data_t['Open'])/data_t['Low'].shift()

        # Create new dataframe joining returns and volume
        dframe = pd.DataFrame(index=gapsup.index)
        dframe['gap_up'] = gapsup
        dframe['gap_dn'] = gapsdn

        # Store
        rets_data[ticker_t] = dframe
    # endfor

    return rets_data
# enddef

def analyse_rets_data(rets_mat, last_candles=10):
    gup_mat = pd.concat([v['gap_up'].rename(k) for k,v in rets_mat.items()], axis=1)
    gdn_mat = pd.concat([v['gap_dn'].rename(k) for k,v in rets_mat.items()], axis=1)
    
    rets_u   = []
    rets_d   = []
    dsize    = len(rets_mat)
    dsize    = dsize if dsize < last_candles else last_candles
    dmat     = pd.DataFrame(index=gup_mat.index[-dsize:])

    def __sort_rd(x):
        return collections.OrderedDict(sorted(x.items()))
    # enddef

    for indx_t in range(dsize):
        gaps_up   = gup_mat.iloc[-indx_t-1].sort_values(ascending=False)
        gaps_dn   = gdn_mat.iloc[-indx_t-1].sort_values(ascending=False)
        # Filter for gapups/gapdowns
        gaps_up   = __sort_rd(gaps_up[gaps_up > 0].to_dict())
        gaps_dn   = __sort_rd(gaps_dn[gaps_dn > 0].to_dict())
        # Append
        rets_u.append(gaps_up)
        rets_d.append(gaps_dn)
    # endfor

    dmat['gap_up']  = list(reversed(rets_u)) #list(reversed([__rd_str(x) for x in rets_g]))
    dmat['gap_dn']  = list(reversed(rets_d)) #list(reversed([__rd_str(x) for x in rets_l]))
    # Reverse in decreasing order of dates
    dmat            = dmat.iloc[::-1]

    return dmat
# enddef

def flatten_sheet(data):
    gaps_up      = []
    gaps_up_num  = []
    gaps_dn      = []
    gaps_dn_num  = []
    time_l       = []

    for i in range(len(data)):
        # Calculate total cells for combined gap_up and gap_dn
        d_cells  = max(len(data.iloc[i]['gap_up']), len(data.iloc[i]['gap_dn']))
        gup_keys = list(data.iloc[i]['gap_up'].keys())
        gup_vals = [data.iloc[i]['gap_up'][x] for x in gup_keys]
        gdn_keys = list(data.iloc[i]['gap_dn'].keys())
        gdn_vals = [data.iloc[i]['gap_dn'][x] for x in gdn_keys]

        for j in range(d_cells):
            try:
                gaps_up.append(gup_keys[j])
            except:
                gaps_up.append(np.nan)
            # endtry
            try:
                gaps_up_num.append(gup_vals[j])
            except:
                gaps_up_num.append(np.nan)
            # endtry
            try:
                gaps_dn.append(gdn_keys[j])
            except:
                gaps_dn.append(np.nan)
            # endtry
            try:
                gaps_dn_num.append(gdn_vals[j])
            except:
                gaps_dn_num.append(np.nan)
            # endtry

            if data.index[i] not in time_l:
                time_l.append(data.index[i])
            else:
                time_l.append(np.nan)
            # endif
        # endfor
    # endfor

    pframe = pd.DataFrame(index=range(len(time_l)))
    pframe['t']            = time_l
    pframe['gaps_up']      = gaps_up
    pframe['gaps_up_perc'] = gaps_up_num
    pframe['gaps_dn']      = gaps_dn
    pframe['gaps_dn_perc'] = gaps_dn_num

    # Reset index
    pframe = pframe.set_index('t')
    
    return pframe
# enddef

def analyse_for_gaps(csv_dir, xls_file, last_candles=10):
    rets_data = process_csvs(csv_dir)
    gn_data   = analyse_rets_data(rets_data, last_candles=last_candles)
    gn_data   = flatten_sheet(gn_data)
    # Write to excel sheet
    print('>> Writing historical top gainers and losers data to {}'.format(xls_file))
    df_to_excel({'sheet1': gn_data}, xls_file)
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csv_dir',     help='Directory with all csv files', type=str, default=None)
    parser.add_argument('--xls',         help='Output xls file', type=str, default=None)
    parser.add_argument('--sessions',    help='Only generate data for last n sessions', type=int, default=10)
    args    = parser.parse_args()

    csv_dir = args.__dict__['csv_dir']
    xls_f   = args.__dict__['xls']
    sess_s  = args.__dict__['sessions']

    if csv_dir is None or xls_f is None:
        print('--csv_dir & --xls are mandatory.')
        sys.exit(-1)
    # endif

    analyse_for_gaps(csv_dir, xls_f, sess_s)
# endif
