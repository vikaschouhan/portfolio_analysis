import pandas as pd

#######################################
# Moving average based signals
def ema(s, window):
    return s.ewm(span=window, adjust=False).mean()
# enddef

def sma(s, window):
    return s.rolling(window).mean()
# enddef
