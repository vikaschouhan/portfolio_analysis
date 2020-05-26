import pandas as pd
import numpy as np
import talib
from   memoization import cached
from   typing import AnyStr, Callable
from   .utils import Cached
from   cymodules.numpy_ext import *

#######################################
def ind_fixed_stop(pos_avg_price: pd.Series, pos: pd.Series, x: float) -> pd.Series:
    return pos_avg_price + pos*x
# enddef

def ind_fixed_perc_stop(pos_avg_price:pd.Series, pos:pd.Series, x: float) -> pd.Series:
    return pos_avg_price * (1 + pos*x/100)
# enddef

def ind_trail_fixed_stop(pos: pd.Series, price: pd.Series, x: float) -> pd.Series:
    return pd.Series(np_trail_fixed_stop(pos.to_numpy(), price.to_numpy(), x), index=pos.index)
# enddef

def ind_trail_perc_stop(pos: pd.Series, price: pd.Series, x: float) -> pd.Series:
    return pd.Series(np_trail_perc_stop(pos.to_numpy(), price.to_numpy(), x), index=pos.index)
# enddef

def ind_atr_perc_stop(pos: pd.Series, price: pd.Series, atr: pd.Series, mult: float=1.0) -> pd.Series:
    return price + pos*atr*mult
# enddef
