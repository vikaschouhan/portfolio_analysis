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
#      ret_pos    -> if True, also returns position vector. Useful for debugging
def run_strategy_single(strat_fn: Callable, strat_params: dict, prices: Price, run_mode: str='any',
        slippage: float=0.0, ret_pos: bool=False):
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
    rets    = np.log(prices['close']).diff()
    nrets   = apply_slippage(pos, rets, slippage, ret_type='log')
    nrets   = sanitize_datetime(nrets)

    if ret_pos:
        return nrets, pos
    # endif
    return nrets
# enddef

############################################################################
# Backtest a strategy on single asset
# @args
#        startegy         -> strategy name
#        strat_params     -> A dictionary of strategy parameters
#        prices           -> Dataframe of price information
#        report_file      -> Report file to be generated for the backtest
#        column_map       -> A dictionary of column mappings
#        run_mode         -> 'any' for both long and short, 'long' for long only
#                            'short' for short only
#        slippage         -> slippage in %centage
def backtest_single(strategy: str,
        strat_params: dict,
        prices: pd.DataFrame,
        report_file: str=None,
        column_map: dict={'close': 'c', 'low': 'l', 'high': 'h', 'open': 'o', 'volume': 'v'},
        run_mode: str='any',
        slippage: float=0.0):
    assert strategy in strat_map, 'ERROR:: Supported strategies = {}'.format(strat_map.keys())
    strat_fn   = strat_map[strategy]

    # Get appropriate columns in prirce data
    _o = column_map['open']
    _h = column_map['high']
    _l = column_map['low']
    _c = column_map['close']
    _v = column_map['volume']

    print('>> Preparing price data.')
    _prices    = Price(prices[_o], prices[_h], prices[_l], prices[_c], prices[_v])
    print('>> Running strategy "{}" on price data.'.format(strategy))
    returns    = run_strategy_single(strat_fn, strat_params, _prices, run_mode, slippage)
    if report_file:
        print('>> Writing tearsheet to {}'.format(report_file))
        generate_tearsheet(returns, report_file)
    # endif
    return returns
# enddef
