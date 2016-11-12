#!/usr/bin/env python

import datetime
import re
import pandas
import json
import sys
import glob
import argparse
import copy
import pprint
import urllib
import csv
import zipfile
import pymongo
from   pymongo import MongoClient
import logging
import inspect
#from   packages.core.utils import *
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO
# endtry

# Variables
__DEBUG__ = False

# Log string
def logmsg(msg):
    stk    = inspect.stack()
    f_name = '{}.{}'.format(str(stk[1][0].f_locals['self'].__class__), stk[1][3])
    msg    = f_name + ' : ' + msg
    if __DEBUG__ == True:
        logging.debug(msg)
    # endif
# enddef

def fname():
    return inspect.stack()[1][3]
# enddef

# A metaclass specifier
class NonOverridable(type):
    def __new__(self, name, bases, dct):
        def __cu(s):
            if s[0:1] == '_' or s[0:2] == '__':
                return True
            return False
        # enddef
        for c in bases:
            for k in c.__dict__:
                if not __cu(k) and k in dct:
                    raise SyntaxError, "Overriding {} is not allowed".format(k)
                # endif
            # endfor
        # endfor
        return type.__new__(self, name, bases, dct)
    # enddef
# endclass

# Download latest bhavcopy
def bse_latest_bhavcopy_info():
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ{:02d}{:02d}{:02d}_CSV.ZIP".format(date_y.day,
               date_y.month, date_y.year % 2000)
    print "Fetching BSE Bhavcopy from {}".format(url_this)
    d_data   = urllib.urlopen(url_this)
    l_file   = StringIO(d_data.read())
    
    # Read zip file
    zip_f    = zipfile.ZipFile(l_file)
    csv_f    = csv.reader(zip_f.open(zip_f.namelist()[0]))
    bse_dict = {}
    ctr      = 0

    for item_this in csv_f:
        # Convert strings to integers/floats
        if ctr != 0:
            cc_dict = {
                "bse_code"        : int(item_this[0]),
                "bse_name"        : item_this[1].rstrip(),
                "bse_group"       : item_this[2].rstrip(),
                "bse_type"        : item_this[3].rstrip(),
                "open"            : float(item_this[4]),
                "high"            : float(item_this[5]),
                "low"             : float(item_this[6]),
                "close"           : float(item_this[7]),
                "last"            : float(item_this[8]),
                "prev_close"      : float(item_this[9]),
                "no_trades"       : int(item_this[10]),
                "no_shares"       : int(item_this[11]),
                "net_turnover"    : float(item_this[12]),
            }
            bse_dict[cc_dict['bse_code']] = cc_dict
            #db.screener_in.update({ 'bse_code' : cc_dict['bse_code'] }, { '$set' : { 'bse_bhavcopy' : cc_dict } })
        # endif
        ctr = ctr + 1
    # endfor
    return bse_dict
# enddef



