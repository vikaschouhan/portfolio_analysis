import json
import pprint
import sys
import re
import urllib, urllib2, json
import socket
import datetime
import pandas
import argparse
import copy
import time
import os
import math
import csv
import contextlib, warnings
import shutil
from   colorama import Fore, Back, Style
import datetime as datetime
import numpy as np
import logging
from   subprocess import call, check_call
import requests
from   bs4 import BeautifulSoup

########################################################
# For EMAIL
def send_email(user, pwd, recipient, body='', subject="Sent from sim_stk_ind.py", attachments=[]):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = user
    msg['To']      = recipient
    msg.attach(MIMEText(TEXT, 'plain'))

    # Add all attachments 
    for a_this in attachments:
        with open(a_this,'rb') as fp:
            att = MIMEApplication(fp.read())
            att.add_header('Content-Disposition', 'attachment', filename=a_this)
            msg.attach(att)
        # endwith
    # endfor
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        print "Mail sent to {} at {}".format(recipient, datetime.datetime.now())
    except:
        print "Failed to send the mail !!"
# enddef
