#!/usr/bin/env python2
# screener.in apis have changed. There is no longer an /api/ endpoint,
# no longer a json transfer. This new script was written for the new api changes

import selenium.webdriver
import selenium.common
import time
from   bs4 import BeautifulSoup
import os
import argparse
import sys

def rp(x):
    return os.path.expanduser(x)
# enddef

def screener_in_populate_company_list(user, passwd, screener_url='/23210/walter-schloss', csv_report_file=None):
    if csv_report_file == None:
        csv_report_file = rp('~/') + '_'.join(screener_url.split('/')) + '.csv'
    else:
        csv_report_file = rp(csv_report_file)
    # endif

    print('Using screen {}'.format(screener_url))
    print('Using csv report file {}'.format(csv_report_file))

    login_url = 'https://www.screener.in/login/'
    options = selenium.webdriver.ChromeOptions()
    driver  = selenium.webdriver.Chrome(options=options)
    
    # Login
    driver.get(login_url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="id_username"]').send_keys(user)
    driver.find_element_by_xpath('//*[@id="id_password"]').send_keys(passwd)
    driver.find_element_by_xpath('//*[@id="main-area"]/form/p[1]/button').click()
    
    page_no = 1
    company_list = []
    
    while True:
        screener_url_p = 'https://www.screener.in/screens/' + screener_url + '/?page={}'.format(page_no)
        driver.get(screener_url_p)
        time.sleep(1)
    
        try:
            table = driver.find_element_by_tag_name('table')
        except selenium.common.exceptions.NoSuchElementException:
            break
        # endtry
    
        page_source = driver.page_source
        html_page   = BeautifulSoup(page_source, 'html.parser')
        html_table  = html_page.find('table')
        table_rows  = html_table.find_all('tr')
        for row_t in table_rows:
            table_columns = row_t.find_all('td')
            if len(table_columns) == 0:
                continue
            # endif
    
            company_name = table_columns[1].text.replace('\t', '').replace('\n', '').lstrip().rstrip()
            company_code = table_columns[1].find('a').attrs['href'].split('/')[2]
            company_list.append((company_code, company_name))
        # endfor
    
        page_no = page_no + 1
    # endwhile
    
    driver.close()
    
    # Write csv file
    print('Writing to {}'.format(csv_report_file))
    with open(csv_report_file, 'w') as f_out:
        f_out.write('sym_name_list\n')
        f_out.write('#Symbol, Name\n')
        for item_t in company_list:
            f_out.write('{},{}\n'.format(item_t[0], item_t[1]))
        # endfor
    # endwith

    #return company_list
# enddef

if __name__ == '__main__':
    default_screen_url = '/17942/Growth-PE-Screener/'

    parser  = argparse.ArgumentParser()
    parser.add_argument("--auth",           help="Screener.in authentication in form user,passwd", type=str, default=None)
    parser.add_argument("--screen_url",     help="Screen's url", type=str, default=None)
    parser.add_argument("--report_file",    help="Csv report file.", type=str, default='~/screener_in_report.csv')
    args    = parser.parse_args()

    if not args.__dict__["auth"]:
        print("--auth is required !!")
        sys.exit(-1)
    # endif
    if not args.__dict__["screen_url"] == None:
        print("--screen_url is None. Using default value {}".format(default_screen_url))
        screen_url = default_screen_url
    else:
        screen_url = default_screen_url
    # endif

    auth_info  = args.__dict__["auth"].replace(' ', '').split(',')

    # Call scrappper
    screener_in_populate_company_list(auth_info[0], auth_info[1], screener_url=screen_url, csv_report_file=args.__dict__["report_file"])
# endif
