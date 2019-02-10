#!/usr/bin/env python

from   selenium import webdriver
from   selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from   selenium.webdriver.support.ui import WebDriverWait
from   selenium.webdriver.support import expected_conditions as EC
from   selenium.common.exceptions import TimeoutException
from   selenium.webdriver.common.by import By
import time
import glob, os, sys
import csv, zipfile
import urllib, datetime
from   StringIO import StringIO
from   pyvirtualdisplay import Display

download_dir = '/home/vi/work/google/'


#caps = DesiredCapabilities.FIREFOX

# Tell the Python bindings to use Marionette.
# This will not be necessary in the future,
# when Selenium will auto-detect what remote end
# it is talking to.
#caps["marionette"] = True

# Path to Firefox DevEdition or Nightly.
# Firefox 47 (stable) is currently not supported,
# and may give you a suboptimal experience.
#
# On Mac OS you must point to the binary executable
# inside the application package, such as
# /Applications/FirefoxNightly.app/Contents/MacOS/firefox-bin
#caps["binary"] = "/usr/bin/firefox"

# Download latest bhavcopy
def bse_latest_bhavcopy_info():
    l_file = None
    date_y   = datetime.datetime.today() - datetime.timedelta(days=1)    # yesterday date
    shift    = datetime.timedelta(max(1,(date_y.weekday() + 6) % 7 - 3))
    date_y   = date_y - shift
    url_this = "http://www.bseindia.com/download/BhavCopy/Equity/EQ{:02d}{:02d}{:02d}_CSV.ZIP".format(date_y.day, date_y.month, date_y.year % 2000)
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

def sleep(n_secs):
    print "Sleeping for {} seconds.".format(n_secs)
    time.sleep(n_secs)
# enddef

def main_thread(bse_list):
    delay = 2 # seconds
    error_list = []
    n_list = len(bse_list)
    ctr = 1

    # Hide display
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Using Firefox 45 with this version
    profile = webdriver.FirefoxProfile()
    
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", download_dir)
    profile.set_preference("browser.download.downloadDir", download_dir)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-excel")
    profile.update_preferences()
    
    driver = webdriver.Firefox(firefox_profile=profile)
    url    = "http://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?scripcode={}".format(bse_list[0])
    driver.get(url)

    for bse_code in bse_list:
        try:
            print "{}/{} : Fetching {}".format(ctr, n_list, bse_code)
            # Fill form with correct bse code and select the first entry
            form = driver.find_element_by_id('ctl00_ContentPlaceHolder1_GetQuote1_smartSearch')
            form.click()
            form.clear()
            form.send_keys(str(bse_code))  # Sending keys as integer causes some problems.
            sleep(delay)
            first_option = driver.find_element_by_id('ajax_response_smart').find_elements_by_tag_name('li')[0]
            # Check if an option was found for the key
            if first_option.text == 'No Match found':
                print "No match found for {}".format(bse_code)
                continue
            else:
                first_option.click()  # Click the option
            # endif
            sleep(delay-1)
            # Select monthly button (We want monthly data)
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_rdbMonthly').click()             # Select monthly
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_cmbMonthly').send_keys('Jan')    # Select Month
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_cmbMYear').send_keys('1992')     # Select Year
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnSubmit').click()              # Submit
        except:
            print "Error happened during fetching {}. Ignoring !!".format(bse_code)
            error_list.append(bse_code)
            ctr = ctr + 1
            continue
        # endtry
        
        #try:
        #    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_btnDownload')))
        #except TimeoutException:
        #    pass
        #except:
        #    print "Error happened during wait. Ignoring !!"
        #    continue
        ## endtry

        sleep(delay)  # Hopefully enough

        try:
            # Try to download
            driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnDownload').click()            # Click download button
        except:
            print "Couldn't download {}".format(bse_code)
        # endtry
        ctr = ctr + 1
    # endfor

    print "Couldn't fetch from companies {}".format(error_list)

    # Clean
    driver.close()
    display.stop()
# enddef

def g_csv_files(in_dir):
    d_list = []
    for i_file in glob.glob1(in_dir, '*.csv'):
        d_list.append(int(os.path.splitext(i_file)[0]))
    # endfor
    return d_list
# enddef

if __name__ == '__main__':
    bse_list = bse_latest_bhavcopy_info().keys()
    already_downloaded = g_csv_files(download_dir)
    to_be_downloaded = list(set(bse_list) - set(already_downloaded))
    main_thread(to_be_downloaded)
# enddef
