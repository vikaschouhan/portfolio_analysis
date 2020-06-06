# Author  : Vikas Chouhan (presentisgood@gmail.com)
# Year    : 2020
# License : GPLv2
import pandas as pd
import copy
import argparse
import sys, os
import collections

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *
from   tabulate import tabulate
##

def resample_df(df, tf='1D'):
    return df.resample(tf).agg({'Open':'first', 'High':'max', 'Low':'min', 'Close': 'last', 'Volume': 'sum' }).dropna()
# enddef

def process_csvs(csv_dir):
    asset_data = read_all_asset_csvs(csv_dir)
    # Iterate over all data, calculate % rets
    rets_data    = {}
    for ticker_t in asset_data:
        data_t    = asset_data[ticker_t]
        data_1D_t = resample_df(data_t)

        data_copy       = copy.copy(data_t)
        data_copy.index = data_copy.index.date
        data_copy       = data_copy.groupby(data_copy.index).first()

        data_1D_t['Open_fc']  = data_copy['Open']
        data_1D_t['Close_fc'] = data_copy['Close']
        data_1D_t['High_fc']  = data_copy['High']
        data_1D_t['Low_fc']   = data_copy['Low']
        
        data_1D_t['rets_close_fc']      = (data_1D_t['Close_fc'] - data_1D_t['Close'].shift())/data_1D_t['Close'].shift()
        data_1D_t['rets']               = (data_1D_t['Close'] - data_1D_t['Close'].shift())/data_1D_t['Close'].shift()
        data_1D_t['rets_bar_fc']        = (data_1D_t['Close_fc'] - data_1D_t['Open'])/data_1D_t['Open']

        # Store
        rets_data[ticker_t] = {'rets': data_1D_t['rets'], 'rets_close_fc': data_1D_t['rets_close_fc']}
    # endfor

    return rets_data
# enddef

def analyse_returns(rets_data, topn=5, last_candles=10):
    # Calculate return and volume matrices
    rets_mat     = pd.concat([v['rets'].rename(k) for k,v in rets_data.items()], axis=1)
    rets_fc_mat  = pd.concat([v['rets_close_fc'].rename(k) for k,v in rets_data.items()], axis=1)
    
    rets_g    = []
    rets_l    = []
    rets_fc_g = []
    rets_fc_l = []
    dsize     = len(rets_mat)
    dsize     = dsize if dsize < last_candles else last_candles
    dmat      = pd.DataFrame(index=rets_mat.index[-dsize:])

    def __sort_rd(x):
        return collections.OrderedDict(sorted(x.items()))
    # enddef

    for indx_t in range(dsize):
        rets_topn = rets_mat.iloc[-indx_t-1].sort_values(ascending=False)[:topn].to_dict()
        rets_botn = rets_mat.iloc[-indx_t-1].sort_values()[:topn].to_dict()
        rets_topn = __sort_rd({k:precision(v, 4) for k,v in rets_topn.items()})
        rets_botn = __sort_rd({k:precision(v, 4) for k,v in rets_botn.items()})

        rets_fc_topn = rets_fc_mat.iloc[-indx_t-1].sort_values(ascending=False)[:topn].to_dict()
        rets_fc_botn = rets_fc_mat.iloc[-indx_t-1].sort_values()[:topn].to_dict()
        rets_fc_topn = __sort_rd({k:precision(v, 4) for k,v in rets_fc_topn.items()})
        rets_fc_botn = __sort_rd({k:precision(v, 4) for k,v in rets_fc_botn.items()})

        # Append
        rets_g.append(rets_topn)
        rets_l.append(rets_botn)
        rets_fc_g.append(rets_fc_topn)
        rets_fc_l.append(rets_fc_botn)
    # endfor

    def __rd_str(x):
        p_str = ''
        for k,v in x.items():
            p_str += '{} ({}%)\n'.format(k, v*100)
        # endfor
        return p_str
    # enddef

    dmat['gainers']    = list(reversed(rets_g))
    dmat['losers']     = list(reversed(rets_l))
    dmat['fc_gainers'] = list(reversed(rets_fc_g))
    dmat['fc_losers']  = list(reversed(rets_fc_l))

    # Reverse in decreasing order of dates
    dmat            = dmat.iloc[::-1]

    return dmat
