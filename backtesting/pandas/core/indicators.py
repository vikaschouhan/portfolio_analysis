import pandas as pd
import numpy as np
import talib
from   memoization import cached
from   typing import AnyStr
from   .utils import Cached
from   cymodules.numpy_ext import *

######################################
# Indicators
def ind_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int) -> pd.Series:
    return pd.Series(talib.ATR(high.to_numpy(), low.to_numpy(), close.to_numpy(), window), index=high.index).fillna(0.0)
# enddef

def ind_ema(s: pd.Series, window: int) -> pd.Series:
    return s.ewm(span=window, adjust=False).mean().fillna(0.0)
# enddef

def ind_sma(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window).mean().fillna(0.0)
# enddef

def ind_supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
        atr_period: int, atr_multiplier: float) -> pd.Series:
    # Calculate atr
    atr_t  = ind_atr(high, low, close, atr_period)

    return pd.Series(np_ind_supertrend(high.to_numpy(),
            low.to_numpy(), close.to_numpy(), atr_t.to_numpy(), atr_multiplier), index=high.index).fillna(0.0)
# endclass

# high, low, close, open are higher timeframe prices.
def ind_pivots_classic(open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.DataFrame:
    pi_level       = (high + low + close)/3
    bc_level       = (high + low)/2
    tc_level       = (pi_level - bc_level) + pi_level
    r1_level       = pi_level * 2 - low
    s1_level       = pi_level * 2 - high
    r2_level       = (pi_level - s1_level) + r1_level
    s2_level       = pi_level - (r1_level - s1_level)

    return pd.DataFrame({
        'pi' : pi_level, 'tc' : tc_level, 'bc' : bc_level,
        'r1' : r1_level, 's1' : s1_level,
        'r2' : r2_level, 's2' : s2_level,
        'hi' : high,     'lo' : low
    })
# enddef

def ind_pivots_fib(open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.DataFrame:
    PP = (high + low + close)/3
    R1 = PP + 0.382*(high - low)
    S1 = PP - 0.382*(high - low)
    R2 = PP + 0.618*(high - low)
    S2 = PP - 0.618*(high - low)
    R3 = PP + (high - low)
    S3 = PP - (high - low)

    return pd.DataFrame({
        'pi' : PP,
        'r1' : R1,   's1' : S1,
        'r2' : R2,   's2' : S2,
        'r3' : R3,   's3' : S3,
        'hi' : high, 'lo' : low,
    })
# enddef
