#!/usr/bin/env python3
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# Pull nse live analysis data (like top gainers, losers etc).

from   modules import invs_core
from   modules import invs_plot
from   modules import invs_scanners
from   modules import invs_utils
from   modules import invs_tools
from   modules import invs_parsers
from   modules import invs_indicators
import logging
from   colorama import Fore, Back, Style
import os
import argparse
import sys
import re
import datetime
import shutil
import csv
import copy
import requests

def populate_sym_dict(invs_dict_file, in_sec_dict):
    # Convert inv_dot_com_db_list to dict:
    inv_dot_com_db_dict = invs_utils.parse_dict_file(invs_dict_file)
    # Generate nse dict
    nse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'nse_code' in item_this and item_this[u'nse_code']:
            nse_dict[item_this[u'nse_code']] = item_this
        # endif
    # endfor

    # code list
    nse_keys = nse_dict.keys()

    # Search for tickers
    sec_dict = {}
    not_f_l  = []
    for sec_this in in_sec_dict:
        sec_code = sec_this
        # Search
        if sec_code in nse_keys:
            sec_dict[sec_code] = {
                                     'ticker' : nse_dict[sec_code][u'ticker'],
                                     'name'   : nse_dict[sec_code][u'description'],
                                 }
        else:
            not_f_l.append(sec_this)
        # endif
    # endfor
    print(Back.RED + '{} not found in investing.com db'.format(not_f_l) + Back.RESET)

    return sec_dict
# enddef

def fetch_nse_live_security_info(key):
    supported_key_dict = {
            'nifty_gainers' : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json',
            'fno_gainers'   : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/fnoGainers1.json',
            'nifty_losers'  : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/niftyLosers1.json',
            'fno_losers'    : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/niftyLosers1.json',
            ##
            'jr_nifty_gainers' : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/jrNiftyGainers1.json',
            'sec_gt20_gainers' : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/secGt20Gainers1.json',
            'sec_lt20_gainers' : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/secLt20Gainers1.json',
            'all_top_gainers'  : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/allTopGainers1.json',
            ##
            'jr_nifty_losers'  : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/niftyLosers1.json',
            'sec_gt20_losers'  : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/secGt20Losers1.json',
            'sec_lt20_losers'  : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/secLt20Losers1.json',
            'all_top_losers'   : 'https://www.nseindia.com/live_market/dynaContent/live_analysis/losers/allTopLosers1.json'
        }
    supported_keys = list(supported_key_dict.keys())
    if key not in supported_keys:
        print('key {} not supported. Supported keys = {}'.format(key, supported_keys))
        return {}
    # endif

    fetch_url = supported_key_dict[key]
    # Fetch data
    req = requests.get(fetch_url, headers={'User-Agent' : 'Mozilla/6.0'})
    req_json = req.json()

    # Parse
    sec_dict = {}
    for item_t in req_json['data']:
        sec_dict[item_t['symbol']] = item_t
    # endfor

    return sec_dict
# enddef

#########################################################
# Main

if __name__ == '__main__':
    # Logging init
    logging.basicConfig(filename='/tmp/scan_security_list_technical.py.log', filemode='w', level=logging.DEBUG)

    dot_invs_py = '~/.investing_dot_com_security_dict.py'
    dot_invs_py_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_invs_py)) and os.path.isfile(os.path.expanduser(dot_invs_py)):
        dot_invs_py_exists = True
    # endif

    parser  = argparse.ArgumentParser()
    parser.add_argument("--invs",    help="Investing.com database file (populated by eq_scan_on_investing_dot_com.py)", type=str, default=None)
    parser.add_argument("--ofile",   help="Output file.", type=str, default=None)
    parser.add_argument("--key",     help="Fetch key (type of data to be fetched", type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["invs"]:
        if dot_invs_py_exists:
            print('Using {} as Investing.com database file.'.format(dot_invs_py))
            invs_db_file = dot_invs_py
        else:
            print("--invs is required !!")
            sys.exit(-1)
        # endif
    else:
        print('Using {} as Investing.com database file.'.format(args.__dict__["invs"]))
        invs_db_file = args.__dict__["invs"]

        # Copy the passed file to dot_invs_py
        print('Copying {} to {} ..'.format(invs_db_file, dot_invs_py))
        shutil.copyfile(os.path.expanduser(invs_db_file), os.path.expanduser(dot_invs_py))
    # endif
    if not args.__dict__["ofile"]:
        print("--ofile is required !!")
        sys.exit(-1)
    # endif
    if not args.__dict__["key"]:
        print("--key is required !!")
        sys.exit(-1)
    # endif

    # Get security dictionary according to key passed
    sec_dict   = fetch_nse_live_security_info(args.__dict__["key"])
    if len(sec_dict) == 0:
        print('Empty data returned from nse !!')
        sys.exit(-1)
    # endif

    # Vars
    invs_db_f  = os.path.expanduser(invs_db_file)
    out_file   = args.__dict__["ofile"]

    # Get security list from screener.in using default screen_no=17942
    print('Found {} securities.'.format(len(sec_dict)))
    sec_tick_d = populate_sym_dict(invs_db_f, sec_dict)
    print('Found {} securities in investing_com database.'.format(len(sec_tick_d)))

    # Write this info in output file
    print('Writing security info to {}'.format(out_file))
    with open(out_file, 'w') as f_out:
        f_out.write('nse_eqlist_m\n')
        f_out.write('SYMBOL, NAME OF COMPANY\n')
        for k_t in sec_tick_d:
            f_out.write('{}, {}\n'.format(k_t, sec_tick_d[k_t]['name']))
        # endfor
    # endwith
# endif
