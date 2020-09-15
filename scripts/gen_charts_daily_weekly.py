import pandas as pd
import nsepy
import datetime
import argparse
import mplfinance as mplf
import sys
import os
import shutil
from   decimal import Decimal
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *
from   modules.parsers import parse_security_file

def resample_weekly(df):
    return df.resample('W').agg({'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'},
        loffset = pd.offsets.timedelta(days=-6))
# enddef

def get_daily_data(symbol, start=None, end=None):
    start = datetime.datetime(2001, 1, 1) if start is None else start
    end   = datetime.datetime.now() if end is None else end
    data  = nsepy.get_history(symbol, start, end)
    if len(data) == 0:
        data = nsepy.get_history(symbol, start, end, index=True)
        if len(data) == 0:
            raise ValueError('Invalid symbol {}'.format(symbol))
        # endif
    # endif
    data.index = pd.to_datetime(data.index)
    return data
# enddef

def format_price(x, _=None):
    x = Decimal(x)
    return x.quantize(Decimal(1)) if x == x.to_integral() else x.normalize()
# enddef

def plot_candlestick(df, title, savefig):
    # Generate log plot. Currently it's not supported by mplf.plot,
    # so we do it overselves.
    kwargs = dict(type='candle', mav=(200), volume=True)
    fig, axlist = mplf.plot(df, ylabel='Price', title=title, returnfig=True, **kwargs, style='yahoo')
    ax1 = axlist[0]
    ax1_minor_yticks = ax1.get_yticks(True)  # save the original ticks because the log ticks are sparse
    ax1_major_yticks = ax1.get_yticks(False)
    ax1.set_yscale('log')
    ax1.set_yticks(ax1_major_yticks, True)
    ax1.set_yticks(ax1_minor_yticks, False)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_price))
    ax1.yaxis.set_minor_formatter(ticker.FuncFormatter(format_price))
    ax1.autoscale()
    plt.savefig(savefig)
    plt.close('all')
# enddef

def generate_candlesticks(sym_list, out_file, start_year=None, n_candles=130):
    t_dir    = '/tmp/___tmp_dir' # temporary dir
    t1_dir   = os.path.join(t_dir, 'l0')
    t2_dir   = os.path.join(t_dir, 'l1')

    mkdir(t1_dir)
    mkdir(t2_dir)

    for indx_t, sym_t in enumerate(sym_list):
        try:
            d_data = get_daily_data(sym_t, start=datetime.datetime(start_year, 1, 1))
        except ValueError as e:
            print(e)
            continue
        # endtry
        w_data = resample_weekly(d_data)

        # Save daily and weekly data
        tt_dir = os.path.join(t1_dir, sym_t)
        mkdir(tt_dir)

        d_data_f = os.path.join(tt_dir, 'd.png')
        w_data_f = os.path.join(tt_dir, 'w.png')

        # Select only n_candles
        d_data   = d_data[-n_candles:] if n_candles < len(d_data) else d_data
        w_data   = w_data[-n_candles:] if n_candles < len(w_data) else w_data

        plot_candlestick(d_data, sym_t + ' DAILY', d_data_f)
        plot_candlestick(w_data, sym_t + ' WEEKLY', w_data_f)

        print('>> [{}/{}]'.format(indx_t+1, len(sym_list)), end='\r')
    # endfor

    # Done saving individual images, time to combine then
    # Iterate over sym_list
    for indx_t, sym_t in enumerate(sym_list):
        files_list_t = [os.path.join(t1_dir, sym_t, 'd.png'), os.path.join(t1_dir, sym_t, 'w.png')]
        merge_images_horizontally(files_list_t, os.path.join(t2_dir, '{}.png'.format(sym_t)))
    # endfor

    # Now we will merge all of them
    print('>> Writing final image to {}'.format(out_file))
    files_list_f = sorted(glob.glob(os.path.join(t2_dir, '*.png')))
    merge_images_vertically(files_list_f, out_file)

    # Remove tmp dir
    shutil.rmtree(t_dir)
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--sfile',      help='Database security file.',         type=str, default=None)
    parser.add_argument('--out',        help='Output file.',                    type=str, default=None)
    parser.add_argument('--start_year', help='Start year for collecting data',  type=int, default=2019)
    parser.add_argument('--ncandles',   help='Number of candles to plot.',      type=int, default=100)
    args    = parser.parse_args()

    if args.__dict__['sfile'] is None or args.__dict__['out'] is None:
        print('All options are mandatory.Please use --help for more information.')
        sys.exit(-1)
    # endif

    sec_file   = rp(args.__dict__['sfile'])
    out_file   = rp(args.__dict__['out'])
    n_candles  = args.__dict__['ncandles']
    start_year = args.__dict__['start_year']

    # Read security file
    sec_dict = parse_security_file(sec_file, 'dict')
    sym_list = list(sec_dict.keys())

    # Remove Symbol if present
    sym_list = list(set(sym_list) - set(['Symbol']))

    print('>> sym_list = {}'.format(sym_list))

    # Generate candlesticks
    generate_candlesticks(sym_list, out_file, start_year, n_candles)
# endif
