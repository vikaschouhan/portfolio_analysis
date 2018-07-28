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

# import strategies
import strategies

# All available strategies
avail_strategies = list(strategies.strategy_map.keys())

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
    parser.add_argument('--csvdir',    help='Csv files directory', type=str, default=None)
    parser.add_argument('--repfile',   help='Report file', type=str, default=None)
    parser.add_argument('--strategy',  help='Strategy Name', type=str, default=None)
    parser.add_argument('--opt',       help='Optional strategy parameters in format (var1=val1,var2=val2 ..)',
                                                          type=str, default=None)
    parser.add_argument('--list_opts', help='Lists optional parameters.', action='store_true')
    args = parser.parse_args()

    if args.__dict__['list_opts']:
        if not args.__dict__['strategy']:
            print('--strategy is required if --list_opts is passed. Available values = {}'.format(avail_strategies))
            sys.exit(-1)
        # endif
        param_def = [ (x, strategies.strategy_map[args.__dict__['strategy']].params.__dict__[x]) \
                for x in dir(strategies.strategy_map[args.__dict__['strategy']].params) \
                if (x[0] != '_') and (x not in ['isdefault', 'notdefault']) ]

        print('Parameters for {} = {}'.format(args.__dict__['strategy'], param_def))
        sys.exit(0)
    # endif

    if (not args.__dict__['strategy']) or (args.__dict__['strategy'] not in avail_strategies):
        print('--strategy is required. Available values = {}'.format(avail_strategies))
        sys.exit(-1)
    # endif

    

    # Parse optional parameters
    if args.__dict__['opt']:
        opt_params = args.__dict__['opt'].split(',')
        opt_dict = {}
        for item_t in opt_params:
            xx = item_t.split('=')
            if len(xx) != 2:
                print('{} is not valid. Skipping.'.format(xx))
                continue
            # endif
            try:
                special_arg_dict = { 'True' : True, 'False' : False, 'None' : None }
                if xx[1] in special_arg_dict:
                    opt_dict[xx[0]] = special_arg_dict[xx[0]]
                else:
                    opt_dict[xx[0]] = int(xx[1])   # Try to assign value to integer, if possible
                # endif
            except:
                opt_dict[xx[0]] = xx[1]
            # endtry
        # endfor
    else:
        opt_dict = {}
    # endif

    if not args.__dict__['csvdir']:
        print('--csvdir is required !!')
        sys.exit(-1)
    # endif

    strategy = args.__dict__['strategy']
    csv_dir  = args.__dict__['csvdir']
    csv_dir  = cdir(csv_dir)
    csv_file = args.__dict__['repfile']

    if csv_file == None:
        csv_file = '~/backtester_{}_'.format(strategy)
        for k_t in opt_dict:
            csv_file = csv_file + '{}_{}'.format(k_t, opt_dict[k_t])
        # endfor
        csv_file = csv_file + '_{}.csv'.format(datetime.datetime.now().strftime('%s'))
    # endif

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
        cerebro.addstrategy(strategy=strategies.strategy_map[strategy], **opt_dict)
 
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
    # endfor

    print('Writing csv report to {}'.format(csv_file))
    with open(rp(csv_file), 'w') as f_out:
        f_out.write('file,returns\n')
        for k_t in ret_dict:
            f_out.write('{},{}\n'.format(k_t, ret_dict[k_t]))
        # endfor
    # endwith
# enddef
