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
    print_params(params)

    short_period = params_get(params, 'short_period')
    long_period  = params_get(params, 'long_period')
    price_key    = params_get(params, 'price_key', Price.CLOSE)
    ma_fn        = __select_ma_fn(ma_type)

    short_ma = ma_fn(prices[price_key], short_period)
    long_ma  = ma_fn(prices[price_key], long_period)

    buy_sig  = crossover(short_ma, long_ma)
    sell_sig = crossunder(short_ma, long_ma)

    buy_sig  = set_buy(buy_sig)
    sell_sig = set_sell(sell_sig)
    signals  = pd.concat([buy_sig, sell_sig], axis=1)

    # Attach additional signals
    signals['0_short_ma'] = short_ma
    signals['0_long_ma']  = long_ma
    signals['0_price']    = prices[price_key]
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
def supertrend_crossover(prices: Price, **params):
    print_params(params)

    atr_period     = params_get(params, 'atr_period')
    atr_multiplier = params_get(params, 'atr_multiplier')
    ema_length     = params_get(params, 'ema_length', None)
    atr_max        = params_get(params, 'atr_max', None)
    price_key      = params_get(params, 'price_key', Price.CLOSE)

    if ema_length:
        print('>> Using EMA Smooth variant of supertrend_crossover.')
        phigh      = ema(prices[Price.HIGH], ema_length)
        plow       = ema(prices[Price.LOW], ema_length)
    else:
        phigh      = prices[Price.HIGH]
        plow       = prices[Price.LOW]
    # endif

    # Choose atr calculation function
    atr_fn         = None
    if atr_max:
        atr_fn     = vatr1_fn(atr_max)
        print('>> Using Vol adjusted ATR fn {} for atr_max={}'.format(atr_fn, atr_max))
    # endif

    strend_sig     = supertrend(phigh, plow, prices[price_key], atr_period, atr_multiplier, atr_fn=atr_fn)
    buy_sig        = crossover(prices[price_key], strend_sig)
    sell_sig       = crossunder(prices[price_key], strend_sig)

    buy_sig        = set_buy(buy_sig)
    sell_sig       = set_sell(sell_sig)
    signals        = pd.concat([buy_sig, sell_sig], axis=1)

    signals['0_strend'] = strend_sig
    signals['0_price']  = prices[price_key]
    return signals
# enddef

#####################################################################
# Strat map
strat_map = {
        'ema_crossover'            : ema_crossover,
        'sma_crossover'            : sma_crossover,
        'supertrend_crossover'     : supertrend_crossover,
    }
