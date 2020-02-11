import backtrader as bt
import itertools

class StrategyOverride(bt.Strategy):
    def __init__(self, **kwargs):
        self.lastprice = None
    # endif

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        # endif
    # enddef

    def init_tradeid(self):
        # To alternate amongst different tradeids
        if self.p.mtrade:
            self.tradeid = itertools.cycle([0, 1, 2])
        else:
            self.tradeid = itertools.cycle([0])
        # endif
    # enddef

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
