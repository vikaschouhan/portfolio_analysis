# Author  : Vikas Chouhan (presentisgood@gmail.com
# License : GPLv2

import spynner
import os
import sys
from   bs4 import BeautifulSoup
import csv
import datetime
import argparse

def download_zerodha_dp_statement(user_name, password, file_name='~/zerodha_dp_statement.csv', gen_report=True):
    row_l    = []
    browser  = spynner.browser.Browser()
    base_url = 'https://q.zerodha.com/'
    hold_url = 'https://q.zerodha.com/holdings/display/'
    browser.load(base_url)

    browser.wk_fill('input[name=username]', 'YC8500')
    browser.wk_fill('input[name=password]', 'system#001')
    browser.wk_click('input[value=Login]', wait_load=True)

    browser.load(hold_url, load_timeout=60)

    while True:
        html_page = BeautifulSoup(browser.html, 'html.parser')
        hld_table = html_page.find('table', {'id' : 'holdings-table'})
        header_l  =  [ x.text for x in hld_table.find('tr').find_all('th') ]

        # Go over all the rows
        for item_this in hld_table.find('tbody').find_all('tr'):
            row_l.append([ x.text.replace('\t', '').replace('\n', '').replace('?', '') for x in item_this.find_all('td')])
        # endfor

        next_btn = html_page.find('a', {'id' : 'holdings-table_next'})
        if next_btn.attrs['class'][2] != 'disabled':
            print 'On page {} \n'.format(next_btn.attrs['tabindex'])
            browser.wc_click('input[id=holdings-table_next]', wait_load=True)
        else:
            break
        # endif
    # endwhile
   
    # NOTE: On enabling these, spynner is throwing some error like
    #        >> AttributeError: 'Browser' object has no attribute 'manager' 
    #       Disabling for now
    #browser.destroy_webview() 
    #browser.close()

    if gen_report:
        print 'Writing report file to {}'.format(file_name)
        with open(os.path.expanduser(file_name), 'w') as f_out:
            csv_writer = csv.writer(f_out, delimiter=',')
            csv_writer.writerow(header_l)
            for item_this in row_l:
                csv_writer.writerow(item_this)
            # endfor
        # endwith
        return None
    else:
        return row_l, header_l
    # endif
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--auth',     help='Zerodha Authentication (username,password)', type=str, default=None)
    parser.add_argument('--filename', help='Target filename', type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__['auth']:
        print '--auth is required !!'
        sys.exit(-1)
    # endif
    if not args.__dict__['filename']:
        file_name = '~/zerodha_mydp_statement_{}.csv'.format(str(datetime.datetime.now()))
    else:
        file_name = args.__dict__['filename']
    # endif

    auth_l = args.__dict__['auth'].replace(' ', '').split(',')
    if len(auth_l) != 2:
        print '--auth should be in format "username,password"'
        sys.exit(-1)
    # endif

    # Download
    download_zerodha_dp_statement(auth_l[0], auth_l[1], file_name)
# endef