# Company context. Defines every data/function need to operate on the ratios
class ScreenerCompanyContext(object):
    __metaclass__              = NonOverridable

    # Keys
    K_NSET                     = u'number_set'
    K_WAREHOUSE_SET            = u'warehouse_set'

    K_QUARTER                  = u'quarters'
    K_ANNUAL                   = u'annual'
    K_NET_PROFIT               = u'net_profit'
    K_SALES                    = u'sales'
    K_EXPENSES                 = u'expenses'
    K_OPERATING_PROFIT         = u'operating_profit'
    K_OPM                      = u'opm'
    K_OTHER_INCOME             = u'other_income'
    K_INTEREST                 = u'interest'
    K_DEPRECIATION             = u'depreciation'
    K_PROFIT_BEFORE_TAX        = u'profit_before_tax'
    K_TAX                      = u'tax'
    K_EPS_UNADJ                = u'eps'
    K_EPS                      = u'eps'
    K_DIVIDEND_PAYOUT          = u'dividend_payout'
    
    K_CASHFLOW                 = u'cashflow'
    K_CFO                      = u'cash_from_operating_activity'
    K_CFI                      = u'cash_from_investing_activity'
    K_CFF                      = u'cash_from_financing_activity'
    K_NET_CASHFLOW             = u'net_cash_flow'

    K_BALANCE_SHEET            = u'balancesheet'
    K_EQUITY_CAPITAL           = u'share_capital'
    K_RESERVES                 = u'reserves'
    K_BORROWINGS               = u'borrowings'
    K_OTHER_LIABILITIES        = u'other_liabilities'
    K_TOTAL_LIABILITIES        = u'total_liabilities'
    K_FIXED_ASSETS             = u'fixed_assets'
    K_CWIP                     = u'cwip'
    K_INVESTMENTS              = u'investments'
    K_OTHER_ASSETS             = u'other_assets'
    K_TOTAL_ASSETS             = u'total_assets'

    K_FACE_VALUE               = u'face_value'
    K_BOOK_VALUE               = u'book_value'
    K_DIV_YIELD                = u'dividend_yield'
    K_ROE                      = u'return_on_equity'
    K_CURR_PRICE               = u'current_price'
    K_P2E                      = u'price_to_earning'
    K_P2B                      = u'price_to_book'
    K_D2B                      = u'debt_to_book'
    K_ROE_3Y                   = u'average_return_on_equity_3years'
    K_ROE_5Y                   = u'average_return_on_equity_5years'
    K_ROE_10Y                  = u'average_return_on_equity_5years'

    K_DATE_LIST                = u'date_list'
    K_BSE_CODE                 = u'bse_code'
    K_NSE_CODE                 = u'nse_code'
    K_NAME                     = u'name'
    K_SHORT_NAME               = u'short_name'

    K_NSET_KEYS_LIST           = [ K_ANNUAL, K_QUARTER, K_CASHFLOW, K_BALANCE_SHEET ]

    # Misc
    K_ANNUAL_DATE_LIST         = "annual_date_list"
    K_QUARTER_DATE_LIST        = "quarter_date_list"
    K_LAST_ANNUAL_DATE         = "last_annual_date"
    K_LAST_QUARTER_DATE        = "last_quarter_date"
    K_DEBT_TO_EQUITY           = "debt_to_equity"
    K_NUM_SHARES               = "number_of_equity_shares"
    K_EARNINGS_PER_SHARE       = "earnings_per_share"
    K_PROFIT_GROWTH_3YRS       = "profit_growth_3years"
    K_PROFIT_GROWTH_5YRS       = "profit_growth_5years"
    K_EARNINGS_GROWTH_3YRS     = "earnings_growth_3years"
    K_EARNINGS_GROWTH_5YRS     = "earnings_growth_5years"
    K_SALES_GROWTH_3YRS        = "sales_growth_3years"
    K_SALES_GROWTH_5YRS        = "sales_growth_5years"
    K_BOOK_VALUE_GROWTH_3YRS   = "book_value_growth_3years"
    K_BOOK_VALUE_GROWTH_5YRS   = "book_value_growth_5years"
    K_OPM_3YRS                 = "opm_3years"
    K_OPM_5YRS                 = "opm_5years"
    K_CUM_CFO_3YRS             = "cumulative_cfo_3years"
    K_CUM_CFO_5YRS             = "cumulative_cfo_5years"
    K_CUM_NCF_3YRS             = "cumulative_ncf_3years"
    K_CUM_NCF_5YRS             = "cumulative_ncf_5years"
    K_CUM_PAT_3YRS             = "cumulative_pat_3years"
    K_CUM_PAT_5YRS             = "cumulative_pat_5years"
    K_CUM_CFO                  = "cumulative_cfo"
    K_CUM_NCF                  = "cumulative_ncf"
    K_CUM_PAT                  = "cumulative_pat"

    K_JUNK_STATUS              = "junk"
    K_GENERATED_SET            = "generated_set"

    # Members
    def update_bsebhavcopy(self, bhavcopy_dict):
        self.__bse_bcopy = {}
        self.__bse_bcopy[self.K_CURR_PRICE]    = bhavcopy_dict["close"]
        self.__curr_price                      = self.__bse_bcopy[self.K_CURR_PRICE]
        self.__bse_bcopy[self.K_P2E]           = self.__curr_price / self.__ttm_earnings_per_share()
        self.__bse_bcopy[self.K_P2B]           = self.__curr_price / self.__edb[self.K_BOOK_VALUE]

        # Updated ratios
        self.__db[self.K_GENERATED_SET].update(self.__bse_bcopy)
    # enddef

    def set_junk(self, status):
        self.__db[self.K_JUNK_STATUS] = status
    def get_junk(self):
        return self.__db[self.K_JUNK_STATUS]

    #####
    def __sorted(self, d_list):
        return sorted(d_list, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    # enddef
    def __sign(self, num):
        return (num > 0) - (num < 0)
    # enddef

    def __init__(self, json_file):
        logmsg('Entry !!')

        self.__db  = self.__populate_company_dbase(json_file)
        self.__db[self.K_GENERATED_SET] = {}
        self.__edb = {}

        # Log everything uptil now
        logmsg('Populated data from __populate_company_dbase() = {}'.format(pprint.pformat(self.__db)))
        #print "json = {}".format(json_file)

        self.__annual_date_list                     = self.__g_annual_date_list()
        self.__quarter_date_list                    = self.__g_quarter_date_list()
        self.__annual_date_list_length              = len(self.__annual_date_list)
        self.__quarter_date_list_length             = len(self.__quarter_date_list)
        self.__last_annual_date                     = self.__g_last_annual_date()
        self.__last_quarter_date                    = self.__g_last_quarter_date()

        # Log
        logmsg('annual_date_list             = {}'.format(self.__annual_date_list))
        logmsg('quarter_date_list            = {}'.format(self.__quarter_date_list))
        logmsg('annual_date_list_length      = {}'.format(self.__annual_date_list_length))
        logmsg('quarter_date_list_length     = {}'.format(self.__quarter_date_list_length))
        logmsg('last_annual_date             = {}'.format(self.__last_annual_date))
        logmsg('last_quarter_date            = {}'.format(self.__last_quarter_date))

        self.__edb[self.K_DEBT_TO_EQUITY]           = self.__debt_to_equity()
        self.__edb[self.K_NUM_SHARES]               = self.__number_of_equity_shares()
        self.__edb[self.K_ROE]                      = self.__warehouse_data(self.K_ROE)
        self.__edb[self.K_BOOK_VALUE]               = self.__warehouse_data(self.K_BOOK_VALUE)
        self.__edb[self.K_DIV_YIELD]                = self.__warehouse_data(self.K_DIV_YIELD)
        self.__edb[self.K_EARNINGS_PER_SHARE]       = self.__ttm_earnings_per_share()
        self.__edb[self.K_PROFIT_GROWTH_3YRS]       = self.__annual_param_growth(self.K_NET_PROFIT, 3)
        self.__edb[self.K_PROFIT_GROWTH_5YRS]       = self.__annual_param_growth(self.K_NET_PROFIT, 5)
        self.__edb[self.K_SALES_GROWTH_3YRS]        = self.__annual_param_growth(self.K_SALES, 3)
        self.__edb[self.K_SALES_GROWTH_5YRS]        = self.__annual_param_growth(self.K_SALES, 5)
        self.__edb[self.K_EARNINGS_GROWTH_3YRS]     = self.__annual_param_growth(self.K_EPS, 3)
        self.__edb[self.K_EARNINGS_GROWTH_5YRS]     = self.__annual_param_growth(self.K_EPS, 5)
        self.__edb[self.K_BOOK_VALUE_GROWTH_3YRS]   = self.__book_value_growth(3)
        self.__edb[self.K_BOOK_VALUE_GROWTH_5YRS]   = self.__book_value_growth(5)
        self.__edb[self.K_CUM_CFO]                  = self.__cum_cashflow(self.K_CFO)
        self.__edb[self.K_CUM_NCF]                  = self.__cum_cashflow(self.K_NET_CASHFLOW)
        self.__edb[self.K_CUM_PAT]                  = self.__cum_param_annual(self.K_NET_PROFIT)

        # Copy some elements intact
        self.__edb[self.K_BSE_CODE]                 = self.__db[self.K_BSE_CODE]
        self.__edb[self.K_NSE_CODE]                 = self.__db[self.K_NSE_CODE]
        self.__edb[self.K_NAME]                     = self.__db[self.K_NAME]
        self.__edb[self.K_SHORT_NAME]               = self.__db[self.K_SHORT_NAME]

        # Update generated set
        self.__db[self.K_GENERATED_SET].update(self.__edb)
        self.__db[self.K_JUNK_STATUS]     = False

        # If There are no quarterly results, set status as Junk
        if self.__quarter_date_list_length == 0:
            self.set_junk(True)
        # endif
    # enddef

    def __populate_company_dbase(self, json_file):
        logmsg('Entry !!')

        d_scrip    = json.load(open(json_file, "r"))
        a_dbase    = copy.copy(d_scrip)

        # number_set
        for skey in self.K_NSET_KEYS_LIST:
            nset_t = d_scrip[self.K_NSET][skey]
            a_dbase[self.K_NSET][skey] = {}
            for i_t in range(0, len(nset_t)):
                k_t = nset_t[i_t][0]
                v_t = nset_t[i_t][1]
                # Create a dict instead of the old list of list
                k_n = k_t.lower().replace(' ', '_')
                # Modify eps
                if k_n[0:3] == 'eps':
                    k_n = 'eps'
                # endif
                a_dbase[self.K_NSET][skey][k_n] = v_t
            # endfor
        # endfor

        # Misc
        a_dbase[self.K_BSE_CODE] = int(str(d_scrip[self.K_BSE_CODE]))

        # Modify warehouse item
        whouse_keys = d_scrip[self.K_WAREHOUSE_SET].keys()
        for item_this in whouse_keys:
            try:
                a_dbase[self.K_WAREHOUSE_SET][item_this] = float(str(d_scrip[self.K_WAREHOUSE_SET][item_this]))
            except ValueError:
                pass
        # endfor

        logmsg('Exit !!')
        return a_dbase
    # enddef

    ########
    def __g_annual_date_list(self):
        if len(self.__db[self.K_NSET][self.K_ANNUAL][self.K_SALES]) > 0:
            return self.__sorted(self.__db[self.K_NSET][self.K_ANNUAL][self.K_SALES].keys())
        else:
            return []
        # endif
    # enddef
    def __g_last_annual_date(self):
        if len(self.__annual_date_list) > 0:
            return self.__annual_date_list[-1]
        else:
            return ''
        # endif
    # enddef
    def __g_quarter_date_list(self):
        if len(self.__db[self.K_NSET][self.K_QUARTER][self.K_SALES]) > 0:
            return self.__sorted(self.__db[self.K_NSET][self.K_QUARTER][self.K_SALES].keys())
        else:
            return []
        # endif
    # enddef
    def __g_last_quarter_date(self):
        if len(self.__quarter_date_list) > 0:
            return self.__quarter_date_list[-1]
        else:
            return ''
        # endif
    # enddef
    
    ########## ratios 
    def __debt_to_equity(self):
        if self.__last_annual_date == '':
            return ''
        # endif
        try:
            lastdate  = self.__last_annual_date
            debt      = self.__balancesheet_borrowings(lastdate)
            equity    = self.__balancesheet_equity_capital(lastdate) + self.__balancesheet_reserves(lastdate)

            # Log
            logmsg('lastdate      = {}'.format(lastdate))
            logmsg('debt          = {}'.format(debt))
            logmsg('equity        = {}'.format(equity))

            return debt/equity
        except:
            return ''
        # endtry
    def __number_of_equity_shares(self):
        if self.__last_annual_date == '':
            return ''
        # endif
        try:
            lastdate   = self.__last_annual_date
            equity_cap = self.__balancesheet_equity_capital(lastdate)
            face_value = self.__db[self.K_WAREHOUSE_SET][self.K_FACE_VALUE]

            logmsg('lastdate      = {}'.format(lastdate))
            logmsg('equity_cap    = {}'.format(equity_cap))
            logmsg('face_value    = {}'.format(face_value))

            return equity_cap/face_value
        except:
            return ''
        # endtry
    def __ttm_earnings_per_share(self):
        if len(self.__quarter_date_list) < 4:
            return ''
        # endif
        try:
            ttm_earnings = sum([ self.__quarter_net_profit(x) for x in  self.__quarter_date_list[-4:] ])/self.__number_of_equity_shares()

            logmsg('ttm_earnings_per_share = {}'.format(ttm_earnings))

            return ttm_earnings
        except:
            return ''
        # endtry
    def __annual_param_growth(self, param_key, t_yrs):
        if len(self.__annual_date_list) < (t_yrs + 1):
            return ''
        # endif
        try:
            prev_t = self.__annual_date_list[-t_yrs-1]
            curr_t = self.__annual_date_list[-1]
            prev_p = self.__annual_income(param_key)[prev_t]
            curr_p = self.__annual_income(param_key)[curr_t]
            sign   = self.__sign(curr_p/prev_p)
            g_per  = sign * (abs(curr_p/prev_p)**(1.0/t_yrs) - 1) * 100.0

            # Log
            logmsg('prev_t  = {}'.format(prev_t))

            return g_per
        except:
            return ''
        # entry
    def __ttm_param_growth(self, param_key, t_yrs):
        if len(self.__annual_date_list) < (t_yrs + 1) or len(self.__quarter_date_list) < 4:
            return ''
        # endif
        try:
            prev_t = self.__annual_date_list[-t_yrs-1]
            prev_p = self.__annual_income(param_key)[prev_t]
            curr_p = sum([ self.__quarter_income(param_key)[x] for x in  self.__quarter_date_list[-4:] ])
            sign   = self.__sign(curr_p/prev_p)
            g_per  = sign * (abs(curr_p/prev_p)**(1.0/t_yrs) - 1) * 100.0
            return g_per
        except:
            return ''
        # entry
    def __balancesheet_param_growth(self, param_key, t_yrs):
        if len(self.__annual_date_list) < (t_yrs + 1):
            return ''
        # endif
        try:
            prev_t = self.__annual_date_list[-t_yrs-1]
            curr_t = self.__annual_date_list[-1]
            prev_p = self.__balancesheet(param_key)[prev_t]
            curr_p = self.__balancesheet(param_key)[curr_t]
            sign   = self.__sign(curr_p/prev_p)
            g_per  = sign * (abs(curr_p/prev_p)**(1.0/t_yrs) - 1) * 100.0
            return g_per
        except:
            return ''
        # entry
    def __book_value_growth(self, t_yrs):
        logmsg('Entry !!')
        if len(self.__annual_date_list) < (t_yrs + 1):
            logmsg('Exit from len check !!')
            return ''
        # endif
        try:
            prev_t = self.__annual_date_list[-t_yrs-1]
            curr_t = self.__annual_date_list[-1]
            prev_p = self.__balancesheet(self.K_EQUITY_CAPITAL)[prev_t] + self.__balancesheet(self.K_RESERVES)[prev_t]
            curr_p = self.__balancesheet(self.K_EQUITY_CAPITAL)[curr_t] + self.__balancesheet(self.K_RESERVES)[curr_t]
            sign   = self.__sign(curr_p/prev_p)
            g_per  = sign * (abs(curr_p/prev_p)**(1.0/t_yrs) - 1) * 100.0

            # Logs
            logmsg('prev_t  = {}'.format(prev_t))
            logmsg('curr_t  = {}'.format(curr_t))
            logmsg('prev_p  = {}'.format(prev_p))
            logmsg('curr_p  = {}'.format(curr_p))
            logmsg('sign    = {}'.format(sign))
            logmsg('g_per   = {}'.format(g_per))

            logmsg('Exit !!')
            return g_per
        except:
            logmsg('Exit from except clause !!')
            return ''
        # entry
    def __cum_param_annual(self, param_key, t_yrs=None):
        logmsg('Entry !!')
        if t_yrs and self.__annual_date_list_length  < (t_yrs + 1):
            logmsg('Exit from len check !!')
            return ''
        # endif
        try:
            if t_yrs == None:
                cum_param = sum(self.__annual_income(param_key).values())
            else:
                cum_param = sum([ self.__annual_income(param_key)[x] for x in self.__annual_date_list[-t_yrs:] ])
            # endif

            # Logs
            logmsg('t_yrs     = {}'.format(t_yrs))
            logmsg('cum_param = {}'.format(cum_param))

            logmsg('Exit !!')
            return cum_param
        except:
            logmsg('Exit from except clause !!')
            return ''
        # endtry
    def __cum_cashflow(self, cf_type, t_yrs=None):
        logmsg('Entry !!')
        if t_yrs and self.__annual_date_list_length < (t_yrs + 1):
            logmsg('Exit from first check !!')
            return ''
        # endif
        try:
            if t_yrs == None:
                cum_cf = sum(self.__cf(cf_type).values())
            else:
                cum_cf = sum([ self.__cf(cf_type)[x] for x in self.__annual_date_list[-t_yrs:] ])
            # endif

            # Logs
            logmsg('t_yrs   = {}'.format(t_yrs))
            logmsg('cum_cf  = {}'.format(cum_cf))

            logmsg('Exit !!')
            return cum_cf
        except:
            logmsg('Exit from except clause !!')
            return ''
        # endtry

    ######## helpers
    def __warehouse_data(self, key):
        return self.__db[self.K_WAREHOUSE_SET][key]

    def __select(self, d_this, subkey=None):
        return (d_this if subkey == None else d_this[subkey])

    def __quarter_income(self, subkey=None):
        return self.__select(self.__db[self.K_NSET][self.K_QUARTER], subkey)
    def __quarter_depreciation(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_DEPRECIATION), d_date)
    def __quarter_sales(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_SALES), d_date)
    def __quarter_expenses(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_EXPENSES), d_date)
    def __quarter_operating_profit(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_OPERATING_PROFIT), d_date)
    def __quarter_opm(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_OPM), d_date)
    def __quarter_other_income(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_OTHER_INCOME), d_date)
    def __quarter_interest(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_INTEREST), d_date)
    def __quarter_profit_before_tax(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_PROFIT_BEFORE_TAX), d_date)
    def __quarter_tax(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_TAX), d_date)
    def __quarter_net_profit(self, d_date=None):
        return self.__select(self.__quarter_income(self.K_NET_PROFIT), d_date)

    def __annual_income(self, subkey=None):
        return self.__select(self.__db[self.K_NSET][self.K_ANNUAL], subkey)
    def __annual_depreciation(self, d_date=None):
        return self.__select(self.__annual_income(self.K_DEPRECIATION), d_date)
    def __annual_sales(self, d_date=None):
        return self.__select(self.__annual_income(self.K_SALES), d_date)
    def __annual_expenses(self, d_date=None):
        return self.__select(self.__annual_income(self.K_EXPENSES), d_date)
    def __annual_operating_profit(self, d_date=None):
        return self.__select(self.__annnual_income(self.K_OPERATING_PROFIT), d_date)
    def __annual_opm(self, d_date=None):
        return self.__select(self.__annual_income(self.K_OPM), d_date)
    def __annual_other_income(self, d_date=None):
        return self.__select(self.__annual_income(self.K_OTHER_INCOME), d_date)
    def __annual_interest(self, d_date=None):
        return self.__select(self.__annual_income(self.K_INTEREST), d_date)
    def __annual_profit_before_tax(self, d_date=None):
        return self.__select(self.__annual_income(self.K_PROFIT_BEFORE_TAX), d_date)
    def __annual_tax(self, d_date=None):
        return self.__select(self.__annual_income(self.K_TAX), d_date)
    def __annual_net_profit(self, d_date=None):
        return self.__select(self.__annual_income(self.K_NET_PROFIT), d_date)
    def __annual_eps_unadj(self, d_date=None):
        return self.__select(self.__annual_income(self.K_EPS_UNADJ), d_date)
    def __annual_dividend_payout(self, d_date=None):
        return self.__select(self.__annual_income(self.K_DIVIDEND_PAYOUT), d_date)

    def __cf(self, subkey=None):
        return self.__select(self.__db[self.K_NSET][self.K_CASHFLOW], subkey)
    def __cfo(self, d_date=None):
        return self.__select(self.__cf(self.K_CFO), d_date)
    def __cfi(self, d_date=None):
        return self.__select(self.__cf(self.K_CFI), d_date)
    def __cff(self, d_date=None):
        return self.__select(self.__cf(self.K_CFF), d_date)
    def __ncf(self, d_date=None):
        return self.__select(self.__cf(self.K_NET_CASHFLOW), d_date)

   
    def __balancesheet(self, subkey=None):
        return self.__select(self.__db[self.K_NSET][self.K_BALANCE_SHEET], subkey)
    def __balancesheet_equity_capital(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_EQUITY_CAPITAL), d_date)
    def __balancesheet_reserves(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_RESERVES), d_date)
    def __balancesheet_borrowings(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_BORROWINGS), d_date)
    def __balancesheet_other_liabilities(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_OTHER_LIABILITIES), d_date)
    def __balancesheet_total_liabilities(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_TOTAL_LIABILITIES), d_date)
    def __balancesheet_fixed_assets(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_FIXED_ASSETS), d_date)
    def __balancesheet_cwip(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_CWIP), d_date)
    def __balancesheet_investments(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_INVESTMENTS), d_date)
    def __balancesheet_other_assets(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_OTHER_ASSETS), d_date)
    def __balancesheet_total_assets(self, d_date=None):
        return self.__select(self.__balancesheet(self.K_TOTAL_ASSETS), d_date)

    ##########

    def database(self):
        return self.__db
    # enddef
    def ext_database(self):
        return self.__edb
    # enddef