# enddef

def flatten_gl_sheet(data):
    gainers         = []
    gainers_perc    = []
    losers          = []
    losers_perc     = []
    time_l          = []
    fc_gainers      = []
    fc_gainers_perc = []
    fc_losers       = []
    fc_losers_perc  = []

    for i in range(len(data)):
        for k,v in data.iloc[i]['gainers'].items():
            gainers.append(k)
            gainers_perc.append(v)
            if data.index[i] not in time_l:
                time_l.append(data.index[i])
            else:
                time_l.append(np.nan)
            # endif
        # endfor
    # endfor

    for i in range(len(data)):
        for k,v in data.iloc[i]['losers'].items():
            losers.append(k)
            losers_perc.append(v)
        # endfor
    # endfor

    for i in range(len(data)):
        for k,v in data.iloc[i]['fc_gainers'].items():
            fc_gainers.append(k)
            fc_gainers_perc.append(v)
        # endfor
    # endfor

    for i in range(len(data)):
        for k,v in data.iloc[i]['fc_losers'].items():
            fc_losers.append(k)
            fc_losers_perc.append(v)
        # endfor
    # endfor

    pframe = pd.DataFrame(index=range(len(time_l)))
    pframe['t'] = time_l
    pframe['gainers'] = gainers
    pframe['gainers_perc'] = gainers_perc
    pframe['losers'] = losers
    pframe['losers_perc'] = losers_perc
    pframe['fc_gainers'] = fc_gainers
    pframe['fc_gainers_perc'] = fc_gainers_perc
    pframe['fc_losers'] = fc_losers
    pframe['fc_losers_perc'] = fc_losers_perc

    # Reset index
    pframe = pframe.set_index('t')
    
    return pframe
# enddef

# rets_dmat is what we get after calling analyse_returns()
def analyse_fc_performers_vs_overall_performers(rets_dmat):
    # Derive topn value with which rets_dmat was generated.
    topn = rets_dmat['gainers'].apply(lambda x: len(x)).max()

    gainers_intersec  = []
    losers_intersec   = []
    gainers_isec_list = []
    losers_isec_list  = []
    gainers_rat_list  = []
    losers_rat_list   = []
    for i in range(len(rets_dmat)):
        g_isecs = set(rets_dmat.iloc[i]['gainers'].keys()).intersection(set(rets_dmat.iloc[i]['fc_gainers'].keys()))
        l_isecs = set(rets_dmat.iloc[i]['losers'].keys()).intersection(set(rets_dmat.iloc[i]['fc_losers'].keys()))

        gainers_intersec.append(len(g_isecs))
        losers_intersec.append(len(l_isecs))
        gainers_isec_list.append(g_isecs)
        losers_isec_list.append(l_isecs)
        try:
            gainers_rat_list.append(np.average([rets_dmat.iloc[i]['gainers'][x]/rets_dmat.iloc[i]['fc_gainers'][x] for x in g_isecs]))
        except ZeroDivisionError:
            gainers_rat_list.append(np.nan)
        # endtry
        try:
            losers_rat_list.append(np.average([rets_dmat.iloc[i]['losers'][x]/rets_dmat.iloc[i]['fc_losers'][x] for x in l_isecs]))
        except ZeroDivisionError:
            losers_rat_list.append(np.nan)
        # endtry
    # endfor

    rets_dmat['gainers_intersec'] = gainers_intersec
    rets_dmat['losers_intersec']  = losers_intersec
    rets_dmat['gainers_avg_rets_ratio'] = gainers_rat_list
    rets_dmat['losers_avg_rets_ratio']  = losers_rat_list
# enddef

def analyse_for_top_gainers_and_losers_from_intraday_charts(csv_dir, xls_file, topn=5, last_candles=10):
    rets_data = process_csvs(csv_dir)
    gn_data   = analyse_returns(rets_data, topn=topn, last_candles=last_candles)
    gn_data   = flatten_gl_sheet(gn_data)
    # Write to excel sheet
    print('>> Writing historical top gainers and losers data to {}'.format(xls_file))
    df_to_excel({'sheet1': gn_data}, xls_file)
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

    analyse_for_top_gainers_and_losers_from_intraday_charts(csv_dir, xls_f, topn, sess_s)
# endif
