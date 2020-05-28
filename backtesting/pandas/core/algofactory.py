from .lines import *
from .indicators import *
from .stops import *
from .ops import *

###################################################################################
# Utils. State maintaining functions/classes
def cstr(*args):
    l = list(filter(None.__ne__, args))
    assert len(l) > 0, '>> ERROR::: At least one string in cstr() should be Non Null !!'
    return '__'.join([str(x) for x in l])
# enddef

class SignalCache(object):
    _signals = {}
    _add_signals = True
    @classmethod
    def signal(cls, key, value=None):
        if value is not None:
            if cls._add_signals:
                cls._signals[key] = value
            # endif
            return value
        else:
            assert key in cls._signals, '>> WARNING:: key={} not found in SignalCache.'.format(key)
            return cls._signals[key]
        # endif
    # enddef
    @classmethod
    def signals(cls):
        return cls._signals
    # enddef
    @classmethod
    def add_ohlcv(cls, ohlcv):
        assert isinstance(ohlcv, Ohlcv), '>> ERROR:: Passed value is not an instance of Ohlcv !!'
        # Clear cache
        cls._signals = {}
        cls._signals['ohlcv'] = ohlcv
    # enddef
    @classmethod
    def get_ohlcv(cls, time_frame=None):
        t_str = cstr('ohlcv',  time_frame)
        if t_str in cls._signals:
            return cls._signals[t_str]
        else:
            assert 'ohlcv' in cls._signals, '>> ERROR:: Please class add_ohlcv() first !!'
            cls._signals[t_str] = cls._signals['ohlcv'].resample(time_frame)
            return cls._signals[t_str]
        # endif
    # enddef
    @classmethod
    def discard_signals(cls):
        cls._add_signals = False
    # enddef
# endclass

def add_ohlcv(v):
    SignalCache.add_ohlcv(v)
# enddef

def add_signal(k, v):
    v.name = k
    return SignalCache.signal(k, v)
# enddef

def disable_signals():
    SignalCache.discard_signals()
# enddef

def check_signal(k):
    return True if k in SignalCache.signals() else False
# enddef

def get_signal(k):
    return SignalCache.signal(k) if k in SignalCache.signals() else None
# enddef

####################################################################################
# All Indicator algos
def close(time_frame=None):
    return add_signal(cstr('close', time_frame),  SignalCache.get_ohlcv(time_frame)[Ohlcv.CLOSE])
# enddef
def high(time_frame=None):
    return add_signal(cstr('high', time_frame), SignalCache.get_ohlcv(time_frame)[Ohlcv.HIGH])
# enddef
def low(time_frame=None):
    return add_signal(cstr('low', time_frame), SignalCache.get_ohlcv(time_frame)[Ohlcv.LOW])
# enddef
def open(time_frame=None):
    return add_signal(cstr('open', time_frame), SignalCache.get_ohlcv(time_frame)[Ohlcv.OPEN])
# enddef
def volume(time_frame=None):
    return add_signal(cstr('volume', time_frame), SignalCache.get_ohlcv(time_frame)[Ohlcv.VOLUME])
# enddef

def ema(period, line=None):
    line_t = close() if line is None else line
    return add_signal(cstr('ema', line_t.name), ind_ema(line_t, period))
# enddef

def sma(period, line=None):
    line_t = close() if line is None else line
    return add_signal(cstr('sma', line_t.name), ind_sma(line_t, period))
# enddef

def supertrend(period, mult, time_frame=None):
    high_t, low_t, close_t = high(time_frame), low(time_frame), close(time_frame)
    return add_signal(cstr('supertrend', time_frame), ind_supertrend(high_t, low_t, close_t, period, mult))
# enddef

def __pivots_classic(time_frame='1D'):
    open_t, high_t, low_t, close_t = open(time_frame), high(time_frame), low(time_frame), close(time_frame)
    pivots_ = add_signal(cstr('pivots_classic', time_frame), ind_pivots_classic(open_t, high_t, low_t, close_t))
    return pivots_
# enddef

def __pivot_classic_x(x, time_frame='1D'):
    pivots_ = get_signal(cstr('pivots_classic', time_frame)) if check_signal(cstr('pivots_classic', time_frame)) \
        else __pivots_classic(time_frame)
    return pivots_[x]
# enddef

def pivot_pi_classic(time_frame='1D'):
    return __pivot_classic_x('pi', time_frame)
def pivot_tc_classic(time_frame='1D'):
    return __pivot_classic_x('tc', time_frame)
