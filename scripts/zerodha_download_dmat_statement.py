# Author  : Vikas Chouhan (presentisgood@gmail.com
# License : GPLv2

import os
import sys
from   bs4 import BeautifulSoup
import csv
import datetime
import argparse
import time
import shutil
import pandas as pd
from   selenium import webdriver

def download_zerodha_dp_statement(user_name, user_pwd, user_pin, file_name='~/zerodha_dp_statement.csv', gen_report=True, brshow=True):
    #print questions_dict

    row_l    = []
    login_url  = 'https://kite.zerodha.com'
    hold_url   = 'https://kite.zerodha.com/holdings'

    down_dir  = '/tmp/chrome-downloads'

    options = webdriver.ChromeOptions()
    if not brshow:
        options.add_argument('headless')
    # endif
    options.add_experimental_option("prefs", {
        "download.default_directory"       : down_dir,
        "download.prompt_for_download"     : False,
        "download.directory_upgrade"       : True,
    })

    driver = webdriver.Chrome(chrome_options=options)

    # Create dir
    try:
        os.makedirs(down_dir)
    except:
        shutil.rmtree(down_dir)
        os.makedirs(down_dir)
    # endtry

    # Login
    driver.get(login_url)
    time.sleep(2)

    # Enter username/password
    input_fields = driver.find_elements_by_tag_name('input')
    input_fields[0].send_keys(user_name)
    input_fields[1].send_keys(user_pwd)
    # Click
    driver.find_element_by_tag_name('button').click()
    time.sleep(4)

    # Enter PIN
    input_field = driver.find_element_by_tag_name('input')
    input_field.send_keys(user_pin)
    driver.find_element_by_tag_name('button').click()
    time.sleep(3)

    # Go to holdings page
    driver.get(hold_url)
    time.sleep(6)
    # Click download holdings report
    driver.find_element_by_class_name('download').click()
    time.sleep(2)

    # Close driver
    driver.close()

    # Filename
    bin_file = '{}/holdings.csv'.format(down_dir)

    # Check if file was downloaded
    if not os.path.isfile(bin_file):
        print('{} does not exist !!. Download failed.'.format(bin_file))
        sys.exit(-1)
    # endif
    
    if gen_report:
        print('Writing report file to {}'.format(file_name))
        with open(os.path.expanduser(file_name), 'wb') as f_out:
            f_out.write(open(bin_file, 'rb').read())
        # endwith
        return 'Report downloaded to {} !!'.format(file_name)
    else:
        data_frame = pd.read_csv(bin_file, header=0)
        header_l   = list(data_frame.keys())
        # Extract rows
        scrip_l = []
        for i_t, r_t in data_frame.iterrows():
           scrip_l.append(list(r_t))
        # endfor

        # Remove dir
        shutil.rmtree(down_dir)

        return scrip_l, header_l
    # endif
# enddef

#if __name__ == '__main__':
#    parser  = argparse.ArgumentParser()
#    parser.add_argument('--auth',     help='Zerodha Authentication (username,password)', type=str, default=None)
#    parser.add_argument('--filename', help='Target filename', type=str, default=None)
#    parser.add_argument('--genrep',    help='Generate Report', action='store_true')
#    args    = parser.parse_args()
#
#    if not args.__dict__['auth']:
#        print '--auth is required !!'
#        sys.exit(-1)
#    # endif
#    if not args.__dict__['filename']:
#        file_name = '~/zerodha_mydp_statement_{}.csv'.format(str(datetime.datetime.now()))
#    else:
#        file_name = args.__dict__['filename']
#    # endif
#
#    auth_l = args.__dict__['auth'].replace(' ', '').split(',')
#    if len(auth_l) != 2:
#        print '--auth should be in format "username,password"'
#        sys.exit(-1)
#    # endif
#
#    # Download
#    print download_zerodha_dp_statement(auth_l[0], auth_l[1], file_name, args.__dict__['genrep'])
## endef
