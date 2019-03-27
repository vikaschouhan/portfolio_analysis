#!/usr/bin/env python3
# Author  : Vikas Chouhan (presentisgood@gmail.com
# License : GPLv2

import os
import sys
from   bs4 import BeautifulSoup
import csv
import datetime
import argparse
from   configparser import ConfigParser
from   modules.invs_utils import rp, cdir

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

from   sharekhan_download_dmat_statement import download_sharekhan_dp_statement
from   zerodha_download_dmat_statement import download_zerodha_dp_statement
#
def get_zerodha_data(config):
    login_data = dict(config.items(section='Zerodha'))
    if 'user_name' not in login_data.keys() or 'user_passwd' not in login_data.keys() or \
            'user_pin' not in login_data.keys():
        print('Zerodha section should have keys : user_name, user_passwd & user_pin')
        sys.exit(-1)
    # endif

    print('Pulling dmat data from zerodha !!')
    data = download_zerodha_dp_statement(login_data['user_name'], login_data['user_passwd'],
            login_data['user_pin'], gen_report=False)
    return data
# enddef

def get_sharekhan_data(config):
    login_data = dict(config.items(section='Sharekhan'))
    if 'user_name' not in login_data.keys() or 'br_passwd' not in login_data.keys() or \
                'tr_passwd' not in login_data.keys():
        print('Sharekhan section should have keys : user_name and passwd')
        sys.exit(-1)
    # endif

    print('Pulling data from sharekhan !!')
    data = download_sharekhan_dp_statement(login_data['user_name'], login_data['br_passwd'], login_data['tr_passwd'], gen_report=False)
    return data
# enddef

def get_scrips_list(config_file):
    print('Using config file {}'.format(config_file))

    # parse config_file
    config = ConfigParser()
    config.optionxform = str
    
    config.read(config_file)
    en_sh  = False if 'Sharekhan' not in config.sections() else True
    en_ze  = False if 'Zerodha' not in config.sections() else True

    scrips_l = []
    scrips_m = {}
    # Try sharekhan if available
    if en_sh:
        scrips_m['Sharekhan'] = []
        sh_data, sh_hdr = get_sharekhan_data(config)
        for item_t in sh_data:
            scrips_l.append(item_t[1])
            scrips_m['Sharekhan'].append(item_t[1])
        # endfor
    # endif
    # Try zerodha if available
    if en_ze:
        scrips_m['Zerodha'] = []
        ze_data, ze_hdr = get_zerodha_data(config)
        for item_t in ze_data:
            scrips_l.append(item_t[0])
            scrips_m['Zerodha'].append(item_t[0])
        # endfor
        #print 'Zerodha Q backoffice login has changed. Thus our old login menthod no longer works !! It will be supported in future.'
    # endif

    return scrips_l, scrips_m
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--out_dir',        help='Output directory.',        type=str, default='~/sc_db_github_files/')
    args    = parser.parse_args()

    if args.__dict__['out_dir'] == None:
        print('--out_dir is required !!')
        sys.exit(-1)
    # endif
    
    out_dir     = rp(args.__dict__['out_dir'])
    cdir(out_dir)
    # config_file
    config_file = rp('~/.dmat.cfg')
    # Target file
    output_file = '{}/dmat_sym_name_list.csv'.format(out_dir)
    out_file_sh = '{}/dmat_sym_name_sharekhan_list.csv'.format(out_dir)
    out_file_ze = '{}/dmat_sym_name_zerodha_list.csv'.format(out_dir)

    # Check if config_file is present
    if not os.path.isfile(config_file):
        print('{} is not present. Ensure that this file is there with proper configuration data !!'.format(config_file))
        sys.exit(-1)
    # endif

    scrips_l, scrips_m = get_scrips_list(config_file)
    print('Security List populated = {}'.format(scrips_l))

    def write_report(scrips_list, out_file):
        print('Writing report to {}'.format(out_file))
        with open(out_file, 'w') as f_out:
            f_out.write('sym_name_list\n')
            f_out.write('#Symbol, Name\n')
            for item_t in scrips_list:
                f_out.write('{},{}\n'.format(item_t, item_t))
            # endfor
        # endwith
    # enddef

    write_report(scrips_l, output_file)

    if 'Sharekhan' in scrips_m:
        write_report(scrips_m['Sharekhan'], out_file_sh)
    # endif
    if 'Zerodha' in scrips_m:
        write_report(scrips_m['Zerodha'], out_file_ze)
    # endif
# endef
