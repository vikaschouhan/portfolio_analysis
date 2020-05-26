from .lines import *
from .indicators import *
from .stops import *

###################################################################################
# Utils. State maintaining functions/classes
def cstr(x, y=None):
    y = '' if y is None else '__{}'.format(y)
    return x + y
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
        # endif
    # enddef
    @classmethod
    def discard_signals(cls):
        cls._add_signals = False
    # enddef
# endclass

def add_ohlcv(v):
    assert isinstance(v, Ohlcv), '>> ERROR:: Passed value is not an instance of Ohlcv !!'
    SignalCache.add_ohlcv(v)
# enddef

def add_signal(k, v):
    v.name = k
    return SignalCache.signal(k, v)
# enddef

def disable_signals():
    SignalCache.discard_signals()
# enddef

def get_signal(k):
    assert k in SignalCache.signals(), '>> ERROR:: key={} not found in SignalCache.'.format(k)
    return SignalCache.signal(k)
# enddef

####################################################################################
# All algos
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
