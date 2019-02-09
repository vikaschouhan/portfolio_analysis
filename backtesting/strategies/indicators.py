from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt

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
