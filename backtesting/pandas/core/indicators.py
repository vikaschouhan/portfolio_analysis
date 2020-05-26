import pandas as pd
import numpy as np
import talib
from   memoization import cached
from   typing import AnyStr
from   .utils import Cached
from   cymodules.numpy_ext import *

######################################
# Indicators
@Cached
def ind_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int) -> pd.Series:
    return pd.Series(talib.ATR(high.to_numpy(), low.to_numpy(), close.to_numpy(), window), index=high.index).fillna(0.0)
# enddef

@Cached
def ind_ema(s: pd.Series, window: int) -> pd.Series:
    return s.ewm(span=window, adjust=False).mean().fillna(0.0)
# enddef

@Cached
def ind_sma(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window).mean().fillna(0.0)
# enddef

@Cached
def ind_supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
        atr_period: int, atr_multiplier: float) -> pd.Series:
    # Calculate atr
    atr_t  = ind_atr(high, low, close, atr_period)

    return pd.Series(np_ind_supertrend(high.to_numpy(),
            low.to_numpy(), close.to_numpy(), atr_t.to_numpy(), atr_multiplier), index=high.index).fillna(0.0)
# endclass
