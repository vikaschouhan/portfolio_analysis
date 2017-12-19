# Author  : Vikas Chouhan
# License : GPLv2

import os, sys
import spynner
import time
import argparse
import datetime

def download_sharekhan_dp_statement(login_id, br_passwd, tr_passwd, file_name='~/sharekhan_mydp.xls', gen_report=True):
    login_url = 'https://newtrade.sharekhan.com/rmmweb/login/LoginPage.jsp'
    dmat_url  = 'https://newtrade.sharekhan.com/rmmweb/statements/excel/eq_dpsr_report.jsp?balance=-1'
    browser = spynner.browser.Browser()
    browser.load(login_url, load_timeout=60)

    browser.wk_fill('input[name=loginid]', login_id)
    browser.wk_fill('input[name=brpwd]', br_passwd)
    browser.wk_fill('input[name=trpwd]', tr_passwd)
    browser.wk_click('input[name=Login]', wait_load=True)

    bin_file = browser.download(dmat_url)
    browser.close()

    if gen_report:
        with open(os.path.expanduser(file_name), 'w') as f_out:
            f_out.write(bin_file)
        # endwith
        return None
    else:
        # Get header and rows fro xls data
        # TODO
        #return row_l, header_l
        return None
    # endif
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--auth',     help='Sharekhan Authentication (loginid,brpwd,trpwd)', type=str, default=None)
    parser.add_argument('--filename', help='Target filename', type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__['auth']:
        print '--auth is required !!'
        sys.exit(-1)
    # endif
    if not args.__dict__['filename']:
        file_name = '~/sharekhan_mydp_statement_{}.xls'.format(str(datetime.datetime.now()))
    else:
        file_name = args.__dict__['filename']
    # endif

    auth_l = args.__dict__['auth'].replace(' ', '').split(',')
    if len(auth_l) != 3:
        print '--auth should be in format "loginid,brpwd,trpwd"'
        sys.exit(-1)
    # endif

    # Download
    download_sharekhan_dp_statement(auth_l[0], auth_l[1], auth_l[2], file_name)
# endif
