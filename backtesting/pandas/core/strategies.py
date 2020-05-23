import pandas as pd
from   .indicators import *
from   .utils import *
from   .lines import *
from   .signals import *
from   .ops import *

#####################################################################
# MA CrossOvers
def __select_ma_fn(ma_type):
    if ma_type == 'ema':
        return ind_ema
    elif ma_type == 'sma':
        return ind_sma
    else:
        raise ValueError('ERROR:: Unsupported ma_type = {}'.format(ma_type))
    # endif
# enddef

def __ma_crossover(ma_type: str, prices: Ohlcv, **params):
    print_params(params)

    short_period = params_get(params, 'short_period')
    long_period  = params_get(params, 'long_period')
    price_key    = params_get(params, 'price_key', Ohlcv.CLOSE)
    ma_fn        = __select_ma_fn(ma_type)

    short_ma = ma_fn(prices[price_key], short_period)
    long_ma  = ma_fn(prices[price_key], long_period)

    buy_sig  = op_crossover(short_ma, long_ma)
    sell_sig = op_crossunder(short_ma, long_ma)

    buy_sig  = set_buy(buy_sig)
    sell_sig = set_sell(sell_sig)
    signals  = pd.concat([buy_sig, sell_sig], axis=1)

    # Attach additional signals
    signals['0_short_ma'] = short_ma
    signals['0_long_ma']  = long_ma
    signals['0_price']    = prices[price_key]
    return signals
# enddef

def strat_sma_crossover(prices: Ohlcv, **params):
    return __ma_crossover('sma', prices, **params)
# enddef

def strat_ema_crossover(prices: Ohlcv, **params):
    return __ma_crossover('ema', prices, **params)
# enddef

#########################################################################
# Supertrend based
def strat_supertrend_crossover(prices: Ohlcv, **params):
    print_params(params)

    atr_period     = params_get(params, 'atr_period')
    atr_multiplier = params_get(params, 'atr_multiplier')
    ema_length     = params_get(params, 'ema_length', None)
    atr_max        = params_get(params, 'atr_max', None)
    price_key      = params_get(params, 'price_key', Ohlcv.CLOSE)

    if ema_length:
        print('>> Using EMA Smooth variant of supertrend_crossover.')
        phigh      = ind_ema(prices[Ohlcv.HIGH], ema_length)
        plow       = ind_ema(prices[Ohlcv.LOW], ema_length)
    else:
        phigh      = prices[Ohlcv.HIGH]
        plow       = prices[Ohlcv.LOW]
    # endif

    # Choose atr calculation function
    atr_fn         = None
    if atr_max:
        atr_fn     = vatr1_fn(atr_max)
        print('>> Using Vol adjusted ATR fn {} for atr_max={}'.format(atr_fn, atr_max))
    # endif

    strend_sig     = ind_supertrend(phigh, plow, prices[price_key], atr_period, atr_multiplier, atr_fn=atr_fn)
    buy_sig        = op_crossover(prices[price_key], strend_sig)
    sell_sig       = op_crossunder(prices[price_key], strend_sig)

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
        'ema_crossover'            : strat_ema_crossover,
        'sma_crossover'            : strat_sma_crossover,
        'supertrend_crossover'     : strat_supertrend_crossover,
    }
