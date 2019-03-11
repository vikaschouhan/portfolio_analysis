# Author : Vikas Chouhan (presentisgood@gmail.com)
# This file defines custom indicators


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt

# RenTrend Indicator.
class Ren3(bt.Indicator):
    lines      = ('ren_ind',)
    params     = (('atr_period', 14), ('ma_period', 2), )
    plotinfo   = dict(subplot=False)
    _nextforce = True

    def __init__(self):
        self.atr_t = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.src   = bt.indicators.EMA(self.data, period=self.p.ma_period)
        super(Ren3, self).__init__()
    # enddef

    def next(self):
        if self.src[0] > self.l.ren_ind[-1] + self.atr_t[0]:
            self.l.ren_ind[0] = self.l.ren_ind[-1] + self.atr_t[0]
        elif self.src[0] < self.l.ren_ind[-1] - self.atr_t[0]:
            self.l.ren_ind[0] = self.l.ren_ind[-1] - self.atr_t[0]
        else:
            self.l.ren_ind[0] = self.l.ren_ind[-1]
        # endif
    # enddef

    def prenext(self):
        # seed recursive value
        self.l.ren_ind[0] = self.src[0]
    # enddef
# endclass

# 2nd variant of RenTrend Indicator
class Ren3F(bt.Indicator):
    lines      = ('ren_ind',)
    params     = (('step_size', 5), ('ma_period', 2),)
    plotinfo   = dict(subplot=False)
    _nextforce = True

    def __init__(self):
        self.step_size  = self.p.step_size
        self.src        = bt.indicators.EMA(self.data, period=self.p.ma_period)
        super(Ren3F, self).__init__()
    # enddef

    def next(self):
        if self.src[0] > self.l.ren_ind[-1] + self.step_size:
            self.l.ren_ind[0] = self.l.ren_ind[-1] + self.step_size
        elif self.src[0] < self.l.ren_ind[-1] - self.step_size:
            self.l.ren_ind[0] = self.l.ren_ind[-1] - self.step_size
        else:
            self.l.ren_ind[0] = self.l.ren_ind[-1]
        # endif
    # enddef

    def prenext(self):
        # seed recursive value
        self.l.ren_ind[0] = self.data.close[0]
    # enddef
# endclass

# 3rd variant (heikinashi version) of RenTrend Indicator.
class Ren3H(bt.Indicator):
    lines      = ('ren_ind',)
    params     = (('atr_period', 14),)
    plotinfo   = dict(subplot=False)
    _nextforce = True

    def __init__(self):
        self.atr_t  = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.heikin = bt.indicators.HeikinAshi()
        super(Ren3H, self).__init__()
    # enddef

    def next(self):
        if self.heikin.ha_open[0] > self.l.ren_ind[-1] + self.atr_t[0]:
            self.l.ren_ind[0] = self.l.ren_ind[-1] + self.atr_t[0]
        elif self.heikin.ha_open[0] < self.l.ren_ind[-1] - self.atr_t[0]:
            self.l.ren_ind[0] = self.l.ren_ind[-1] - self.atr_t[0]
        else:
            self.l.ren_ind[0] = self.l.ren_ind[-1]
        # endif
    # enddef

    def prenext(self):
        # seed recursive value
        self.l.ren_ind[0] = self.heikin.ha_open[0]
    # enddef
# endclass


# SuperTrend Indicator
class Supertrend(bt.Indicator):
    lines      = ('supertrend', 'final_up', 'final_down', 'close',)
    params     = (('atr_period', 14), ('atr_multiplier', 4),)
    plotinfo   = dict(subplot=False)
    plotlines  = dict(
                     supertrend=dict(_fill_lt=('close', 'g'),
                                     _fill_gt=('close', 'r'),
                                     _plotskip=False),
                     final_up=dict(_plotskip=True),
                     final_down=dict(_plotskip=True),
                     close=dict(_plotskip=True)
                 )
    _nextforce = True

    def __init__(self):
        self.atr_t  = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.avg_t  = (self.data.high + self.data.low)/2
        self.bas_u  = self.avg_t - self.p.atr_multiplier * self.atr_t
        self.bas_l  = self.avg_t + self.p.atr_multiplier * self.atr_t
        self.l.close = self.data.close
        super(Supertrend, self).__init__()
    # enddef

    def next(self):
        if (self.data.close[-1] > self.l.final_up[-1]):
            self.l.final_up[0] = max(self.bas_u[0], self.l.final_up[-1])
        else:
            self.l.final_up[0] = self.bas_u[0]
        # endif
        if (self.data.close[-1] < self.l.final_down[-1]):
            self.l.final_down[0] = min(self.bas_l[0], self.l.final_down[-1])
        else:
            self.l.final_down[0] = self.bas_l[0]
        # endif
     
        if self.data.close[0] > self.final_down[-1]:
            self.l.supertrend[0] = self.l.final_up[0]
        elif self.data.close[0] < self.final_up[-1]:
            self.l.supertrend[0] = self.l.final_down[0]
        else:
            self.l.supertrend[0] = self.l.supertrend[-1]
        # endif
        
    # enddef

    def prenext(self):
        # seed recursive value
        self.l.final_up[0]   = 0
        self.l.final_down[0] = 0
    # enddef
# endclass
