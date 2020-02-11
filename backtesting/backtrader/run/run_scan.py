#!/usr/bin/env python3
import argparse
import json
import os, sys
from   common import run_scanner_main, check_config

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--config_file',    help='json config file', type=str, default=None)
    parser.add_argument('--override',       help='override json params', type=str, default=None)
    args = parser.parse_args()

    if not args.__dict__['config_file']:
        print('--config_file is required !!')
        sys.exit(-1)
    # endif

    config_file = args.__dict__['config_file']
    config_json = json.load(open(config_file, 'r'))
    override    = args.__dict__['override']

    args_dict   = {}
    if override:
        try:
            args_dict = dict([x.split('=') for x in override.split(';')])
        except:
            print('args {} not in proper format'.format(override))
            sys.exit(-1)
        # endtry
    # endif

    # Checks
    check_config(config_json)

    # Ovveride
    config_json = {**config_json, **args_dict}
    print(config_json)

    # Invoke scanner
    run_scanner_main(config_json)
# enddef
