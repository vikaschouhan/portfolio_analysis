#!/usr/bin/env python3
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# csv generator for Zerodha Kite platform

import pandas as pd
import os
import argparse
import sys
import shutil
import csv
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules import core as invs_core
from   modules import utils as invs_utils
from   modules import parsers as invs_parsers

# Aliases
coloritf   = invs_utils.coloritf
coloritb   = invs_utils.coloritb

# CSV report generator
def run_csv_gen(sym_list, instr_file, kis_res, pub_tok, output_dir, verbose=False):
    assert output_dir != None

    output_dir = invs_utils.rp(output_dir)
    if not os.path.isdir(output_dir):
        print("{} doesn't exist. Creating it now !!".format(output_dir))
        os.makedirs(output_dir)
    # endif
    print('Output dir = {}'.format(output_dir))

    # Read instrument file into dataframe
    dframe_instrs = pd.read_csv(instr_file)

    for ctr, sym_this in enumerate(sym_list):
        ticker_this = search_sym_in_kite_instruments(dframe_instrs, sym_this)
        if ticker_this is None:
            continue
        # endif

        # Fetch data
        d_this   = invs_core.fetch_data_kite(ticker_this, kis_res, pub_tok, verbose=verbose)

        # If dataframe is empty, continue
        if d_this.empty:
            print('Couldnot download data for {}'.format(sym_this))
            return
        # endif

        # save to CSV file
        csv_file_this = output_dir + '/{}_{}.csv'.format(sym_this, kis_res)
        print('{}. Downloading CSV Report for {}'.format(ctr, coloritf(sym_this, 'magenta')))
        d_this.to_csv(csv_file_this)
    # endfor
# enddef

def search_sym_in_kite_instruments(dframe, symbol):
    dsearch   = dframe[dframe['tradingsymbol'] == symbol]
    if len(dsearch) == 0:
        print('ERROR:: Symbol {} not found !!'.format(symbol))
        return None
    # endif

    # Get ticker
    ticker    = dsearch['instrument_token'].iloc[0]
    return ticker
# enddef

#########################################################
# Main

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--instr',   help='Kite instruments file', type=str, default=None)
    parser.add_argument('--res',     help='Resolution', type=str, default='1W')
    parser.add_argument('--sym',     help='Security symbol(s).', type=str, default=None)
    parser.add_argument('--odir',    help='Output directory where csvs are stored.', type=str, default=None)
    parser.add_argument('--ptok',    help='Public token key.', type=str, default=None)
    parser.add_argument('--verbose', help='Verbose mode', action='store_true')
    args    = parser.parse_args()

    if not args.__dict__['sym']:
        print('--sym is required !!')
        sys.exit(-1)
    # endif
    if not args.__dict__['ptok']:
        print('--ptok is required !!')
        sys.exit(-1)
    # endif
    if not args.__dict__['odir']:
        print('--odir is required !!')
        sys.exit(-1)
    # endif

    if not args.__dict__['instr']:
        # Try to download kite instruments file
        kis_db_file = invs_utils.download_kite_instruments()
        assert kis_db_file is not None, 'Couldnot download kite instruments file. Please provide --instr option.'
    else:
        print('Using {} as Zerodha Kite database file.'.format(args.__dict__['instr']))
        kis_db_file = args.__dict__['instr']
    # endif

    # Vars
    kis_db_f   = os.path.expanduser(kis_db_file)
    sym_list   = invs_utils.parse_sarg(args.__dict__['sym'])
    kis_res    = args.__dict__['res']
    out_dir    = args.__dict__['odir']
    pub_tok    = args.__dict__['ptok']
    verbose    = args.__dict__['verbose']

    run_csv_gen(sym_list, kis_db_f, kis_res=kis_res, pub_tok=pub_tok, output_dir=args.__dict__['odir'], verbose=verbose)
# endif
