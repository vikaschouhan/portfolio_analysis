# Author : Vikas Chouhan
# Simple Long/Short Moving Average Crossover

import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
from   common import StrategyOverride

class LongShortEMA(StrategyOverride):
    params = dict(
        fast=14,
        slow=21,
        stake=1,
        printout=False,
        onlylong=False,
        mtrade=False,
    )

    def __init__(self):
        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0
        self.lastprice = None

        # Create SMA on 2nd data
        ema_slow = btind.MovAv.EMA(self.data, period=self.p.slow)
        ema_fast = btind.MovAv.EMA(self.data, period=self.p.fast)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ema_fast, ema_slow)

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