def pivot_bc_classic(time_frame='1D'):
    return __pivot_classic_x('bc', time_frame)
def pivot_r1_classic(time_frame='1D'):
    return __pivot_classic_x('r1', time_frame)
def pivot_s1_classic(time_frame='1D'):
    return __pivot_classic_x('s1', time_frame)
def pivot_r2_classic(time_frame='1D'):
    return __pivot_classic_x('r2', time_frame)
def pivot_s2_classic(time_frame='1D'):
    return __pivot_classic_x('s2', time_frame)
def pivot_hi_classic(time_frame='1D'):
    return __pivot_classic_x('hi', time_frame)
def pivot_lo_classic(time_frame='1D'):
    return __pivot_classic_x('lo', time_frame)

def __pivots_fib(time_frame='1D'):
    open_t, high_t, low_t, close_t = open(time_frame), high(time_frame), low(time_frame), close(time_frame)
    pivots_ = add_signal(cstr('pivots_fib', time_frame), ind_pivots_fib(open_t, high_t, low_t, close_t))
    return pivots_
# enddef

def __pivot_fib_x(x, time_frame='1D'):
    pivots_ = get_signal(cstr('pivots_fib', time_frame)) if check_signal(cstr('pivots_fib', time_frame)) \
        else __pivots_fib(time_frame)
    return pivots_[x]
# enddef

def pivot_pi_fib(time_frame='1D'):
    return __pivot_fib_x('pi', time_frame)
def pivot_r1_fib(time_frame='1D'):
    return __pivot_fib_x('r1', time_frame)
def pivot_s1_fib(time_frame='1D'):
    return __pivot_fib_x('s1', time_frame)
def pivot_r2_fib(time_frame='1D'):
    return __pivot_fib_x('r2', time_frame)
def pivot_s2_fib(time_frame='1D'):
    return __pivot_fib_x('s2', time_frame)
def pivot_r3_fib(time_frame='1D'):
    return __pivot_fib_x('r3', time_frame)
def pivot_s3_fib(time_frame='1D'):
    return __pivot_fib_x('s3', time_frame)
def pivot_hi_fib(time_frame='1D'):
    return __pivot_fib_x('hi', time_frame)
def pivot_lo_fib(time_frame='1D'):
    return __pivot_fib_x('lo', time_frame)

def day_change():
    l_chng = SignalCache.get_ohlcv()['date'].day.to_series().diff()
    l_chng[l_chng != 0] = 1.0
    return add_signal(cstr('day_change'), pd.Series(l_chng.values, index=SignalCache.get_ohlcv()['date']))
# enddef

def __orb(time_frame='15min'):
    # day_change signal
    d_chng_ = day_change()
    # Advance day_change signal by number of minutes in orb timeframe
    d_chng_.index += pd.to_timedelta(time_frame)
    
    # Get new orb timeframe high low
    high_ntf_ = high(time_frame)
    low_ntf_  = low(time_frame)
    
    # Create new empty series (just to get the old index)
    empty_series = pd.DataFrame(np.zeros(len(high_ntf_)), index=high_ntf_.index)
    
    # Merge the day_change advance with the old index to get combined index.
    # Due to datetime shifting, some of the beginning dates have been lost and next few dates
    # added to the end of d_chng_
    d_chng_ = pd.concat([d_chng_, empty_series], axis=1).fillna(0)
    d_chng_ = d_chng_[d_chng_.columns[0]]
    
    # Only retain old index throwing out newly created date values at the end
    d_chng_ = d_chng_.loc[high_ntf_.index]
    
    high_ntf__ = (d_chng_ * high_ntf_).replace(to_replace=0, method='ffill')
    low_ntf__  = (d_chng_ * low_ntf_).replace(to_replace=0, method='ffill')

    high_low_orb = pd.DataFrame({'high': high_ntf__, 'low': low_ntf__})

    return add_signal(cstr('orb', time_frame), high_low_orb)
# enddef

def __orb_x(x, time_frame='15min'):
    orb__ = get_signal(cstr('orb', time_frame)) if check_signal(cstr('orb', time_frame)) \
        else __orb(time_frame)
    return orb__[x]
# enddef

def orb_high(time_frame='15min'):
    return __orb_x('high', time_frame)
def orb_low(time_frame='15min'):
    return __orb_x('low', time_frame)

#########################################################################
# All strategy algos
def crossover(x, y):
    return op_crossover(x, y)
# enddef

def crossunder(x, y):
    return op_crossunder(x, y)
# enddef
