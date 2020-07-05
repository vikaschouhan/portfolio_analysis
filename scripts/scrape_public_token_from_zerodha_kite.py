# Author   : Vikas Chouhan (presentisgood@gmail.com)
# Purpose  : Scrape public token id from zerodha kite.

from   seleniumwire import webdriver
import time
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *

# Converts cookies recovered by selenium to python dictionary
def selenium_cookies_to_pydict(cookies):
    return {x['name']: x['value'] for x in cookies}
# enddef

# Generate request headers for kite
def generate_request_headers(cookies):
    user_agent   = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
    cookiesd     = selenium_cookies_to_pydict(cookies)
    headers      = {
        'authority'        : 'kite.zerodha.com',
        'accept'           : 'application/json, text/plain, */*',
        'authorization'    : 'enctoken {}'.format(cookiesd['enctoken']),
        'user-agent'       : user_agent,
        'sec-fetch-site'   : 'same-origin',
        'sec-fetch-mode'   : 'cors',
        'accept-encoding'  : 'application/json, text/plain, */*',
        'accept-language'  : 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie'           : '__cfduid={}; kf_session={}; public_token={}; user_id={}; enctoken={}'.format(cookiesd['__cfduid'],
                             cookiesd['kf_session'], cookiesd['public_token'], cookiesd['user_id'], cookiesd['enctoken'])
    }
    return headers
# enddef

def generate_request_params(cookies, t_from=None, t_to=None):
    cookiesd  = selenium_cookies_to_pydict(cookies)
    params_base = [('user_id', cookiesd['user_id']), ('oi', 1)]
    return  params_base + [('from', t_from), ('to', t_to)] if t_from and t_to else params_base
# enddef

# Generate curl headers
def generate_curl_command_headers(cookies):
    headers = generate_request_headers(cookies)
    headers_cmd = ''.join([" -H '{}: {}'".format(k, v) for k,v in headers.items()])
    return headers_cmd
# enddef

# Scrape headers
def scrape_kite_cookies(clientid, passwd, pin, headless=True):
    base_url   = 'https://kite.zerodha.com/'
    demo_chart_url = 'https://kite.zerodha.com/chart/web/tvc/INDICES/NIFTY%2050/256265'

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

    # Load a demo chart and sleep
    driver.get(demo_chart_url)
    time.sleep(2)

    return driver.get_cookies()
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--auth', help='Authentication [client_id,password,login_pin].', type=str, default=None)
    parser.add_argument('--show', help='Show browser window', action='store_true')
    parser.add_argument('--pyfile', help='Dump headers and params as python file.', type=str, default=None)
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

    cookies  = scrape_kite_cookies(auth_toks[0], auth_toks[1], auth_toks[2], headless=not args.__dict__['show'])
    headers  = generate_request_headers(cookies)
    cheaders = generate_curl_command_headers(cookies)
    params   = generate_request_params(cookies)
    print('>> Headers.')
    print(headers)
    print('>> Curl headers.')
    print(cheaders)
    print('>> Request params.')
    print(params)

    if args.__dict__['pyfile']:
        print('>> Writing all info to {}'.format(args.__dict__['pyfile']))
        with open(rp(args.__dict__['pyfile']), 'w') as f_out:
            f_out.write('headers = {}\n'.format(headers))
            f_out.write('headers_curl = "{}"\n'.format(cheaders))
            f_out.write('params = {}\n'.format(params))
        # endwith
    # endif
# endif
