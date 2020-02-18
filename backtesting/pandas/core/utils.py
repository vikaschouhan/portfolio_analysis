import pandas as pd
import numpy as np
import quantstats as qs
from   typing import AnyStr, Callable

############################################################
# Constants
class SIGNAL:
    BUY    = 'Buy'
    SELL   = 'Sell'
    SHORT  = 'Short'
    COVER  = 'Cover'
# endclass

# Various kinds of Masks, depending on the naming convention used to define
# Signals
SIGNAL_MASK        = (SIGNAL.BUY, SIGNAL.SELL, SIGNAL.SHORT, SIGNAL.COVER)
SIGNAL_MASK2       = (SIGNAL.BUY, SIGNAL.SELL, SIGNAL.SELL, SIGNAL.BUY)
SIGNAL_MASK_LONG   = (SIGNAL.BUY, SIGNAL.SELL)
SIGNAL_MASK_SHORT  = (SIGNAL.SHORT, SIGNAL.COVER)
SIGNAL_MASK_SHORT2 = (SIGNAL.SELL, SIGNAL.BUY)

#############################################################
# Signal utility functions
def crossover(s1, s2, lag=1):
    return (s1 > s2) & (s1.shift(lag) < s2.shift(lag))
# enddef

def crossunder(s1, s2, lag=1):
    return (s1 < s2) & (s1.shift(lag) > s2.shift(lag))
# enddef

def set_buy(s):
    s.name = SIGNAL.BUY
    return s
# enddef

def set_sell(s):
    s.name = SIGNAL.SELL
    return s
# enddef

def set_short(s):
    s.name = SIGNAL.SHORT
# enddef

def set_cover(s):
    s.name = SIGNAL.COVER
# enddef

#############################################################
# Pandas utility functions
def fillna(df):
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    return df
# enddef

################################################################
# For handling price data
class Price(object):
    keys_list = ['open', 'high', 'low', 'close', 'volume', 'all']

    def __init__(self, open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series = None):
        volume      = pd.Series(0, index=close.index) if volume is None else volume
        open.name   = 'open'
        close.name  = 'close'
        high.name   = 'high'
        low.name    = 'low'
        volume.name = 'volume'
        self.data = pd.DataFrame([close, open, high, low, volume]).T
    # enddef

    def __getitem__(self, key):
        if key in ['open', 'high', 'low', 'close', 'volume']:
            return self.data[key]
        elif key == 'all':
            return self.data
        else:
            raise ValueError('Unsupported key {} in Price[]. Supported keys are = {}'.format(key, self.keys_list))
        # endif
    # enddef
# endclass

############################################################
# Singnals to Position Generator
def _take_position_any(sig, pos, long_en, long_ex, short_en, short_ex):
    # check exit signals
    if pos != 0:  # if in position
        if pos > 0 and sig[long_ex]:  # if exit long signal
            pos -= sig[long_ex]
        elif pos < 0 and sig[short_ex]:  # if exit short signal
            pos += sig[short_ex]
        # endif
    # endif
    # check entry (possibly right after exit)
    if pos == 0:
        if sig[long_en]:
            pos += sig[long_en]
        elif sig[short_en]:
            pos -= sig[short_en]
        # endif
    # endif

    return pos
# enddef

def _take_position_long(sig, pos, long_en, long_ex):
    # check exit signals
    if pos != 0:  # if in position
        if pos > 0 and sig[long_ex]:  # if exit long signal
            pos -= sig[long_ex]
        # endif
    # endif
    # check entry (possibly right after exit)
    if pos == 0:
        if sig[long_en]:
            pos += sig[long_en]
        # endif
    # endif

    return pos
# enddef

def _take_position_short(sig, pos, short_en, short_ex):
    # check exit signals
    if pos != 0:  # if in position
        if pos < 0 and sig[short_ex]:  # if exit short signal
            pos += sig[short_ex]
        # endif
    # endif
    # check entry (possibly right after exit)
    if pos == 0:
        if sig[short_en]:
            pos -= sig[short_en]
        # endif
    # endif

    return pos
# enddef

def _check_signals_to_positions_args(mode, pos_type, mask):
    mode_list = ['long', 'short', 'any']
    pos_types = ['full', 'sparse']

    assert mode in mode_list, 'ERROR:: mode should be one of {}'.format(mode_list)
    assert pos_type in pos_types, 'ERROR:: pos_type should be one of {}'.format(pos_types)
    if mode == 'any':
        assert len(mask) == 4 , 'ERROR:: in "any" mode, mask should be of 4 keys.'
    # endif
    assert len(mask) == 2 or len(mask) == 4, 'ERROR:: mask should be of 2 or 4 keys.'
# enddef

def signals_to_positions(signals, init_pos=0, mode='any',
        mask=SIGNAL_MASK, pos_type='full'):
    # Checks
    _check_signals_to_positions_args(mode, pos_type, mask)

    pos = init_pos
    ps  = pd.Series(0., index=signals.index)

    if mode == 'any':
        long_en, long_ex, short_en, short_ex = mask
        for t, sig in signals.iterrows():
            pos   = _take_position_any(sig, pos, long_en, long_ex, short_en, short_ex)
            ps[t] = pos
        # endfor
    elif mode == 'long':
        long_en, long_ex = mask
        for t, sig in signals.iterrows():
            pos   = _take_position_long(sig, pos, long_en, long_ex)
            ps[t] = pos
        # endfor
    elif mode == 'short':
        short_en, short_ex = mask
        for t, sig in signals.iterrows():
            pos   = _take_position_short(sig, pos, short_en, short_ex)
            ps[t] = pos
        # endfor
    # endif
    ps = ps.shift()
    return ps[ps != ps.shift()] if pos_type == 'sparse' else ps
# enddef

########################################################
# Calculate returns for a portfolio of assets given their
# individual returns
def calculate_portfolio_returns(returns, weights_list, log_returns=True):
    assert isinstance(returns, pd.DataFrame), 'ERROR::: returns should be a pandas dataframe of individual asset returns'
    assert len(returns.columns) == len(weights_list), 'ERROR:: Dimensions of weights_list should match that of number of columns in returns.'

    crets = np.log(np.dot(np.exp(returns), weights_list)) if log_returns else np.dot(returns, weights_list)
    return pd.Series(crets, index=returns.index)
# enddef

########################################################
# Slippage calculator
def apply_slippage(pos, slip_perc=0):
    # Apply slippage
    pos_slip = (1-0.01*slip_perc)
    neg_slip = (1+0.01*slip_perc)
    new_pos  = pos * pos.diff().apply(lambda x : pos_slip if x>0 else neg_slip if x<0 else 1)
    return new_pos
# enddef

#########################################################
# Quantstrat based tearsheet generator
def generate_tearsheet(rets, out_file):
    qs.reports.html(rets, output=out_file)
# enddef
