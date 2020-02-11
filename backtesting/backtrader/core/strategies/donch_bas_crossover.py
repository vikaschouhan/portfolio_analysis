# Author : Vikas Chouhan
# Simple Donchian Channel Breakout
import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
from   common import StrategyOverride
from   indicators import DonchianChannel

class DonchBasCrossOver(StrategyOverride):
    params = dict(
        period=40,
        stake=1,
        printout=False,
        mtrade=False,
    )

    def __init__(self):
        super(DonchBasCrossOver, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0
        self.lastprice = None

        self.donch     = DonchianChannel(self.data, period=self.p.period)
        self.signal    = btind.CrossOver(self.data.close, self.donch.l.bas)

        self.init_tradeid()
        # endif
    # enddef

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.signal > 0.0:
            if self.position: # Close short
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)
            # endif

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)
        elif self.signal < 0.0:
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
