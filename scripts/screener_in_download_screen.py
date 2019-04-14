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
from   modules.invs_utils import rp, url_norm


def screener_in_populate_company_list(user, passwd, screener_url=None, csv_report_file=None, headless=True):
    if csv_report_file == None:
        csv_report_file = rp('~/') + '_'.join(screener_url.split('/')) + '.csv'
    else:
        csv_report_file = rp(csv_report_file)
    # endif

    print('Using csv report file {}'.format(csv_report_file))

    login_url  = 'https://www.screener.in/login/'
    screen_url = 'https://www.screener.in/screens'
    options    = selenium.webdriver.ChromeOptions()
    options.headless = headless
    driver     = selenium.webdriver.Chrome(options=options)
    
    # Login
    driver.get(login_url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="id_username"]').send_keys(user)
    driver.find_element_by_xpath('//*[@id="id_password"]').send_keys(passwd)
    driver.find_element_by_xpath('//*[@id="main-area"]/form/p[1]/button').click()

    # Try to read all screens
    list_screens = None
    panel_eles   = driver.find_elements_by_class_name('panel')
    for panel_t in panel_eles:
        if panel_t.find_element_by_class_name('title').text == 'YOUR SCREENS':
            list_screens = panel_t.find_elements_by_tag_name('li')
            break
        # endif
    # endfor

    if list_screens == None:
        print('No screens found !! Please create one or more screens on www.screener.in.')
        driver.close()
        sys.exit(-1)
    # endif

    # Open options
    list_screens_new = [(x.text, url_norm(x.find_element_by_tag_name('a').get_attribute('href'))) for x in list_screens]
    list_screen_urls = [x[1] for x in list_screens_new]
    if screener_url:
        full_screen_url = url_norm(screener_url)
        if full_screen_url not in list_screen_urls:
            print('Url {} not found. Please select one of {}'.format(full_screen_url, list_screen_urls))
            sys.exit(-1)
        # endif
    else:
        inp_choice  = None
        # Print options
        for index_t, screen_t in enumerate(list_screens_new):
            print('{}. {} ({})'.format(index_t, screen_t[0], screen_t[1]))
        # endfor
        while True:
            inp_choice  = int(input('Enter choice : '))
            if inp_choice >= 0 and inp_choice < len(list_screens_new):
                break
            # endif
            print('Wrong choice.')
        # endwhile
        full_screen_url = list_screens_new[inp_choice][1]
    # endif
    
    print('Using screener url = {}'.format(full_screen_url)) 
    page_no = 1
    company_list = []
    
    while True:
        screener_url_p = full_screen_url + '/?page={}'.format(page_no)
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
    parser  = argparse.ArgumentParser()
    parser.add_argument("--auth",           help="Screener.in authentication in form user,passwd", type=str, default=None)
    parser.add_argument("--screen_url",     help="Screen's url", type=str, default=None)
    parser.add_argument("--report_file",    help="Csv report file.", type=str, default='~/screener_in_report.csv')
    args    = parser.parse_args()

    if not args.__dict__["auth"]:
        print("--auth is required !!")
        sys.exit(-1)
    # endif

    screen_url = args.__dict__["screen_url"]
    auth_info  = args.__dict__["auth"].replace(' ', '').split(',')

    # Call scrappper
    screener_in_populate_company_list(auth_info[0], auth_info[1], screener_url=screen_url, csv_report_file=args.__dict__["report_file"])
# endif
