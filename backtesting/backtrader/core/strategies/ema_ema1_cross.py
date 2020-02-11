# Author : Vikas Chouhan (presentisgood@gmail.com)
# EMA-EMA(EMA) crossover

import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
from   common import StrategyOverride

class EMA_EMA1(StrategyOverride):
    params = dict(
        ema1=50,
        ema2=25,
        stake=1,
        printout=False,
        onlylong=False,
        mtrade=False,
    )

    def __init__(self):
        super(EMA_EMA1, self).__init__()

        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()
        self.accpoints = 0

        # Create SMA on 2nd data
        ema_1   = btind.MovAv.EMA(self.data, period=self.p.ema1)
        ema_2   = btind.MovAv.EMA(ema_1, period=self.p.ema2)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ema_1, ema_2)

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
