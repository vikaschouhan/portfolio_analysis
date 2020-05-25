import pandas as pd
import numpy as np
import talib
from   memoization import cached
from   typing import AnyStr, Callable
from   .utils import Cached

#######################################
# Derivatives
def vatr1_fn(atr_max):
    def __catr(high, low, close, timeperiod):
        return 2*atr_max - talib.ATR(high, low, close, timeperiod=timeperiod)
    # endef
    return __catr
# enddef

######################################
# Indicators
@Cached
def ind_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int) -> pd.Series:
    return pd.Series(talib.ATR(high.to_numpy(), low.to_numpy(), close.to_numpy(), window), index=high.index)
# enddef

@Cached
def ind_ema(s: pd.Series, window: int) -> pd.Series:
    return s.ewm(span=window, adjust=False).mean()
# enddef

@Cached
def ind_sma(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window).mean()
# enddef

@Cached
def ind_supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
        atr_period: int, atr_multiplier: float, atr_fn: Callable=None) -> pd.Series:
    # To numpy
    index  = close.index
    high   = high.to_numpy()
    low    = low.to_numpy()
    close  = close.to_numpy()

    # Base signals
    atr_fn = atr_fn if atr_fn else talib.ATR
    atr_t  = atr_fn(high, low, close, timeperiod=atr_period)
    avg_t  = (high + low)/2
    bas_u  = avg_t - atr_multiplier * atr_t
    bas_l  = avg_t + atr_multiplier * atr_t
    f_up   = np.zeros_like(close)
    f_down = np.zeros_like(close)
    strend = np.zeros_like(close)
    tpos   = np.zeros_like(close)

    for i, _ in enumerate(close):
        f_up[i]    = max(bas_u[i], f_up[i-1]) if close[i-1] > f_up[i-1] else bas_u[i]
        f_down[i]  = min(bas_l[i], f_down[i-1]) if close[i-1] < f_down[i-1] else bas_l[i]
        tpos[i]    = 1.0 if close[i] > f_down[i-1] else -1.0 if close[i] < f_up[i-1] else tpos[i-1]
        strend[i]  = f_up[i] if tpos[i] == 1.0 else f_down[i] if tpos[i] == -1.0 else strend[i-1]
    # endfor

    return pd.Series(strend, index=index)
# endclass
