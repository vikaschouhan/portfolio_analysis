# Author : Vikas Chouhan (presentisgood@gmail.com)

import backtrader.cerebro
import backtrader.plot as plot
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
from   utils import *

# This is for running strategies
class Cerebro(backtrader.Cerebro):
    def __init__(self, **kwargs):
        self.norm_ref   = kwargs.pop('normalization_reference', 100)
        self.en_pyfolio = kwargs.pop('enable_pyfolio', False)
        self.riskfree   = kwargs.pop('risk_free_rate', 0.06)
        self.en_debug   = kwargs.pop('enable_debug', False)

        super().__init__(**kwargs)
        self.add_report_analyzers()
    # enddef

    # Enable debug
    def enable_debug(self):
        self.en_debug = True
    # enddef
    # For debug prints
    def log(self, message):
        if self.en_debug:
            print(message)
        # endif
    # enddef

    # Add analyzers according to options passed
    def add_report_analyzers(self):
        self.log('Adding SherpeRatio analyzer with risk free rate {}'.format(self.riskfree))
        self.addanalyzer(bt.analyzers.SharpeRatio,
                         _name="mySharpe",
                         riskfreerate=self.riskfree,
                         timeframe=bt.TimeFrame.Months)
        self.log('Adding DrawDown analyzer')
        self.addanalyzer(bt.analyzers.DrawDown, _name="myDrawDown")
        self.log('Adding AnnualReturn analyzer')
        self.addanalyzer(bt.analyzers.AnnualReturn, _name="myReturn")
        self.log('Adding Trade analyzer.')
        self.addanalyzer(bt.analyzers.TradeAnalyzer, _name="myTradeAnalysis")
        self.log('Adding SQN analyzer.')
        self.addanalyzer(bt.analyzers.SQN, _name="mySqn")
        self.log('Adding Transactions analyzer.')
        self.addanalyzer(bt.analyzers.Transactions, _name="myTransactions")
        if self.en_pyfolio:
            self.log('Adding pyFolio analyzer')
            self.addanalyzer(bt.analyzers.PyFolio, _name='myPyFolio')
        # endif
    # enddef

    ####################
    # Override default cerebro.plot for returning fig objects instead of plotting them
    def plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=300, tight=True, use=None,
             **kwargs):
        if self._exactbars > 0:
            return
        # endif

        if not plotter:
            if self.p.oldsync:
                plotter = plot.Plot_OldSync(**kwargs)
            else:
                plotter = plot.Plot(**kwargs)
            # endif
        # endif

        figs = []
        for stratlist in self.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)
                figs.append(rfig)
            # endfor
            #plotter.show()
        # endfor

        return figs
    # enddef

    #######################################################
    # Write a csv report with custom stats
    def get_stats0(self):
        strat = self.get_strategy_backtest()
        end_portf_value = self.broker.get_value()
        start_portf_value = self.broker.startingcash

        ret_dict = {}
        ret_dict['rets'] = (end_portf_value - start_portf_value)*100.0/start_portf_value

        sqn = strat.analyzers.mySqn.get_analysis()
        ret_dict['sqn_score'] = to_precision(sqn['sqn'], 2)

        ta = strat.analyzers.myTradeAnalysis.get_analysis()
        ddown = strat.analyzers.myDrawDown.get_analysis()
        ret_dict['max_drawdown'] =  ddown['max']['moneydown']
        ret_dict['max_drawdown_len'] = ddown['max']['len']
        ret_dict['net_profit'] = ta['pnl']['net']['total']

        tsactions = strat.analyzers.myTransactions.get_analysis()
        last_tsac = tsactions.popitem(last=True)
        ret_dict['last_trade'] = 'buy' if (last_tsac[1][0][0] > 0) else 'sell'
        ret_dict['last_trade_time'] = last_tsac[0]
        return ret_dict
    # enddef

    ##############################################
    # Much of the below functions have been copied from
    # https://github.com/Oxylo/btreport
    # I would like to thank the author of this project for his work.
    # Add new functions for implementing extra plotting
    def get_strategy_backtest(self):
        return self.runstrats[0][0]
    # enddef
    def get_buynhold_curve(self):
        st = self.get_strategy_backtest()
        s = st.data._dataname[st.data.params.open]
        return self.norm_ref * s / s[0]
    # enddef
    def get_equity_curve(self):
        st = self.get_strategy_backtest()
        dt = st.data._dataname[st.data.params.open].index
        value = st.observers.broker.lines[1].array[:len(dt)]
        curve = pd.Series(data=value, index=dt)
        return self.norm_ref * curve / curve.iloc[0]
    # enddef
    def plot_equity_curve(self):
        curve = self.get_equity_curve()
        buynhold = self.get_buynhold_curve()
        xrnge = [curve.index[0], curve.index[-1]]
        dotted = pd.Series(data=[self.norm_ref, self.norm_ref], index=xrnge)
        fig, ax = plt.subplots(1, 1)
        ax.set_ylabel('Net Asset Value (start=100)')
        ax.set_title('Equity curve')
        _ = curve.plot(kind='line', ax=ax, color='green')
        #_ = buynhold.plot(kind='line', ax=ax, color='blue')
        _ = dotted.plot(kind='line', ax=ax, color='grey', linestyle=':')
        return fig
    # enddef
    def get_equity_curve_pts(self):
        st = self.get_strategy_backtest()
        dt = st.data._dataname[st.data.params.open].index
        profit_pts = np.nan_to_num(np.array(st.stats.trades.lines[0].array[:len(dt)]))
        loss_pts = np.nan_to_num(np.array(st.stats.trades.lines[1].array[:len(dt)]))
        final_pts = profit_pts + loss_pts
        # Create incementing pts array
        sum = np.cumsum(final_pts)
        curve = pd.Series(data=sum, index=dt)
        return curve
    # enddef
    def plot_equity_curve_pts(self, ma_len=None):
        curve = self.get_equity_curve_pts()
        xrnge = [curve.index[0], curve.index[-1]]
        dotted = pd.Series(data=[0, 0], index=xrnge)
        fig, ax = plt.subplots(1, 1)
        ax.set_ylabel('Pts')
        ax.set_title('Equity curve')
        _ = curve.plot(kind='line', ax=ax, color='green')
        _ = dotted.plot(kind='line', ax=ax, color='grey', linestyle=':')
        if ma_len:
            ma_curve = curve.ewm(span=ma_len, min_periods=ma_len).mean()
            _ = ma_curve.plot(kind='line', ax=ax, color='blue', linestyle='-')
        # endif
        return fig
    # enddef
    def _get_periodicity(self):
        curve = self.get_equity_curve()
        startdate = curve.index[0]
        enddate = curve.index[-1]
        time_interval = enddate - startdate
        time_interval_days = time_interval.days
        if time_interval_days > 5 * 365.25:
            periodicity = ('Yearly', 'Y')
        elif time_interval_days > 365.25:
            periodicity = ('Monthly', 'M')
        elif time_interval_days > 50:
            periodicity = ('Weekly', '168H')
        elif time_interval_days > 5:
            periodicity = ('Daily', '24H')
        elif time_interval_days > 0.5:
            periodicity = ('Hourly', 'H')
        elif time_interval_days > 0.05:
            periodicity = ('Per 15 Min', '15M')
        else:
            periodicity = ('Per minute', '1M')
        # endif
        return periodicity
    # enddef
    def plot_return_curve(self):
        curve = self.get_equity_curve()
        period = self._get_periodicity()
        values = curve.resample(period[1]).ohlc()['close']
        # returns = 100 * values.diff().shift(-1) / values
        returns = 100 * values.diff() / values
        returns.index = returns.index.date
        is_positive = returns > 0
        fig, ax = plt.subplots(1, 1)
        ax.set_title("{} returns".format(period[0]))
        ax.set_xlabel("date")
        ax.set_ylabel("return (%)")
        _ = returns.plot.bar(color=is_positive.map({True: 'green', False: 'red'}), ax=ax)
        return fig
    # enddef
    def create_pyfolio_tearsheet(self):
        if self.en_pyfolio:
            strat = self.get_strategy_backtest()
            returns, positions, transactions, gross_lev = strat.analyzers.pyfolio.get_pf_items()
            #sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
            #import pyfolio_override as pfo
            #report_file = '{}/{}.pdf'.format(out_dir, os.path.basename(file_t))
            #pfo.create_full_tear_sheet(
            #        returns,
            #        positions=positions,
            #        transactions=transactions,
            #        save_file=report_file)
            #        #live_start_date='2005-05-01',
        # endif
    # enddef

    #####################################
    # Save plots
    def save_plots(self, plot_file, width=16, height=9):
        main_figs    = self.plot(style='candlestick', barup='green', bardown='red', volume=False, numfigs=1)[0]
        equity_fig   = self.plot_equity_curve()
        ret_fig      = self.plot_return_curve()

        # List of all figures to be plotted
        plot_figs = [equity_fig, ret_fig] + main_figs
        save_multiple_figs_to_image_file(plot_figs, plot_file, width=width, height=height)
    # enddef
    def save_equity_curve_plot(self, plot_file, width=16, height=9, ma_len=None):
        plot_figs = [self.plot_equity_curve_pts(ma_len=ma_len)]
        save_multiple_figs_to_image_file(plot_figs, plot_file, width=width, height=height)
    # enddef
    def save_main_plot(self, plot_file, width=16, height=9, period=None):
        start     = max(0, len(self.datas[0]) - period) if period else 0
        plt.figure(figsize=(width, height))
        main_fig  = self.plot(style='candlestick', barup='green', bardown='red', volume=False, numfigs=1, start=start)[0][0]
        main_fig.savefig(plot_file)
        plt.close()
