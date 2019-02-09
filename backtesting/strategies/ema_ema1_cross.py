import backtrader as bt
import datetime
import backtrader.indicators as btind
import itertools
import os, sys

class EMA_EMA1(bt.Strategy):
    params = dict(
        ema1=50,
        ema2=25,
        stake=1,
        printout=False,
        onlylong=False,
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
        ema_1   = btind.MovAv.EMA(self.data, period=self.p.ema1)
        ema_2   = btind.MovAv.EMA(ema_1, period=self.p.ema2)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ema_1, ema_2)

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
        self.log('Period_List: {},{} Final PnL Points: {}'.format(self.p.ema1, self.p.ema2, int(self.accpoints)))
    # enddef
# endclass
