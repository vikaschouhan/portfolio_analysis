#!/usr/bin/env python
from   modules.invs_core import option_table
from   tabulate import tabulate
import argparse
import sys
##
if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--symbol',      help='OPTION symbol', type=str, default=None)
    parser.add_argument('--month',       help='Month (0 is latest, 1 is next and 2 is next of next.', type=int, default=0)
    parser.add_argument('--instrument',  help='Instrument type (OPTSTK for stock, OPTIDX for indices).', type=int, default=None)
    parser.add_argument('--outfile',     help='Output file (csv).If none passed table is displayed on console.', type=str, default=None)
    args    = parser.parse_args()

    symbol = args.__dict__['symbol']
    month  = args.__dict__['month']
    instr  = args.__dict__['instrument']
    outf   = args.__dict__['outfile']

    if symbol == None:
        print('--symbol is mandatory.')
        sys.exit(-1)
    # endif
    option_tbl_data, option_tbl_hdr = option_table(symbol=symbol, month=month, instrument=instr)
    #print(option_tbl_data)
    if outf:
        print('Saving in {}'.format(outf))
        with open(outf, 'w') as f_out:
            f_out.write(','.join([str(x) for x in option_tbl_hdr]) + '\n')
            for item_t in option_tbl_data:
                f_out.write(','.join([str(x) for x in item_t]) + '\n')
            # endfor
        # endwith
    else:
        print(tabulate(option_tbl_data, headers=option_tbl_hdr))
    # endif
# endif
