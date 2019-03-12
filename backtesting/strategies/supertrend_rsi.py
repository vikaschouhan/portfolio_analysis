# Author : Vikas Chouhan (presentisgood@gmail.com)
# SuperTrend RSI strategies

import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
import indicators as myind
from   common import StrategyOverride

#############################################
class SupertrendRSILong(StrategyOverride):
    params = dict(
        atr_period=14,
        atr_multiplier=2,
        rsi_period=14,
        rsi_high=70,
        rsi_low=30,
        stake=1,
        printout=False,
        mtrade=False,
    )

    def __init__(self):
        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0
        self.lastprice = None

        # Create SMA on 2nd data
        self.supertrend_sig = myind.Supertrend(self.data, atr_period=self.p.atr_period, atr_multiplier=self.p.atr_multiplier)
        self.rsi_sig        = bt.indicators.RSI(self.data, period=self.p.rsi_period, upperband=self.p.rsi_high, lowerband=self.p.rsi_low)

        # To alternate amongst different tradeids
        self.init_tradeid()
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        self.buy_sig   = (self.data.close[0] > self.supertrend_sig[0] and self.rsi_sig[0] > self.p.rsi_high)
        self.sell_sig  = (self.data.close[0] < self.supertrend_sig[0])

        if self.buy_sig > 0.0:  # cross upwards
            if not self.position:
                self.log('BUY CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.buy(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        elif self.sell_sig > 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif
        # endif
# endclass

class SupertrendRSIShort(StrategyOverride):
    params = dict(
        atr_period=14,
        atr_multiplier=2,
        rsi_period=14,
        rsi_high=70,
        rsi_low=30,
        stake=1,
        printout=False,
        mtrade=False,
    )

    def __init__(self):
        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0
        self.lastprice = None

        # Create SMA on 2nd data
        self.supertrend_sig = myind.Supertrend(self.data, atr_period=self.p.atr_period, atr_multiplier=self.p.atr_multiplier)
        self.rsi_sig        = bt.indicators.RSI(self.data, period=self.p.rsi_period, upperband=self.p.rsi_high, lowerband=self.p.rsi_low)

        # To alternate amongst different tradeids
        self.init_tradeid()
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        self.sell_sig   = (self.data.close[0] < self.supertrend_sig[0] and self.rsi_sig[0] < self.p.rsi_low)
        self.buy_sig    = (self.data.close[0] > self.supertrend_sig[0])

        if self.buy_sig > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif
        elif self.sell_sig > 0.0:
            if not self.position:
                self.log('SELL SHORT , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif
    # enddef
# endclass
