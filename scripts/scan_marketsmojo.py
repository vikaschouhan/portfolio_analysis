#/usr/bin/env python
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# This script pulls some data (right now only a few) from marketsmojo.com using a search pattern
# (may be company's scrip id or code or name etc). Will add more info to display in future


import argparse
import pprint
import sys
from   modules import invs_core

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument("--scrip",    help="Scrip to be searched for.", type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["scrip"]:
        print "--scrip is required !!"
        sys.exit(-1)
    # endif

    search_results = invs_core.pull_info_from_marketsmojo(args.__dict__["scrip"])
    pprint.pprint(search_results, indent=4)
# endif
