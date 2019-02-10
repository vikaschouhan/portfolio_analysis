# Author  : Vikas Chouhan (presentisgood@gmail.com
# License : GPLv2

import os
import sys
from   bs4 import BeautifulSoup
import csv
import datetime
import argparse
import time
from   selenium import webdriver

def download_zerodha_dp_statement(user_name, password, questions_dict, file_name='~/zerodha_dp_statement.csv', gen_report=True, brshow=False):
    #print questions_dict

    row_l    = []
    login_url  = 'https://kite.zerodha.com'
    base_url   = 'https://q.zerodha.com/'
    hold_url   = 'https://q.zerodha.com/holdings/display/'

    options = webdriver.ChromeOptions()
    if not brshow:
        options.add_argument('headless')
    # endif
    driver = webdriver.Chrome(chrome_options=options)

    # Login
    driver.get(login_url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[2]/input').send_keys(user_name)
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[3]/input').send_keys(password)
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[4]/button').click()
    time.sleep(2)
    
    # Questions page
    # Assuming only two questions
    ques1 = str(driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[2]/div/label').text)
    ques2 = str(driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[3]/div/label').text)
    if ques1 not in questions_dict :
        print('Answer to question "{}" is not present in Zerodha Questions.'.format(ques1))
        driver.close()
        sys.exit(-1)
    # endif
    if ques2 not in questions_dict :
        print('Answer to question "{}" is not present in Zerodha Questions.'.format(ques1))
        driver.close()
        sys.exit(-1)
    # endif

    # Answer
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[2]/div/input').send_keys(questions_dict[ques1])
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[3]/div/input').send_keys(questions_dict[ques2])

    # Click continue button
    driver.find_element_by_xpath('//*[@id="container"]/div/div/div/form/div[4]/button').click()

    # Goto backoffice page
    driver.get(base_url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="login"]/div/center/a').click()

    # Goto holdings
    driver.get(hold_url)
    time.sleep(1)
    browser_html = driver.page_source

    while True:
        html_page = BeautifulSoup(browser_html, 'html.parser')
        hld_table = html_page.find('table', {'id' : 'holdings-table'})
        header_l  =  [ x.text for x in hld_table.find('tr').find_all('th') ]

        # Go over all the rows
        for item_this in hld_table.find('tbody').find_all('tr'):
            row_l.append([ x.text.replace('\t', '').replace('\n', '').replace('?', '') for x in item_this.find_all('td')])
        # endfor

        next_btn = html_page.find('a', {'id' : 'holdings-table_next'})
        if next_btn.attrs['class'][2] != 'disabled':
            print('On page {} \n'.format(next_btn.attrs['tabindex']))
            driver.find_element_by_xpath('//*[@id="holdings-table_next"]')
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
        print('Writing report file to {}'.format(file_name))
        with open(os.path.expanduser(file_name), 'w') as f_out:
            csv_writer = csv.writer(f_out, delimiter=',')
            csv_writer.writerow(header_l)
            for item_this in row_l:
                csv_writer.writerow(item_this)
            # endfor
        # endwith
        return 'Report downloaded to {}'.format(file_name)
    else:
        return row_l, header_l
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
