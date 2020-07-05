# Author   : Vikas Chouhan (presentisgood@gmail.com)
# Purpose  : Scrape public token id from zerodha kite.

from   seleniumwire import webdriver
import time
import argparse
import sys

def scrape_kite_public_token(clientid, passwd, pin, headless=True):
    base_url   = 'https://kite.zerodha.com/'

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')  # For headless mode
    # endif
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(base_url)
    # Login using clientid and password
    base_inps = driver.find_elements_by_tag_name('input')
    base_inps[0].send_keys(clientid)
    base_inps[1].send_keys(passwd)
    base_button = driver.find_element_by_tag_name('button')
    base_button.click()
    time.sleep(2)
    # Specify PIN
    der_inp = driver.find_element_by_tag_name('input')
    der_inp.send_keys(pin)
    der_button = driver.find_element_by_tag_name('button')
    der_button.click()

    # Again load main page and sleep
    driver.get(base_url)
    time.sleep(2)
    
    reqs_all = driver.requests
    req_toks = []
    for indx,req_t in enumerate(reqs_all):
        if req_t.path == base_url:
            req_toks.append(indx)
        # endif
    # endfor
    
    assert len(req_toks) != 0, 'FATAL::: No Request token found !!'
    
    cookie_info = reqs_all[req_toks[-1]].headers['Cookie'].split(';') # Remove __cfduid
    print('>> Extra info = {}'.format(cookie_info))
    driver.close()
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--auth', help='Authentication [client_id,password,login_pin].', type=str, default=None)
    parser.add_argument('--show', help='Show browser window', action='store_true')
    args    = parser.parse_args()

    print('>> Browser window {}'.format('enabled' if args.__dict__['show'] else 'disabled'))

    if args.__dict__['auth'] == None:
        print('--auth is required !!')
        sys.exit(-1)
    # endif

    # Flags
    auth_info = args.__dict__['auth']
    auth_toks = auth_info.split(',')
    if len(auth_toks) != 3:
        print('--auth should be in proper format.Check --help.')
        sys.exit(-1)
    # endif

    scrape_kite_public_token(auth_toks[0], auth_toks[1], auth_toks[2], headless=not args.__dict__['show'])
# endif
