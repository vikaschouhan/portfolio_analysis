from   selenium import webdriver
from   selenium.webdriver.common.keys import Keys
from   selenium.webdriver.common.proxy import *
import time
import os
import json
import sys
import multiprocessing
from   multiprocessing import Process
import argparse

def assertm(cond, msg):
    if not cond:
        print msg
        sys.exit(-1)
    # endif
# enddef

def main_thread(file_out):
    site_path         = "http://proxylist.hidemyass.com/"
    pages_list        = [ "#listable", "#2listable", "#3listable" ]
    # Initialize driver
    driver            = webdriver.Firefox()
    f_out             = open(file_out, "a+")

    # Get first page
    driver.get(site_path)

    el                = driver.find_element_by_name("pp")
    for option in el.find_elements_by_tag_name("option"):
        if option.text == "100 PER PAGE":
            option.click() # select() in earlier versions of webdriver
            break
        # endif
    # endfor

    # Iterate
    for page_this in pages_list:
        page_final    = site_path + page_this
        # Get first page
        driver.get(page_final)

        # Extract tables
        table_this    = driver.find_element_by_id("listable")
        # Extract all rows
        rows_all      = table_this.find_elements_by_tag_name("tr")
        # Iterate over all rows
        for row_this in rows_all:
            try:
                td_l  = row_this.find_elements_by_tag_name("td")
                ip    = td_l[1].text
                port  = td_l[2].text
                f_out.write("{}:{}".format(ip, port))
                f_out.write("\n")
                f_out.flush()
            except:
                continue
        # endfor
        time.sleep(1)
    # endfor
    
    # Close driver
    driver.close()
    # Close file
    f_out.close()
# enddef


# Main
if __name__ == "__main__":
    parser  = argparse.ArgumentParser()
    parser.add_argument("--fout",   help="output file", type=str, default=None)
    args    = parser.parse_args()

    if not args.__dict__["fout"]:
        print "--fout is required !!"
        sys.exit(-1)
    # endif

    main_thread(args.__dict__["fout"])
# endif
