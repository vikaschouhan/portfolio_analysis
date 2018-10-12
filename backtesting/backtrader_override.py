import backtrader.cerebro
import backtrader.plot as plot
import pandas as pd
import matplotlib.pyplot as plt

class Cerebro(backtrader.Cerebro):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.norm_ref = kwargs.get('normalization_reference', 100)
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
        _ = buynhold.plot(kind='line', ax=ax, color='blue')
        _ = dotted.plot(kind='line', ax=ax, color='grey', linestyle=':')
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
# endclass
