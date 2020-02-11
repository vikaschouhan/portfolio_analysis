#!/usr/bin/env python3
from   tabulate import tabulate
import argparse
import sys, os
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.core import option_historical
##

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--symbol',      help='OPTION symbol', type=str, default=None)
    parser.add_argument('--month',       help='Month (0 is latest, 1 is next and 2 is next of next.', type=int, default=0)
    parser.add_argument('--option_type', help='Option type (PE, CE).', type=str, default=None)
    parser.add_argument('--instrument',  help='Instrument type (OPTSTK for stock, OPTIDX for indices).', type=str, default=None)
    parser.add_argument('--outfile',     help='''Output file (csv).If none passed table is displayed on console.
                                               Use --outfile=open to open with default application''', type=str, default=None)
    parser.add_argument('--verbose',     help='Verbose mode', action='store_true')
    args    = parser.parse_args()

    symbol = args.__dict__['symbol']
    otype  = args.__dict__['option_type']
    month  = args.__dict__['month']
    instr  = args.__dict__['instrument']
    outf   = args.__dict__['outfile']
    debug  = args.__dict__['verbose']

    if symbol == None:
        print('--symbol is mandatory.')
        sys.exit(-1)
    # endif
    if otype == None:
        print('--option_type is mandatory.')
        sys.exit(-1)

    # This is a dataframe
    option_tbl = option_historical(symbol=symbol, option_type=otype, month=month, instrument=instr, verbose=debug)

    if outf == 'open':
        tmp_file = '/tmp/____tmp.csv'
        print('Saving in {}'.format(tmp_file))
        subprocess.call(['xdg-open', tmp_file])
    elif outf:
        print('Saving in {}'.format(outf))
        option_tbl.to_csv(outf)
    else:
        print(tabulate(option_tbl, headers='keys'))
    # endif
# endif
