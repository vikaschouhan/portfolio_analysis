#!/usr/bin/env python

import argparse
import glob
import os
import json
import sys

parser  = argparse.ArgumentParser()
parser.add_argument("--in_dir",   help="input repository directory.",   type=str, default=None)
parser.add_argument("--out_dir",  help="output repository directory.",  type=str, default=None)
args    = parser.parse_args()

if not args.__dict__["in_dir"]:
    print "--in_dir is required !!"
    sys.exit(-1)
# endif
if not args.__dict__["out_dir"]:
    print "--out_dir is required !!"
    sys.exit(-1)
# endif

src_dir = args.__dict__["in_dir"]
dst_dir = args.__dict__["out_dir"]

if src_dir == dst_dir:
    print "--in_dir and --out_dir should not be same !!"
    sys.exit(-1)
# endif

f_list = [f for f in os.listdir(src_dir) if f.endswith('.json')]

for f_this in f_list:
    j_this = json.load(open(src_dir + "/" + f_this, "r"))
    j_this.pop("announcement_set")
    j_this.pop("annualreport_set")
    j_this.pop("companyrating_set")
    j_this["warehouse_set"].pop("analysis")
    j_this["warehouse_set"].pop("current_price")
    j_this["warehouse_set"].pop("high_price")
    j_this["warehouse_set"].pop("low_price")
    j_this["warehouse_set"].pop("market_capitalization")

    json.dump(j_this, open(dst_dir + "/" + f_this, "w"), indent=8)
# endfor
