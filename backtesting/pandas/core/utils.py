import pandas as pd
import numpy as np
import quantstats as qs
from   modules.utils import *
from   memoization import cached

##########################################################
# Decorators
# @Cached decorator captures return values of functions decorated with
# and also caches them
def Cached(f):
    Cached.data = {}
    @cached
    def _d(*args, **kwargs):
        value = f(*args, **kwargs)
        Cached.data[f.__name__] = value
        return value
    # enddef
    return _d
# enddef


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
