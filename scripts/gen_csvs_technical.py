#!/usr/bin/env python3
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# csv generator

import os
import argparse
import sys
import shutil
import csv

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules import core as invs_core
from   modules import utils as invs_utils
from   modules import parsers as invs_parsers

# Aliases
coloritf   = invs_utils.coloritf
coloritb   = invs_utils.coloritb

# CSV report generator
def run_csv_gen(sec_dict, invs_res, output_dir, verbose=False):
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
        d_this   = invs_core.fetch_data(sec_dict[sec_code]['ticker'], invs_res, verbose=verbose)
        sec_name = sec_dict[sec_code]['name']

        # If dataframe is empty, continue
        if d_this.empty:
            continue
        # endif

        # Set time axis as index
        d_this = d_this.set_index('t')

        # save to CSV file
        csv_file_this = output_dir + '/{}_{}.csv'.format(sec_name.replace(' ', '_'), invs_res)
        print('{}. CSV Report for {}'.format(ctr, coloritf(sec_name, 'magenta')))
        d_this.to_csv(csv_file_this)

        ctr = ctr + 1
    # endfor

    # Write to csv file
    print(coloritf('--------------------- REPORT END --------------------------------', 'green'))
# enddef

#########################################################
# Main

if __name__ == '__main__':
    dot_invs_py = '~/.investing_dot_com_security_dict.py'
    dot_invs_py_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_invs_py)) and os.path.isfile(os.path.expanduser(dot_invs_py)):
        dot_invs_py_exists = True
    # endif

    parser  = argparse.ArgumentParser()
    parser.add_argument('--invs',    help='Investing.com database file (populated by eq_scan_on_investing_dot_com.py)', type=str, default=None)
    parser.add_argument('--res',     help='Resolution', type=str, default='1W')
    parser.add_argument('--sfile',   help='Security csv file. Can be list file or bhavcopy file.', type=str, default=None)
    parser.add_argument('--odir',    help='Output directory where csvs are stored.', type=str, default=None)
    parser.add_argument('--verbose', help='Enable verbose mode', action='store_true')
    args    = parser.parse_args()

    if not args.__dict__['invs']:
        if dot_invs_py_exists:
            print('Using {} as Investing.com database file.'.format(dot_invs_py))
            invs_db_file = dot_invs_py
        else:
            print('--invs is required !!')
            sys.exit(-1)
        # endif
    else:
        print('Using {} as Investing.com database file.'.format(args.__dict__['invs']))
        invs_db_file = args.__dict__['invs']

        # Copy the passed file to dot_invs_py
        print('Copying {} to {} ..'.format(invs_db_file, dot_invs_py))
        shutil.copyfile(os.path.expanduser(invs_db_file), os.path.expanduser(dot_invs_py))
    # endif
    if not args.__dict__['sfile']:
        print('--sfile is required !! It should be one of supported types : {}'.format(invs_parsers.populate_sec_list(None)))
        sys.exit(-1)
    # endif

    # Vars
    invs_db_f  = os.path.expanduser(invs_db_file)
    sec_file   = args.__dict__['sfile']
    invs_res   = args.__dict__['res']
    out_dir    = args.__dict__['odir']
    verbose    = args.__dict__['verbose']

    sec_tick_d = invs_parsers.populate_sym_list_from_sec_file(invs_db_f, sec_file)
    run_csv_gen(sec_tick_d, invs_res=invs_res, output_dir=args.__dict__['odir'], verbose=verbose)
# endif
