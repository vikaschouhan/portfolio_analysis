#!/usr/bin/env python

import datetime
import re
import requests
import pandas
import json
import sys
import glob
import argparse
import csv
import pprint
#from   packages.core.utils import *

def list_to_float(L):
    return [float(str(x).replace(',','')) if x != '' else 0.0 for x in L]
def list_to_int(L):
    return [int(str(x).replace(',','')) if x != '' else 0.0 for x in L]
def cast_list(L, target_type):
    if target_type == int:
        return list_to_int(L)
    elif target_type == float:
        return list_to_float(L)
    else:
        return None

def parse_morningstar_csv(csv_file):
    this_dict      = {}
    curr_key       = None
    csv_obj        = csv.reader(open(csv_file, 'r'), delimiter=',')

    # Skip first line
    csv_obj.next()

    list_this                  = csv_obj.next()        # 'Financials'
    list_this                  = csv_obj.next()        # Dates list
    curr_key                   = "financials"
    this_dict[curr_key]        = {}
    this_dict["date_list"]     = list_this[1:]
    # next 15 lists are actual data for the financials
    for i in range(0, 15):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Key Ratios -> Profitability'
    list_this                  = csv_obj.next()        # 'Margins % of sales'
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 9 lists are actual data for this
    for i in range(0, 9):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Profitability
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 8 lists are actual data for the profitability tab
    for i in range(0, 8):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Key Ratios Growth'
    list_this                  = csv_obj.next()        # Dates

    list_this                  = csv_obj.next()        # 'Revenue %'
    curr_key                   = "Revenue Growth %"
    this_dict[curr_key]        = {}
    # next 4 items
    for i in range(0, 4):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # 'Operating Income %'
    curr_key                   = "Operating Income Growth %"
    this_dict[curr_key]        = {}
    # next 4 items
    for i in range(0, 4):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # 'Net Income %'
    curr_key                   = "Net Income Growth %"
    this_dict[curr_key]        = {}
    # next 4 items
    for i in range(0, 4):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # 'EPS %'
    curr_key                   = "EPS Growth %"
    this_dict[curr_key]        = {}
    # next 4 items
    for i in range(0, 4):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Key Ratios -> Cash Flow'
    list_this                  = csv_obj.next()        # 'Cash Flow Ratios'
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 5 lists are actual data for this
    for i in range(0, 5):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Key Ratios -> Financial Health'
    list_this                  = csv_obj.next()        # 'Balance Sheet Items (in %)'
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 20 lists are actual data for this
    for i in range(0, 20):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Liquidity/Financial Health'
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 4 lists are actual data for this
    for i in range(0, 4):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    list_this                  = csv_obj.next()        # Blank line
    list_this                  = csv_obj.next()        # 'Key Ratios -> Efficiency Ratios'
    list_this                  = csv_obj.next()        # 'Efficiency'
    curr_key                   = list_this[0]
    this_dict[curr_key]        = {}
    # next 8 lists are actual data for this
    for i in range(0, 8):
        list_this                         = csv_obj.next()
        this_dict[curr_key][list_this[0]] = cast_list(list_this[1:], float)
    # endfor

    return this_dict


if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument("--out_file",   help="output price/volume json file",     type=str, default=None)
    parser.add_argument("--in_file",    help="input bse_code_list json file",     type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["out_file"]:
        print "--out_file is required !!"
        sys.exit(-1)
    # endif
    if not args.__dict__["in_file"]:
        print "--in_file is required !!"
        sys.exit(-1)
    # endif

    pprint.pprint(parse_morningstar_csv(args.__dict__["in_file"]))
# endif
