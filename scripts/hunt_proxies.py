#!/usr/bin/env python

import requests
from   requests.exceptions import ConnectionError
import socket
import struct
import nmap
import argparse
import sys
import re

class ValidProxy(Exception):
    pass

def ips(start, end):
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0] + 1
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]

parser  = argparse.ArgumentParser()
parser.add_argument("--ip_range", help="ip_range.", type=str, default=None)
parser.add_argument("--ip_file",  help="ip_range file", type=str, default=None)
parser.add_argument("--ip_out",   help="ip output file", type=str, default=None)
args    = parser.parse_args()

if not args.__dict__["ip_range"] and not args.__dict__["ip_file"]:
    print "At least one option is required !!"
    sys.exit(-1)
# endif
if args.__dict__["ip_range"] and args.__dict__["ip_file"]:
    print "--ip_range and --ip_file can't be passed simultaneously !!"
    sys.exit(-1)
# endif
if not args.__dict__["ip_out"]:
    print "--ip_out is required !!"
    sys.exit(-1)
# endif

# Empty range list
ip_range_list = []
if args.__dict__["ip_file"]:
    fin = args.__dict__["ip_file"]
    for item in fin:
        ip_range_list.apppend(item)
    # endfor
    fin.close()
else:
    ip_range_list.append(args.__dict__["ip_range"])
# endif

# Open output file
ip_out = open(args.__dict__["ip_out"], "a+")

# Iterate over all ranges
for rng_this in ip_range_list:
    #ip_3    = "183.218.54"
    #ip_3    = args.__dict__["ip_base"]
    #rng_4   = range(256)
    rng_s   = rng_this.replace(" ", "").split("-")
    rng_4   = ips(rng_s[0], rng_s[1])
    #ports   = "80,808,8080,8081,8084,8088,8089,8118,8123,1080,3128,3389,9000,18628"
    ports   = "80-90,443,808,843,900,8080-8090,8100-8200,1080,3128,3389,9000,18628,1111,2222,3333,4444,5555,6666,7777,8888,9999,12980,18000"
    #ports    = "*"
    scanner = nmap.PortScanner()
    #tip_l   = [ "http://screener.in", "https://screener.in" ]
    tip_l   = [ "http://www.screener.in", "https://www.screener.in" ]
    title   = r'Screener.in'
    #test_ip = "http://www.screener.in"
    
    # Iterate ip by ip
    for indx in rng_4:
        #ip_this = ip_3 + ".{}".format(indx)
        ip_this = indx
        sys.stdout.write("{}".format("+"))
        sys.stdout.flush()
    
        res     = scanner.scan(hosts=ip_this, ports=ports, arguments="--open")
    
        # If no open ports were found, continue
        if len(res["scan"]) == 0:
            continue
        # endif
   
        try:
            for port_this in res["scan"].values()[0]["tcp"]:
                sys.stdout.write("..")
                sys.stdout.flush()
                proxy_this = "{}:{}".format(ip_this, port_this)
                proxy_dict = {
                                 "http"  : proxy_this,
                                 "https" : proxy_this,
                             }
                headers    = {
                                 "User-Agent" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)' + \
                                                ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
                             }
                for j_ip in tip_l:
                    try:
                        r      = requests.get(j_ip, proxies=proxy_dict, headers=headers)
                        # If page was returned allright and title was found in the document,
                        # try to read my external ip.
                        if r.ok == True:
                            ri = requests.get("http://jsonip.com", proxies=proxy_dict, headers=headers)
                            ip = ri.json()['ip']
                            ri.close()
                            r.close()
                            print "\nValid proxy : {} for {}. Public ip : {}".format(proxy_this, j_ip, ip)
                            ip_out.write(proxy_this)
                            ip_out.write("\n")
                            ip_out.flush()
                            raise ValidProxy()
                        # endif
                    except ConnectionError:
                        continue
                    except ValueError:
			            # Couldn't open JSONIP.COM means it was a bogus ip, raise exception
			            pass
    	            # Python bug http://bugs.python.org/issue17849
    	            except TypeError:
    	                continue
                # endfor
            # endfor
        # Catch exceptions
        except ValidProxy:
            continue
    # endfor
# endfor

# Close output file handle
ip_out.close()
