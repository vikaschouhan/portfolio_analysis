import pandas as pd
import itertools
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *

def process_margin_sheet(margin_xls):
    raw_sheet = pd.read_excel(margin_xls)
    raw_sheet = raw_sheet[['Contract', 'NRML Margin', 'NRML Margin Rate']]
    cols_c    = raw_sheet['Contract'].apply(lambda x: list(itertools.chain(*[x.split('*') \
                    for x in x.replace('Lot size', '').replace('MWPL', '').replace('%', '').split('\n')]))[1:])
    ctrct_df  = pd.DataFrame(cols_c.to_list(), columns=['Ticker', 'Expiry', 'Lot size', 'MWPL'])
    final_df  = pd.concat((raw_sheet, ctrct_df), axis=1)
    final_df  = final_df[['Ticker', 'Expiry', 'Lot size', 'NRML Margin', 'NRML Margin Rate', 'MWPL']]
    final_df  = final_df.set_index('Ticker')
    return final_df
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--fno_xls',     help='Raw sheet', type=str, default=None)
    parser.add_argument('--out_xls',     help='Output sheet', type=str, default=None)
    args    = parser.parse_args()

    raw_sheet = rp(args.__dict__['fno_xls'])
    out_sheet = rp(args.__dict__['out_xls'])

    if raw_sheet is None or out_sheet is None:
        print('All arguments required.')
        sys.exit(-1)
    # endif

    final_df = process_margin_sheet(raw_sheet)
    final_df.to_excel(out_sheet)
# endif