# endclass

# This is for scanners
class CerebroSC(backtrader.Cerebro):
    def __init__(self, **kwargs):
        self.en_debug   = kwargs.pop('enable_debug', False)

        super().__init__(**kwargs)
        self.add_report_analyzers()
        self.p.stdstats = False  # Disable broker and cash
    # enddef

    # Enable debug
    def enable_debug(self):
        self.en_debug = True
    # enddef
    # Enable log
    def log(self, message):
        if self.en_debug:
            print(message)
        # endif
    # enddef

    # Add analyzers according to options passed
    def add_report_analyzers(self):
        self.log('Adding Transactions analyzer.')
        self.addanalyzer(bt.analyzers.Transactions, _name="myTransactions")
    # enddef

    ####################
    # Override default cerebro.plot for returning fig objects instead of plotting them
    def plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
             width=16, height=9, dpi=300, tight=True, use=None,
             **kwargs):
        if self._exactbars > 0:
            return
        # endif

        if not plotter:
            if self.p.oldsync:
                plotter = plot.Plot_OldSync(**kwargs)
            else:
                plotter = plot.Plot(**kwargs)
            # endif
        # endif

        figs = []
        for stratlist in self.runstrats:
            for si, strat in enumerate(stratlist):
                rfig = plotter.plot(strat, figid=si * 100,
                                    numfigs=numfigs, iplot=iplot,
                                    start=start, end=end, use=use)
                figs.append(rfig)
            # endfor
            #plotter.show()
        # endfor

        return figs
    # enddef

    #######################################################
    # Write a csv report with custom stats
    def get_stats0(self):
        strat = self.get_strategy_backtest()

        ret_dict = {}
        tsactions = strat.analyzers.myTransactions.get_analysis()
        last_tsac = tsactions.popitem(last=True)
        ret_dict['last_trade'] = 'buy' if (last_tsac[1][0][0] > 0) else 'sell'
        ret_dict['last_trade_time'] = last_tsac[0]

        high_line = self.datas[0].high
        low_line  = self.datas[0].low
        close_line = self.datas[0].close
        date_line = self.datas[0].datetime
        ret_dict['high'] = max(high_line.get(size=high_line.get_idx()))
        ret_dict['low']  = min(low_line.get(size=low_line.get_idx()))
        ret_dict['close'] = close_line[0]
        ret_dict['last_time'] = self.datas[0].num2date(date_line[0])
        ret_dict['time_step'] = ret_dict['last_time'] - self.datas[0].num2date(date_line[-1])
        return ret_dict
    # enddef

    ##############################################
    # Much of the below functions have been copied from
    # https://github.com/Oxylo/btreport
    # I would like to thank the author of this project for his work.
    # Add new functions for implementing extra plotting
    def get_strategy_backtest(self):
        return self.runstrats[0][0]
    # enddef
    def save_main_plot(self, plot_file, width=16, height=9, period=None):
        start     = max(0, len(self.datas[0]) - period) if period else 0
        plt.figure(figsize=(width, height))
        main_fig  = self.plot(style='candlestick', barup='green', bardown='red', volume=True, numfigs=1, start=start)[0][0]
        main_fig.savefig(plot_file)
        plt.close(main_fig)
# endclass
