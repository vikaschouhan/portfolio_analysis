# Author : Vikas Chouhan (presentisgood@gmail.com)
# SuperTrend RSI strategies

import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys
import indicators as myind

#############################################
class SupertrendRSILong(bt.Strategy):
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

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        # endif
    # enddef

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
        if self.p.mtrade:
            self.tradeid = itertools.cycle([0, 1, 2])
        else:
            self.tradeid = itertools.cycle([0])
        # endif
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

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications
        # endif

        if order.status == order.Completed:
            if order.isbuy():
                self.accpoints += (self.lastprice - order.executed.price) if self.lastprice else 0
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
                self.lastorder = order.executed.price
            else:
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

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))
        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)
        # endif
    # enddef

    def stop(self):
        #pnl = round(self.broker.getvalue() - self.startcash,2)
        self.log('Final PnL Points: {}'.format(int(self.accpoints)))
    # enddef
# endclass

class SupertrendRSIShort(bt.Strategy):
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

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        # endif
    # enddef

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
        if self.p.mtrade:
            self.tradeid = itertools.cycle([0, 1, 2])
        else:
            self.tradeid = itertools.cycle([0])
        # endif
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

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications
        # endif

        if order.status == order.Completed:
            if order.isbuy():
                self.accpoints += (self.lastprice - order.executed.price) if self.lastprice else 0
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
                self.lastorder = order.executed.price
            else:
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

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))
        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)
        # endif
    # enddef

    def stop(self):
        #pnl = round(self.broker.getvalue() - self.startcash,2)
        self.log('Final PnL Points: {}'.format(int(self.accpoints)))
    # enddef
# endclass
