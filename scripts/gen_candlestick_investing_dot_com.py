#!/usr/bin/env python3
#
# Author  : Vikas Chouhan (presentisgood@gmail.com)
# License : GPLv2

import argparse
import copy
import time
import sys
import os
import contextlib, warnings

import copy
from   modules import invs_core
from   modules import invs_plot


# Process watchlist
def process_watchlist_file(wfile):
    w_list = []
    with open(os.path.expanduser(wfile), 'r') as f_in:
        for l_this in f_in:
            e_a = l_this.replace('\n', '').split(':')
            sym_name = e_a[0]
            exchg    = e_a[1]
            sym_res  = e_a[2].replace(' ', '')
            try:
                ma_list =  [ int(x) for x in e_a[3].split(',') ]
            except:
                print('{} does not look like a period list seperated by commas.'.format(e_a[3].split(',')))
                sys.exit(-1)
            # endtry
            try:
                num_bars = int(e_a[4])
            except:
                print('{} does not look like an integer.'.format(e_a[4].replace(' ', '')))
                sys.exit(-1)
            # endtry
            w_list.append({
                              'name'      : sym_name,
                              'exchg'     : exchg,
                              'res'       : sym_res,
                              'ma_l'      : ma_list,
                              'nbars'     : num_bars,
                         })
        # endfor
    # endwith
    return w_list
# enddef

# Process watchlist file by name
def process_watchlist_file_by_name(wfile):
    wlist_l  = process_watchlist_file(wfile)

    # Generate a list of all securities
    sec_full_l = []
    for item_this in wlist_l:
        exchg_l = item_this['exchg'].split(',')
        sec_l  = scan_security_by_name(item_this['name'], exchg_list=exchg_l)
        for i_this in sec_l:
            # Modify this node
            i_this_tmp = copy.copy(i_this)
            i_this_tmp['symbol']               = i_this_tmp['symbol'].split(':')[0]
            i_this_tmp['resolution']           = item_this['res']
            i_this_tmp['ema_period_list']      = item_this['ma_l']
            i_this_tmp['num_bars']             = item_this['nbars']
            # Add node to main dict
            sec_full_l.append(i_this_tmp)
        # endfor
    # endfor

    return sec_full_l
# enddef

# Same as above but using local database
def process_watchlist_file_by_name_local_db(wfile, invs_db):
    wlist_l  = process_watchlist_file(wfile)

    # Generate a list of all securities
    sec_full_l = []
    for item_this in wlist_l:
        sec_l  = scan_security_by_name(item_this['name'])
        for i_this in sec_l:
            # Modify this node
            i_this_tmp = copy.copy(i_this)
            i_this_tmp['symbol']               = i_this_tmp['symbol'].split(':')[0]
            i_this_tmp['resolution']           = item_this['res']
            i_this_tmp['ema_period_list']      = item_this['ma_l']
            i_this_tmp['num_bars']             = item_this['nbars']
            # Add node to main dict
            sec_full_l.append(i_this_tmp)
        # endfor
    # endfor

    return sec_full_l
# enddef

# For use by external server
def gen_candlestick_wrap(sym, res='1D', mode='c', period_list=[9, 14, 21], plot_period=40, plot_dir='~/outputs/', plot_volume=True):
    if res not in invs_core.res_tbl:
        return "Resolution should be one of {}".format(invs_core.res_tbl.keys())
    # endif
    sec_name, _ = invs_core.scan_security_by_symbol(sym)
    j_data = fetch_data(sym, res)
    if j_data is None:
        return sec_name
    # endif
    file_name = '{}/{}_{}_{}_{}.png'.format(plot_dir, sym, res, plot_period, '-'.join([str(x) for x in period_list]))
    invs_plot.gen_candlestick(j_data, period_list=period_list, title=sec_name, file_name=file_name, plot_period=plot_period, plot_volume=plot_volume)
    return file_name
# enddef

#########################################################
# Main func
if __name__ == '__main__':
    # ignore warnings
    warnings.filterwarnings("ignore")
    send_mail = False

    prsr = argparse.ArgumentParser()
    prsr.add_argument("--sym",     help="symbol",                 type=str, default=None)
    prsr.add_argument("--res",     help="resolution",             type=str, default=None)
    prsr.add_argument("--pfile",   help="plot file",              type=str, default=None)
    prsr.add_argument("--nbars",   help="no of candles to print", type=int, default=40)
    prsr.add_argument("--stime",   help="Sleep time. Default=None", type=int, default=None)
    prsr.add_argument("--csvfile", help="write to csv file",      type=str, default=None)
    args = prsr.parse_args()

    ### Symbol
    if args.__dict__["sym"] == None:
        print('--sym is required !!')
        sys.exit(-1)
    else:
        sym = args.__dict__["sym"]
    # endif
    ### Resolution
    if args.__dict__["res"] == None:
        print('--res is required !! It can be any of the following {}'.format(invs_core.res_tbl.keys()))
        sys.exit(-1)
    else:
        assert(args.__dict__["res"] in invs_core.res_tbl.keys())
        res = args.__dict__["res"]
    # endif
    if args.__dict__["csvfile"]:
        csv_file = args.__dict__["csvfile"]
    else:
        csv_file = None
    # endif

    # init socket
    invs_core.init_sock()

    sym_name, sym = invs_core.scan_security_by_symbol(sym)
    pfile    = '~/tmp_candles.png' if not args.__dict__["pfile"] else args.__dict__["pfile"]
    nbars    = args.__dict__["nbars"]
    stime    = args.__dict__["stime"]

    print('Plotting {} for resolution {} to {}. Using {} bars, {} sleep time'.format(sym_name, res, pfile, nbars, stime))
    while True:
        # Fetch data and generate plot file
        j_data = invs_core.fetch_data(sym, res)
        # Check for any error
        if j_data is None:
            print(sym_name)
            sys.exit(-1)
        # endif
        invs_plot.gen_candlestick(j_data, period_list=[9, 14, 21], title=sym_name, file_name=pfile, plot_period=nbars)
        #gen_supp_res(j_data)
        if csv_file:
            j_data.to_csv(csv_file, encoding='utf-8', index=False)
        # endif 
        if stime == None:
            break
        else:
            # Sleep for some time
            time.sleep(stime)
        # endif
    # endwhile
# enddef
