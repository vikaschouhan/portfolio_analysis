import pandas as pd
import numpy as np
import talib
from   memoization import cached
from   typing import AnyStr, Callable
from   .utils import Cached
from   cymodules.numpy_ext import *

#######################################
def ind_fixed_loss(pos_avg_price: pd.Series, pos: pd.Series, x: float) -> pd.Series:
    return pos_avg_price + pos*x
# enddef

def ind_fixed_perc_loss(pos_avg_price:pd.Series, pos:pd.Series, x: float) -> pd.Series:
    return pos_avg_price * (1 + pos*x/100)
# enddef

def ind_trail_fixed_loss(pos: pd.Series, price: pd.Series, x: float) -> pd.Series:
    _loss = np_trail_fixed_loss(pos.to_numpy(), price.to_numpy(), x)

    return pd.Series(_loss, index=pos.index)
# enddef
