#/usr/bin/env python
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# This script pulls some data (right now only a few) from marketsmojo.com using a search pattern
# (may be company's scrip id or code or name etc). Will add more info to display in future


import requests
from   bs4 import BeautifulSoup
import argparse
import pprint
import sys

def pull_info_from_marketsmojo(scrip):
    url_search = 'https://www.marketsmojo.com/portfolio-plus/frontendsearch?SearchPhrase={}'
    url_front  = 'https://www.marketsmojo.com'
    company_l  = []

    req_this   = requests.get(url_search.format(scrip))
    if req_this.json() == []:
        print 'Nothing found for {} !!'.format(scrip)
        return
    # endif

    # Go over all of them
    for item_this in req_this.json():
        url_page = url_front + item_this[u'url']
        company  = item_this[u'Company']
        pg_this  = requests.get(url_page)

        # Parse using beautifulsoup
        html_page = BeautifulSoup(pg_this.text, 'html.parser')
        ##
        valuation = html_page.find('div', {'class' : 'valuation cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')
        quality   = html_page.find('div', {'class' : 'quality cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')
        fin_trend = html_page.find('div', {'class' : 'financials cf'}).text.replace('\n', ' ').rstrip(' ').strip(' ')

        company_l.append({
                             "name"         : company,
                             "code"         : scrip,
                             "valuation"    : valuation,
                             "quality"      : quality,
                             "fintrend"     : fin_trend,
                        })
    # endfor

    return company_l
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument("--scrip",    help="Scrip to be searched for.", type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["scrip"]:
        print "--scrip is required !!"
        sys.exit(-1)
    # endif

    search_results = pull_info_from_marketsmojo(args.__dict__["scrip"])
    pprint.pprint(search_results, indent=4)
# endif
