import pandas as pd
import numpy as np
import talib

#######################################
# Moving average based signals
def ema(s, window):
    return s.ewm(span=window, adjust=False).mean()
# enddef

def sma(s, window):
    return s.rolling(window).mean()
# enddef

########################################
# 
def supertrend(high, low, close, atr_period, atr_multiplier):
    atr_t  = talib.ATR(high, low, close, timeperiod=atr_period)
    avg_t  = (high + low)/2
    bas_u  = avg_t - atr_multiplier * atr_t
    bas_l  = avg_t + atr_multiplier * atr_t
    f_up   = np.zeros_like(close)
    f_down = np.zeros_like(close)
    strend = np.zeros_like(close)
    tpos   = np.zeros_like(close)

    for i, _ in enumerate(close):
        if i == 0:
            continue
        # endif

        f_up[i]    = max(bas_u[i], f_up[i-1]) if close[i-1] > f_up[i-1] else bas_u[i]
        f_down[i]  = min(bas_l[i], f_down[i-1]) if close[i-1] < f_down[i-1] else bas_l[i]
        tpos[i]    = 1.0 if close[i] > f_down[i-1] else -1.0 if close[i] < f_up[i-1] else tpos[i-1]
        strend[i]  = f_up[i] if tpos[i] == 1.0 else f_down[i] if tpos[i] == -1.0 else strend[i-1]
    # endfor

    return strend, f_up, f_down
# endclass