# endclass

def populate_screener_dbase(dir_name):
    files_list    = glob.glob(dir_name + "/*.json")
    #mongo_client  = MongoClient()
    #db            = mongo_client.fscreener
    co_ctxt_d     = {}
    print "Start populating internal database."

    for file_this in files_list:
        ctxt = ScreenerCompanyContext(file_this)
        inf_dbase = ctxt.database()
        co_ctxt_d[inf_dbase['bse_code']] = ctxt
    # endfor
    return co_ctxt_d
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument("--json_dir",   help="screener.in json files directory", type=str,  default=None)
    parser.add_argument("--log",        help="logging enabled",                  action='store_true')
    args    = parser.parse_args()

    if not args.__dict__["json_dir"]:
        print "--json_dir is required !!"
        sys.exit(-1)
    # endif
    if args.__dict__["log"]:
        __DEBUG__ = True
    # endif

    # Logging file init
    logging.basicConfig(filename='/tmp/build_screener_dbase.py.log', filemode='w', level=logging.DEBUG)

    # Build dbase
    bse_bhavcopy_d = bse_latest_bhavcopy_info()
    co_ctxt_d = populate_screener_dbase(args.__dict__["json_dir"])
    
    # Update co_ctxt with bhavcopy info
    print "Updating bhavcopy for populated internal database."
    for k in co_ctxt_d.keys():
        try:
            (co_ctxt_d[k]).update_bsebhavcopy(bse_bhavcopy_d[k])   # k -> bse_code
        except:
            (co_ctxt_d[k]).set_junk(True)
        # endtry
    # endfor

    # Write to db
    print "Updating mongodb database."
    mongo_client  = MongoClient()
    db            = mongo_client.fscreener
    for k in co_ctxt_d.keys():
        ctxt_t    = co_ctxt_d[k]
        dbase_t   = ctxt_t.database()
        db.screener_in.update({ 'bse_code' : dbase_t['bse_code'] }, dbase_t, upsert=True)
    # endfor

    mongo_client.close()
# endif
