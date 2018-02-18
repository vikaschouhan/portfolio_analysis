import sys
import argparse
import pandas as pd

def gen_congest_levels(init_level, level_diff, num_levels):
    n_l_h = int(num_levels/2)
    be_l  = []
    ab_l  = []
    for i in range(1, n_l_h+1):
        be_l.append(init_level - i*level_diff)
        ab_l.append(init_level + i*level_diff)
    # endfor
    # Sort below list
    be_l.sort()
    full_l = be_l + [init_level] + ab_l
    return pd.Series(full_l)
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--ilevel',    help='Input level', type=float, default=None)
    parser.add_argument('--diff',      help='Level Difference', type=float, default=None)
    parser.add_argument('--count',     help='Number of levels to calculate', type=int, default=None)
    args    = parser.parse_args()

    if args.__dict__['ilevel'] == None or args.__dict__['diff'] == None or args.__dict__['count'] == None:
        print 'All options (--ilevel, --diff, --count) are mandatory !!'
        sys.exit(-1)
    # endif

    levels_s = gen_congest_levels(args.__dict__['ilevel'], args.__dict__['diff'], args.__dict__['count'])
    print levels_s
# endif
