# Author : Vikas Chouhan
# Simple Donchian Channel Breakout
import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
from   common import StrategyOverride

class SimpleBreakout(StrategyOverride):
    params = dict(
        stake=1,
        printout=False,
        mtrade=False,
    )

    def __init__(self):
        super(SimpleBreakout, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0

        self.init_tradeid()
        # endif
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.data.close > self.data.high[-1]:
            if self.position: # Close short
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)
        elif self.data.close < self.data.low[-1]:
            if self.position:  # Close long
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('SELL CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.sell(size=self.p.stake, tradeid=self.curtradeid)
        # endif
    # enddef
# endclass
