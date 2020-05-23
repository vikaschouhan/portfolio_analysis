import pandas as pd
import numpy as np
import quantstats as qs
from   modules.utils import *

#############################################################
# Pandas utility functions
def fillna(df):
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    return df
# enddef

def sanitize_datetime(df):
    df.index = pd.to_datetime(df.index)
    return df
# enddef

#########################################################
# Quantstrat based tearsheet generator
def generate_tearsheet(rets, out_file):
    qs.reports.html(rets, output=out_file)
# enddef

def generate_basic_report(rets):
    qs.reports.metrics(rets)
# enddef
