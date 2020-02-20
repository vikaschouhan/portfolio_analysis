#!/usr/bin/env python3
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# csv generator for Zerodha Kite platform

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
def run_csv_gen(sec_dict, kis_res, pub_tok, output_dir, sleep_secs=5, interval_limit=400, verbose=False):
    ctr = 0
    assert output_dir != None

    output_dir = invs_utils.rp(output_dir)
    if not os.path.isdir(output_dir):
        print("{} doesn't exist. Creating it now !!".format(output_dir))
        os.makedirs(output_dir)
    # endif
    print('Output dir = {}'.format(output_dir))

    # Iterate over all security dict
    for sec_code in sec_dict.keys():
        # Fetch data
        d_this   = invs_core.fetch_data_kite(sec_dict[sec_code]['ticker'], kis_res, pub_tok, interval_limit=interval_limit, verbose=verbose)
        sec_name = sec_dict[sec_code]['name']

        # If dataframe is empty, continue
        if d_this.empty:
            continue
        # endif

        # save to CSV file
        csv_file_this = output_dir + '/{}_{}.csv'.format(sec_name.replace(' ', '_'), kis_res)
        print('{}. CSV Report for {}'.format(ctr, coloritf(sec_name, 'magenta')))
        d_this.to_csv(csv_file_this)

        # Sleep for some time so as not to overload server
        if sleep_secs:
            print('Sleeping for {} seconds'.format(sleep_secs))
            time.sleep(sleep_secs)
        # endif

        ctr = ctr + 1
    # endfor

    # Write to csv file
    print(coloritf('--------------------- REPORT END --------------------------------', 'green'))
# enddef

#########################################################
# Main

if __name__ == '__main__':
    dot_kis = '~/.kite_instruments.csv'
    dot_kis_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_kis)) and os.path.isfile(os.path.expanduser(dot_kis)):
        dot_kis_exists = True
    # endif

    parser  = argparse.ArgumentParser()
    parser.add_argument('--instr',   help='Kite instruments file', type=str, default=None)
    parser.add_argument('--res',     help='Resolution', type=str, default='1W')
    parser.add_argument('--sfile',   help='Security csv file. Can be list file or bhavcopy file.', type=str, default=None)
    parser.add_argument('--odir',    help='Output directory where csvs are stored.', type=str, default=None)
    parser.add_argument('--ptok',    help='Public token key.', type=str, default=None)
    parser.add_argument('--sleep',   help='Sleep for this much time.', type=int, default=None)
    parser.add_argument('--ilimit',  help='Interval limit for zerodha kite api.', type=int, default=400)
    parser.add_argument('--verbose', help='Verbose mode', action='store_true')
    args    = parser.parse_args()

    if not args.__dict__['instr']:
        if dot_kis_exists:
            print('Using {} as Zerodha Kite database file.'.format(dot_kis))
            kis_db_file = dot_kis
        else:
            print('--instr is required !!')
            sys.exit(-1)
        # endif
    else:
        print('Using {} as Zerodha Kite database file.'.format(args.__dict__['instr']))
        kis_db_file = args.__dict__['instr']

        # Copy the passed file to dot_invs_py
        print('Copying {} to {} ..'.format(kis_db_file, dot_kis))
        shutil.copyfile(os.path.expanduser(kis_db_file), os.path.expanduser(dot_kis))
    # endif
    if not args.__dict__['sfile']:
        print('--sfile is required !! It should be one of supported types : {}'.format(invs_parsers.populate_sec_list(None)))
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

    # Vars
    kis_db_f   = os.path.expanduser(kis_db_file)
    sec_file   = args.__dict__['sfile']
    kis_res    = args.__dict__['res']
    out_dir    = args.__dict__['odir']
    pub_tok    = args.__dict__['ptok']
    sleep_time = args.__dict__['sleep']
    verbose    = args.__dict__['verbose']
    ilimit     = args.__dict__['ilimit']

    sec_tick_d = invs_parsers.populate_sym_list_from_sec_file_kite(kis_db_f, sec_file)
    run_csv_gen(sec_tick_d, kis_res=kis_res, pub_tok=pub_tok, output_dir=args.__dict__['odir'],
            interval_limit=ilimit, sleep_secs=sleep_time, verbose=verbose)
# endif
