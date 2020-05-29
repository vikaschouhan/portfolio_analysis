import pandas as pd
import numpy as np
import talib
import copy
from   memoization import cached
from   typing import AnyStr, Callable
from   .utils import Cached
from   cymodules.numpy_ext import *

#######################################
def ind_fixed_stop(pos_avg_price: pd.Series, pos: pd.Series, x: float) -> pd.Series:
    return pos_avg_price - pos*x
# enddef

def ind_fixed_perc_stop(pos_avg_price: pd.Series, pos: pd.Series, x: float) -> pd.Series:
    return pos_avg_price * (1 - pos*x/100)
# enddef

def ind_trail_fixed_stop(pos: pd.Series, price: pd.Series, x: float) -> pd.Series:
    return pd.Series(np_trail_fixed_stop(pos.to_numpy(), price.to_numpy(), x), index=pos.index)
# enddef

def ind_trail_perc_stop(pos: pd.Series, price: pd.Series, x: float) -> pd.Series:
    return pd.Series(np_trail_perc_stop(pos.to_numpy(), price.to_numpy(), x), index=pos.index)
# enddef

def ind_atr_perc_stop(pos: pd.Series, price: pd.Series, atr: pd.Series, mult: float=1.0) -> pd.Series:
    return price - pos*atr*mult
# enddef

###############################################################
# Misc functions
# For combining main positions with stop loss signals
def combine_pos_with_sl_signals(pos: pd.Series, sl_sig: pd.Series) -> pd.Series:
    return pd.Series(np_combine_pos_and_sl_signals(pos.to_numpy(), sl_sig.to_numpy()), index=pos.index)
# enddef

# shift=True since, positions are to be taken on next bar
def generate_sl_signals(pos: pd.Series, price: pd.Series, sl_price: pd.Series, shift: bool=True) -> pd.Series:
    sl_mult    = pos * (-1)
    pos_mult   = pos

    sl_sigs = ((price*pos_mult + sl_price*sl_mult) < 0).astype('float')
    sl_sigs = sl_sigs.shift().fillna(0.0) if shift else sl_sigs
    return sl_sigs
# enddef
