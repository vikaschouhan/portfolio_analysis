import backtrader as bt
import datetime
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os, sys
import glob

def rp(path):
    return os.path.expanduser(path)
# enddef

def cdir(d_path):
    d_path = rp(d_path)
    if not os.path.isdir(d_path):
        os.mkdir(d_path)
    # endif
    return d_path
# enddef

class LongShortEMA(bt.Strategy):
    params = dict(
        fast=14,
        slow=21,
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

    def __init__(self):
        # To control operation entries
        self.order = None
        self.startcash = self.broker.getvalue()

        # Create SMA on 2nd data
        ema_slow = btind.MovAv.EMA(self.data, period=self.p.slow)
        ema_fast = btind.MovAv.EMA(self.data, period=self.p.fast)
        # Create a CrossOver Signal from close an moving average
        self.signal = btind.CrossOver(ema_fast, ema_slow)

        # To alternate amongst different tradeids
        if self.p.mtrade:
            self.tradeid = itertools.cycle([0, 1, 2])
        else:
            self.tradeid = itertools.cycle([0])

    def next(self):
        if self.order:
            return  # if an order is active, no new orders are allowed

        if self.signal > 0.0:  # cross upwards
            if self.position:
                self.log('CLOSE SHORT , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)

            self.log('BUY CREATE , %.2f' % self.data.close[0])
            self.curtradeid = next(self.tradeid)
            self.buy(size=self.p.stake, tradeid=self.curtradeid)

        elif self.signal < 0.0:
            if self.position:
                self.log('CLOSE LONG , %.2f' % self.data.close[0])
                self.close(tradeid=self.curtradeid)

            if not self.p.onlylong:
                self.log('SELL CREATE , %.2f' % self.data.close[0])
                self.curtradeid = next(self.tradeid)
                self.sell(size=self.p.stake, tradeid=self.curtradeid)

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))

        elif trade.justopened:
            self.log('TRADE OPENED, SIZE %2d' % trade.size)

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        #print('Period_List: {},{} Final PnL: {}'.format(self.p.fast, self.p.slow, pnl))

class PandasDataCustom(btfeeds.PandasData):
    params = (
        ('nocase', True),

        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('datetime', None),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', 'o'),
        ('high', 'h'),
        ('low', 'l'),
        ('close', 'c'),
        ('volume', 'v'),
        ('openinterest', -1),
    )
# endclass

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csvdir',    help='Csv dir for scrips', type=str, default=None)
    parser.add_argument('--repfile',   help='Report file', type=str, default='~/a.csv')
    args = parser.parse_args()

    if not args.__dict__['csvdir']:
        print('--csvdir required.')
        sys.exit(-1)
    # endif

    csv_dir  = args.__dict__['csvdir']
    csv_dir  = cdir(csv_dir)
    csv_file = args.__dict__['repfile']

    files = glob.glob('{}/*.csv'.format(csv_dir))
    if len(files) == 0:
        print('No csv files found.')
        sys.exit(-1)
    # endif

    ret_dict = {}

    for file_t in files:
        print('Analysing {}'.format(file_t))

        pd_data  = pd.read_csv(file_t, index_col='t', parse_dates=['t'])

        # drop all rows with close=0,open=0,high=0,low=0
        pd_data  = pd_data.drop(pd_data[(pd_data.c == 0.0) & (pd_data.o == 0.0) & (pd_data.h == 0.0) & (pd_data.l == 0.0)].index)

        # prepare feed
        data = PandasDataCustom(dataname=pd_data)

        cerebro = bt.Cerebro()
        # Setting my parameters : Stop loss at 1%, take profit at 4%, go short when rsi is 90 and long when 20.
        #cerebro.addstrategy(strategy=LongShortEMA, printout=False)
        cerebro.addstrategy(strategy=LongShortEMA, printout=False)
 
        cerebro.adddata(data)
 
        # no slippage
        cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0)
 
        # 20 000$ cash initialization
        cerebro.broker.setcash(20000.0)
 
        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
 
        # Set the fees
        #cerebro.broker.setcommission(commission=0.00005)
 
        # add analyzers
        #cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="mySharpe", timeframe=bt.TimeFrame.Minutes, compression=15, riskfreerate=0.061)
        #cerebro.addanalyzer(bt.analyzers.DrawDown, _name="myDrawDown")
        #cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='myReturns')
 
        # Print out the starting conditions
        #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        start_portf_value = cerebro.broker.get_value()
 
        backtest = cerebro.run()
        #thestrat = backtest[0]

        end_portf_value = cerebro.broker.get_value()

        #print('Start_port_value = {}'.format(start_portf_value))
        #print('End_port_value = {}'.format(end_portf_value))

        #print('{},{}'.format(file_t, (end_portf_value - start_portf_value)*100.0/start_portf_value))
        ret_dict[file_t] = (end_portf_value - start_portf_value)*100.0/start_portf_value

        #print('Sharpe Ratio:', thestrat.analyzers.mySharpe.get_analysis())
        #print('Returns:', thestrat.analyzers.myReturns.get_analysis())

        #cerebro.plot(style='candlestick', barup='green', bardown='red', volume=False)

    # endif

    print('Writing csv report to {}'.format(csv_file))
    with open(rp(csv_file), 'w') as f_out:
        f_out.write('file,returns\n')
        for k_t in ret_dict:
            f_out.write('{},{}\n'.format(k_t, ret_dict[k_t]))
        # endfor
    # endwith
# enddef
