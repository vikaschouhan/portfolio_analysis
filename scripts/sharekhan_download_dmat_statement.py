# Author  : Vikas Chouhan
# License : GPLv2

import os, sys
import spynner
import time
import argparse
import datetime

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31"

def download_sharekhan_dp_statement(login_id, br_passwd, tr_passwd, file_name='~/sharekhan_mydp.xls', gen_report=True, brshow=False, timeout=60):
    login_url = 'https://newtrade.sharekhan.com/rmmweb/login/LoginPage.jsp'
    dmat_url  = 'https://newtrade.sharekhan.com/rmmweb/statements/excel/eq_dpsr_report.jsp?balance=-1'
    dmat_lurl = 'https://newtrade.sharekhan.com/rcs.sk?execute=dynamicreport&pType=905'
    browser = spynner.browser.Browser(user_agent=user_agent)
    
    if brshow:
        browser.show()
    # endif

    browser.load(login_url, load_timeout=timeout)
    browser.wk_fill('input[name=loginid]', login_id)
    browser.wk_fill('input[name=brpwd]', br_passwd)
    browser.wk_fill('input[name=trpwd]', tr_passwd)
    browser.wk_click('input[name=Login]', wait_load=True)

    # WTF (sometime the dmat statement simply doesn't load, I don't know
    # anything else besides waiting !!)
    browser.load(dmat_lurl, load_timeout=60)
    #time.sleep(sleep_time)

    # Get dmat statement file & close the browser
    bin_file = browser.download(dmat_url)
    browser.close()

    if gen_report:
        with open(os.path.expanduser(file_name), 'w') as f_out:
            f_out.write(bin_file)
        # endwith
        return 'Report downloaded to {} !!'.format(file_name)
    else:
        # Get header and rows fro xls data
        # TODO
        from bs4 import BeautifulSoup
        soup_t = BeautifulSoup(bin_file, 'lxml')
        table_t = soup_t.find('table', {'border':1})
        row_l = table_t.find_all('tr')
        # Pop last row as it's some useless information
        row_l.pop(-1)
        # Pop header
        header_r = row_l.pop(0)
        header_l = [x.text for x in header_r.find_all('td')]
        # Extract rows
        scrip_l = []
        for r_t in row_l:
           scrip_l.append([x.text.replace('\t', '').replace('\r', '').replace('\n', '') for x in r_t.find_all('td')])
        # endfor
        return scrip_l, header_l
    # endif
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--auth',     help='Sharekhan Authentication (loginid,brpwd,trpwd)', type=str, default=None)
    parser.add_argument('--filename', help='Target filename', type=str, default=None)
    parser.add_argument('--genrep',   help='Generate Report', action='store_true')
    parser.add_argument('--brshow',   help='Browser show', action='store_true')
    parser.add_argument('--timeout',  help='Page load timeout', type=int, default=60)
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
    print download_sharekhan_dp_statement(auth_l[0], auth_l[1], auth_l[2], \
              file_name, args.__dict__['genrep'], args.__dict__['brshow'], args.__dict__['timeout'])
# endif
