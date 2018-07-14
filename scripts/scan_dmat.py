# Author  : Vikas Chouhan (presentisgood@gmail.com
# License : GPLv2

import os
import sys
from   bs4 import BeautifulSoup
import csv
import datetime
import argparse
import ConfigParser

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

from   sharekhan_download_dmat_statement import download_sharekhan_dp_statement
#from   zerodha_download_dmat_statement import download_zerodha_dp_statement
#
#def get_zerodha_data(config):
#    login_data = dict(config.items(section='Zerodha'))
#    if 'user_name' not in login_data.keys() or 'passwd' not in login_data.keys():
#        print 'Zerodha section should have keys : user_name and passwd'
#        sys.exit(-1)
#    # endif
#
#    print 'Pulling dmat data from zerodha !!'
#    data = download_zerodha_dp_statement(login_data['user_name'], login_data['passwd'], gen_report=False)
#    return data
## enddef

def get_sharekhan_data(config):
    login_data = dict(config.items(section='Sharekhan'))
    if 'user_name' not in login_data.keys() or 'br_passwd' not in login_data.keys() or \
                'tr_passwd' not in login_data.keys():
        print 'Sharekhan section should have keys : user_name and passwd'
        sys.exit(-1)
    # endif

    print 'Pulling data from sharekhan !!'
    data = download_sharekhan_dp_statement(login_data['user_name'], login_data['br_passwd'], login_data['tr_passwd'], gen_report=False)
    return data
# enddef

def get_scrips_list(config_file):
    print 'Using config file {}'.format(config_file)

    # parse config_file
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    en_sh  = False if 'Sharekhan' not in config.sections() else True
    en_ze  = False if 'Zerodha' not in config.sections() else True

    scrips_l = []
    # Try sharekhan if available
    try:
        if en_sh:
            sh_data, sh_hdr = get_sharekhan_data(config)
            for item_t in sh_data:
                scrips_l.append(item_t[1])
            # endfor
        # endif
    except:
        print 'Sharekhan timeout !!'
    # endtry
    # Try zerodha if available
    try:
        if en_ze:
            #ze_data, ze_hdr = get_zerodha_data(config)
            #for item_t in ze_data:
            #    scrips_l.append(item_t[1])
            ## endfor
            print 'Zerodha Q backoffice login has changed. Thus our old login menthod no longer works !! It will be supported in future.'
        # endif
    except:
        print 'Zerodha timeout !!'
    # endtry

    return scrips_l 
# enddef

if __name__ == '__main__':
    # config_file
    config_file = '~/.dmat.cfg'
    config_file = os.path.expanduser(config_file)
    # Target file
    output_file = '~/dmat_sym_name_list.csv'
    output_file = os.path.expanduser(output_file)

    # Check if config_file is present
    if not os.path.isfile(config_file):
        print '{} is not present. Ensure that this file is there with proper configuration data !!'.format(config_file)
        sys.exit(-1)
    # endif

    scrips_l = get_scrips_list(config_file)
    print 'Security List populated = {}'.format(scrips_l)

    print 'Writing report to {}'.format(output_file)
    with open(output_file, 'w') as f_out:
        f_out.write('sym_name_list\n')
        f_out.write('#Symbol, Name\n')
        for item_t in scrips_l:
            f_out.write('{},{}\n'.format(item_t, item_t))
        # endfor
    # endwith
# endef
