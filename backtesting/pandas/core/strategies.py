import pandas as pd
from   .indicators import *
from   .utils import *

#####################################################################
# MA CrossOvers
def __select_ma_fn(ma_type):
    if ma_type == 'ema':
        return ema
    elif ma_type == 'sma':
        return sma
    else:
        raise ValueError('ERROR:: Unsupported ma_type = {}'.format(ma_type))
    # endif
# enddef

def __ma_crossover(ma_type: str, prices: Price, **params):
    short_period = params.get('short_period')
    long_period  = params.get('long_period')
    price_key    = params.get('price_key', 'close')
    ma_fn        = __select_ma_fn(ma_type)

    short_ma = ma_fn(prices[price_key], short_period)
    long_ma  = ma_fn(prices[price_key], long_period)

    buy_sig  = crossover(short_ma, long_ma)
    sell_sig = crossunder(short_ma, long_ma)

    buy_sig  = set_buy(buy_sig)
    sell_sig = set_sell(sell_sig)
    signals  = pd.concat([buy_sig, sell_sig], axis=1)
    return signals
# enddef

def sma_crossover(prices: Price, **params):
    return __ma_crossover('sma', prices, **params)
# enddef

def ema_crossover(prices: Price, **params):
    return __ma_crossover('ema', prices, **params)
# enddef

#########################################################################
# Supertrend based
def supertrend_cross(prices: Price, **params):
    atr_period     = params.get('atr_period')
    atr_multiplier = params.get('atr_multiplier')

    strend_sig     = supertrend(prices['high'], prices['low'], prices['close'], atr_period, atr_multiplier)
    buy_sig        = crossover(prices['close'], strend_sig)
    sell_sig       = crossunder(prices['close'], strend_sig)

    buy_sig        = set_buy(buy_sig)
    sell_sig       = set_sell(sell_sig)
    signals        = pd.concat([buy_sig, sell_sig], axis=1)
    return signals
# enddef
