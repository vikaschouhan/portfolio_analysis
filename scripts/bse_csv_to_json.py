#!/usr/bin/env python

import argparse
import re
import csv
import json

if __name__ == '__main__':
    """bsefile is the actual csv file which we get from bseindia.com"""

    bse_scrip_list   = []
    exclude_list     = []
    include_list     = [ "A", "B", "S", "T", "TS", "Z" ]

    # Parser
    parser           = argparse.ArgumentParser()
    parser.add_argument("--outfile",   help="Output json file",            type=str, required=True)
    parser.add_argument("--csvfile",   help="bse bhavcopy csv file",       type=str, required=True)

    args             = parser.parse_args()
    bsefile          = open(args.csvfile, "r")
    bsefile_data     = csv.reader(bsefile)

    # Populate scrip information from bse database
    for item in bsefile_data:
        bse_group    = item[2].replace(" ", "")
        #if bse_group in include_list and bse_group not in exclude_list:
        bse_scrip_list.append(item)
        # endif
    # endfor

    # Write to json file
    json.dump(bse_scrip_list, open(args.outfile, "w"), indent=8)

    bsefile.close()
# endif
