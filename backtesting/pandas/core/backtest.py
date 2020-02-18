from .indicators import *
from .strategies import *
from .utils import *

##############################################################################
# Run backtest strategy on single instrument.
#
# @args 
#      strat_fn   -> strategy fn of format (prices, **params) where prices is of Price type
#      strat_params -> params for strategy_fn (python dictionary)
#      prices     -> price data of "Price" type
#      run_mode   -> 'any' means run both long and short.
#                    'long' means long only positions
#                    'short' means short only positions
#      slippage   -> slippage as percentage of close price
#
def run_strategy_single(strat_fn: Callable, strat_params: dict, prices: Price, run_mode: str='any', slippage: float=0.0):
    signals = strat_fn(prices, **strat_params)

    # Select appropriate signals first
    buy_sig = sell_sig = short_sig = cover_sig = None
    if SIGNAL.SHORT in signals.columns and SIGNAL.COVER in signals.columns:
        short_sig = SIGNAL.SHORT
        cover_sig = SIGNAL.COVER
    # endif
    if SIGNAL.BUY in signals.columns and SIGNAL.SELL in signals.columns:
        buy_sig   = SIGNAL.BUY
        sell_sig  = SIGNAL.SELL
    # endif

    if None in [buy_sig, sell_sig] and None in [short_sig, cover_sig]:
        raise ValueError('ERROR:: Signal from {} should have either {} of {} defined.'.format(strat_fn, SIGNAL_MASK_LONG, SIGNAL_MASK_SHORT))
    # endif

    if run_mode == 'any':
        buy_sig   = buy_sig if buy_sig else cover_sig
        sell_sig  = sell_sig if sell_sig else short_sig
        short_sig = short_sig if short_sig else sell_sig
        cover_sig = cover_sig if cover_sig else buy_sig
        smask     = (buy_sig, sell_sig, short_sig, cover_sig)
    elif run_mode == 'long':
        buy_sig   = buy_sig if buy_sig else cover_sig
        sell_sig  = sell_sig if sell_sig else short_sig
        smask     = (buy_sig, sell_sig)
    elif run_mode == 'short':
        short_sig = short_sig if short_sig else sell_sig
        cover_sig = cover_sig if cover_sig else buy_sig
        smask     = (short_sig, cover_sig)
    # endif

    print('>> Using signal mask {}.'.format(smask))
    pos     = signals_to_positions(signals, mode=run_mode, mask=smask)
    pos     = apply_slippage(pos, slippage)
    rets    = np.log(prices['close']).diff()
    nrets   = rets * pos

    return nrets
# enddef
