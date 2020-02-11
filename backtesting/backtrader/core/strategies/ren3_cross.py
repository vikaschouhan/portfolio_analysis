# Author : Vikas Chouhan (presentisgood@gmail.com)
# NOTE   : This file defines crossover algorithms based on variants of RenTrend.
#          The name is a play on Renko charts, since the indicator algorithm
#          uses something similar to Renko charts (but not same) for defining trends.
# RenTrend Crossovers
import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
import indicators as myind
from   common import StrategyOverride

#############################################
# based on Ren3 Indicator
class Ren3Cross(StrategyOverride):
    params = dict(
        atr_period=14,
        ma_period1=2,
        ma_period2=9,
        stake=1,
        printout=False,
        onlylong=False,
        mtrade=False,
    )

    def __init__(self):
        super(Ren3Cross, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0

        # Create SMA on 2nd data
        ren3_sig      = myind.Ren3(self.data, atr_period=self.p.atr_period, ma_period=self.p.ma_period1)
        ren3_sig_ema  = btind.MovAv.EMA(ren3_sig, period=self.p.ma_period2)

        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ren3_sig, ren3_sig_ema)

        self.init_tradeid()
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif
# endclass

###########################################################
# Based on Ren3F indicator
class Ren3FCross(StrategyOverride):
    params = dict(
        step_size=2,
        ma_period1=2,
        ma_period2=9,
        stake=1,
        printout=False,
        onlylong=False,
        mtrade=False,
    )

    def __init__(self):
        super(Ren3FCross, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0

        # Create SMA on 2nd data
        ren3_sig      = myind.Ren3F(self.data, step_size=self.p.step_size, ma_period=self.p.ma_period1)
        ren3_sig_ema  = btind.MovAv.EMA(ren3_sig, period=self.p.ma_period2)

        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ren3_sig, ren3_sig_ema)

        self.init_tradeid()
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif
# endclass

###########################################################
# Based on Ren3H indicator
class Ren3HCross(StrategyOverride):
    params = dict(
        atr_period=14,
        ma_period=9,
        stake=1,
        printout=False,
        onlylong=False,
        mtrade=False,
    )

    def __init__(self):
        super(Ren3HCross, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0

        # Create SMA on 2nd data
        ren3_sig      = myind.Ren3H(self.data, atr_period=self.p.atr_period)
        ren3_sig_ema  = btind.MovAv.EMA(ren3_sig, period=self.p.ma_period)

        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ren3_sig, ren3_sig_ema)

        # To alternate amongst different tradeids
        self.init_tradeid()
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif
# endclass

