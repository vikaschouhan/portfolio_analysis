#!/usr/bin/env python3
import argparse
import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules import parsers as invs_parsers
from   modules import utils as invs_utils

# Main
if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--sfile',      help='Security csv file. Can be list file or bhavcopy file.', type=str, default=None)
    parser.add_argument('--suffix',     help='Suffix(s) to add to code names.Useful to generate workspace file for futures.', type=str, default='')
    parser.add_argument('--ofile',      help='Output file name.', type=str, default='~/fo.workspace')
    args    = parser.parse_args()

    if args.__dict__['sfile'] == None:
        print('--sfile required !!')
        sys.exit(-1)
    # endif

    suff_list = args.__dict__['suffix'].split(',') if args.__dict__['suffix'] else ['']
    out_file  = invs_utils.rp(args.__dict__['ofile'])
    sec_file  = invs_utils.rp(args.__dict__['sfile'])

    ofile_hdr = 'Symbols'
    ofile_ftr = 'ColumnList\n1,0,94;1,3,69;1,4,64;1,5,58;1,6,64;1,7,63;0,8,100;1,9,64;1,10,61;1,11,64;1,12,65;1,1,67;1,13,63;1,14,68;0,15,100;0,16,100;0,17,100;0,18,100;1,19,67;1,20,67;0,21,100;0,22,100;0,23,100;0,24,100;0,25,100;0,26,100;0,27,100;0,28,100;0,29,100;0,30,100;0,31,100;0,32,100;1,33,100;1,34,83;1,2,100;\nCharts'

    sec_list = invs_parsers.populate_sec_list(sec_file)

    code_list = []
    for sec_t in sec_list:
        for suffx_t in suff_list:
            code_list.append(sec_t['code'] + suffx_t)
        # endfor
    # endfor

    # Write to workspace file
    print('Writing to {}'.format(out_file))
    with open(out_file, 'w') as ofile_hndl:
        ofile_hndl.write(ofile_hdr)
        ofile_hndl.write('\n')
        ofile_hndl.write('\n'.join(code_list))
        ofile_hndl.write('\n')
        ofile_hndl.write(ofile_ftr)
    # endwith
# enddef
