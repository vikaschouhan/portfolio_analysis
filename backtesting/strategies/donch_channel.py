# Author : Vikas Chouhan
# Simple Donchian Channel Breakout
import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
from   common import StrategyOverride

class Donch(StrategyOverride):
    params = dict(
        period=20,
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
        self.long = None

        # Create SMA on 2nd data
        self.data_hhv  = btind.Highest(self.data.high, period=self.p.period, subplot=False)
        self.data_llv  = btind.Lowest(self.data.low, period=self.p.period, subplot=False)

        self.init_tradeid()
        # endif
    # enddef

    def set_mode(self, mode='buy'):
        if (self.long == True and mode == 'buy') or (self.long == False and mode == 'sell'):
            pass
        else:
            self.long = True if mode == 'buy' else False
        # endif
    # enddef
          
    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed
        # endif

        if self.data.close[0] > self.data_hhv[-1]:
            if self.long == False:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)

                self.log('BUY CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.buy(size=self.p.stake, tradeid=self.curtradeid)
            elif self.long == None:
                self.log('BUY CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.buy(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif

        elif self.data.close[0] < self.data_llv[-1]:
            if self.long == True:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)

                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            elif self.long == None:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)
            # endif
        # endif
    # enddef

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications
        # endif

        if order.status == order.Completed:
            if order.isbuy():
                self.set_mode('buy')
                self.accpoints += (self.lastprice - order.executed.price) if self.lastprice else 0
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
                self.lastorder = order.executed.price
            else:
                self.set_mode('sell')
                self.accpoints += (order.executed.price - self.lastprice) if self.lastprice else 0
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)
                self.lastprice = order.executed.price
            # endif

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log
        # endif

        # Allow new orders
        self.order = None
    # enddef
# endclass
