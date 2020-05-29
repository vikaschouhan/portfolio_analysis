from .indicators import *
from .strategies import *
from .utils import *

##############################################################################
# Run backtest strategy on single instrument.
#
# @args 
#      strat_fn   -> strategy fn of format (prices, **params) where prices is of Ohlcv type
#      strat_params -> params for strategy_fn (python dictionary)
#      prices     -> price data of "Ohlcv" type
#      run_mode   -> 'any' means run both long and short.
#                    'long' means long only positions
#                    'short' means short only positions
#      slippage   -> slippage
def run_strategy_single(strat_fn: Callable, strat_params: dict, prices: Ohlcv, run_mode: str='any', slippage: str='0.0%'):
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
    pos     = signals_to_positions(signals, mode=run_mode, mask=smask, use_vec=True)
    rets    = np.log(prices[Ohlcv.CLOSE]).diff()
    nrets   = apply_slippage_v2(pos, rets, slippage, ret_type='log', price=prices[Ohlcv.CLOSE])
    pavgp   = positions_to_avg_position_price(pos, price=prices[Ohlcv.OPEN], mode=run_mode)
    nrets   = sanitize_datetime(nrets)
    points  = (np.exp(nrets.sum()) - 1) * prices[Ohlcv.CLOSE][0]

    return {
               KEY_RETURNS     : nrets,
               KEY_POSITIONS   : pos,
               KEY_SIGNALS     : signals,
               KEY_PRICES      : prices,
               KEY_RUNMODE     : run_mode,
               KEY_SLIPPAGE    : slippage,
               KEY_NPOINTS     : points,
               KEY_PAVG_PRICE  : pavgp
           }
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
#        slippage         -> slippage
def backtest_single(strategy: str,
        strat_params: dict,
        prices: pd.DataFrame,
        report_file: str=None,
        columns: str='ohlcv',
        run_mode: str='any',
        slippage: str='0.0%'):
    assert strategy in strat_map, 'ERROR:: Supported strategies = {}'.format(strat_map.keys())
    strat_fn   = strat_map[strategy]

    print('>> Preparing price data.')
    _prices    = Ohlcv(prices, columns)
    print('>> Running strategy "{}" on price data.'.format(strategy))
    ret_data   = run_strategy_single(strat_fn, strat_params, _prices, run_mode, slippage)
    if report_file:
        print('>> Writing tearsheet to {}'.format(report_file))
        generate_tearsheet(ret_data[KEY_RETURNS], report_file)
    # endif

    ext_data   = {
            KEY_PRICES            : _prices,
            KEY_STRATEGY          : strategy,
            KEY_STRATPARAMS       : strat_params,
            KEY_RUNMODE           : run_mode,
            KEY_SLIPPAGE          : slippage,
        }
    return {**ret_data, **ext_data}
# enddef
