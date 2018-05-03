# NOTE : This script requires python3

# 
# Moving average backtester using pysystemtrader(https://github.com/robcarver17/pysystemtrade)
# @args :  csvdir -> dir containing price data for all instruments to be anlysed
#          outdir -> output dir for generating graphs and stats
#          ma_plist -> moving average period list

from   syscore.algos import robust_vol_calc
from   syscore.accounting import accountCurve
import pandas as pd
import os
import sys
import glob
import matplotlib.pyplot as plt
import json
import argparse

def rp(path):
    return os.path.expanduser(path)
# enddef

def cdir(d_path):
    d_path = rp(d_path)
    if not os.path.isdir(d_path):
        os.mkdir(d_path)
    # endif
    return d_path
# enddef

def calc_ewmac_forecast(price, l_fast, l_slow=None):
    if l_slow is None:
        l_slow = 4 * l_fast

    # We don't need to calculate the decay parameter, just use the span
    # directly
    fast_ewma = price.ewm(span=l_fast).mean()
    slow_ewma = price.ewm(span=l_slow).mean()
    raw_ewmac = fast_ewma - slow_ewma

    vol = robust_vol_calc(price.diff())
    return raw_ewmac / vol
# enddef


def gen_stats_ewma_forecast(price_data, l_slow, l_fast):
    ewmac = calc_ewmac_forecast(price_data, l_slow, l_fast)
    ewmac.columns=['forecast']
    account = accountCurve(price_data, forecast=ewmac)
    
    return account
# enddef


def run_ewma_strategy_on_csv_files(csv_dir, out_dir, l_fast, l_slow):
    csv_dir = cdir(csv_dir)
    out_dir = cdir(out_dir)

    files = glob.glob('{}/*.csv'.format(csv_dir))
    if len(files) == 0:
        print('No csv files found.')
        return
    # endif

    stats_dict = {}
    ctr = 0
    for file_t in files:
        file_name  = os.path.basename(file_t)
        print('{}. Analysing {}'.format(ctr, file_name))

        price_data = pd.read_csv(file_t, index_col='t', parse_dates=['t'])['c']
        stats_dict[file_name] = gen_stats_ewma_forecast(price_data, l_fast, l_slow)

        acc_obj = stats_dict[file_name]

        # Plot eq curve
        acc_obj.curve().plot()
        plt.savefig('{}/{}_{}.png'.format(out_dir, file_name, 'curve_plot'))
        plt.clf()
        plt.close('all')

        # Write stats
        stats = acc_obj.percent().stats()
        with open('{}/{}_{}.json'.format(out_dir, file_name, 'stats'), 'w') as s_file:
            s_file.write(json.dumps({'stats' : stats}))
        # endif

        ctr = ctr + 1
    # endfor

    return stats_dict
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csvdir',    help='Csv dir for scrips', type=str, default=None)
    parser.add_argument('--ma_plist',  help='Moving average period list separated by comma.', type=str, default='14,21')
    parser.add_argument('--outdir',    help='Output dir for generated files', type=str, default=None)

    args = parser.parse_args()

    if not args.__dict__['csvdir']:
        print('--csvdir required.')
        sys.exit(-1)
    # endif
    if not args.__dict__['outdir']:
        print('--outdir requird')
        sys.exit(-1)
    # endif

    ma_plist = [int(x) for x in args.__dict__['ma_plist'].split(',')]
    csv_dir  = args.__dict__['csvdir']
    out_dir  = args.__dict__['outdir']

    run_ewma_strategy_on_csv_files(csv_dir, out_dir, ma_plist[0], ma_plist[1])
# endif
