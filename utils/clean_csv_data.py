#!/usr/bin/env python3

import sys, os
import argparse
import glob

def clean_csv(csv_file, out_file):
    not_allowed_strs = ['08:45:00', '09:00:00', '15:30:00', '15:45:00']
    with open(csv_file, 'r') as f_in:
        with open(out_file, 'w') as f_out:
            for l_t in f_in:
                # Split on commans
                l_arr = l_t.split(',')
                if len(l_arr) > 1:
                    col0_arr = l_arr[0].replace(' ', '_').split('_')
                    if len(col0_arr) > 1:
                        time_str = col0_arr[1]
                        if time_str in not_allowed_strs:
                            continue
                        # endif
                    # endif
                # endif
                f_out.write(l_t)
            # endfor
        # endwith
    # endwith
# enddef

if __name__ == '__main__':
    prsr = argparse.ArgumentParser()
    prsr.add_argument("--in_dir",    help="Input csv dir",      type=str, default=None)
    prsr.add_argument("--out_dir",   help="Output csv dir",     type=str, default=None)
    args = prsr.parse_args()

    if args.__dict__['in_dir'] == None or args.__dict__['out_dir'] == None:
        print('All arguments are required. Please check --help.')
        sys.exit(-1)
    # endif

    in_dir   = args.__dict__['in_dir']
    out_dir  = args.__dict__['out_dir']

    # Check dir
    if not os.path.isdir(in_dir):
        print('{} doesnot exist.'.format(in_dir))
        sysexit(-1)
    # endif
    # Get list of all files in in_dir
    csv_list = glob.glob1(in_dir, '*.csv')
    if len(csv_list) == 0:
        print('{} is empty'.format(in_dir))
        sys.exit(-1)
    # endif
    # Create directory if required
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    # endif

    for csv_file_t in csv_list:
        print('Analysing {}..............................................'.format(csv_file_t), end='\r')
        in_file_path    = '{}/{}'.format(in_dir, csv_file_t)
        out_file_path   = '{}/{}'.format(out_dir, csv_file_t)
        clean_csv(in_file_path, out_file_path)
    # endfor
# enddef
