#!/usr/bin/env python
import pandas as pd
import argparse
import sys

sys.path.append('.')
from   modules.utils import *

if __name__ == '__main__':
    # Parser
    parser           = argparse.ArgumentParser()
    parser.add_argument("--infile",   help="Input csv file",        type=str, required=True)
    parser.add_argument("--outfile",  help="Output txt file",       type=str, required=True)

    args             = parser.parse_args()
    fo_file          = rp(args.__dict__['infile'])
    wl_file          = rp(args.__dict__['outfile'])

    df_fo  = pd.read_csv(fo_file, sep='\s*,\s*')
    df_fo  = df_fo[df_fo['UNDERLYING'].apply(lambda x: 'Derivatives' not in x)] # Filter one row starts with "Derivatives"
    syms   = df_fo['SYMBOL'].apply(lambda x: x.replace('&', '_').replace('-', '_'))
    syms_l = ','.join(syms.apply(lambda x: 'NSE:' + x))

    # Write to file
    with open(wl_file, 'w') as wf:
        print('>> Generating tradingview watchlist for f&o to {}'.format(wl_file))
        wf.write(syms_l)
    # endwith
# endif
