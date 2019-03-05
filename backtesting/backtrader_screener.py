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
import backtrader_override as bto
import multiprocessing
from   utils import *

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

def run_cerebro_over_csvs(csv_list, strategy, slippage, out_dir, period=None, opt_dict={}, proc_id=None):
    file_ctr  = 1
    num_files = len(csv_list)
    proc_id   = 'Unk' if proc_id == None else proc_id

    for file_t in csv_list:
        print('{:<4}:[{:<4}:{:<4}] Analysing {}'.format(proc_id, file_ctr, num_files, os.path.basename(file_t)))
        pd_data = pd.read_csv(file_t, index_col='t', parse_dates=['t'])

        # drop all rows with close=0,open=0,high=0,low=0
        pd_data = pd_data.drop(pd_data[(pd_data.c == 0.0) & (pd_data.o == 0.0) & (pd_data.h == 0.0) & (pd_data.l == 0.0)].index)
        period  = len(pd_data) if period == None else period

        # prepare feed
        data = PandasDataCustom(dataname=pd_data)

        cerebro = bto.CerebroSC()
        # Setting my parameters : Stop loss at 1%, take profit at 4%, go short when rsi is 90 and long when 20.
        cerebro.addstrategy(strategy=strategy_map[strategy], **opt_dict)
        cerebro.adddata(data)
 
        # no slippage
        cerebro.broker.set_slippage_fixed(slippage, slip_open=True, slip_match=True, slip_out=False)
        # 20 000$ cash initialization
        cerebro.broker.setcash(20000.0)
        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=1)
        # Set the fees
        cerebro.broker.setcommission(commission=0.00005)

        # Run backtest?!?jedi=0, ?!?        (*_***kwargs*_*) ?!?jedi?!?
        backtest = cerebro.run()

        # Get some stats
        ret_dict[file_t] = cerebro.get_stats0()

        # Save plots
        cerebro.save_main_plot('{}/{}.png'.format(out_dir, os.path.basename(file_t)), width=16, height=9, period=200)

        file_ctr = file_ctr + 1
    # endfor
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csvdir',    help='Csv files directory', type=str, default=None)
    parser.add_argument('--repfile',   help='Report file', type=str, default=None)
    parser.add_argument('--strategy',  help='Strategy Name', type=str, default=None)
    parser.add_argument('--opt',       help='Optional strategy parameters in format (var1=val1,var2=val2 ..)',
                                                          type=str, default=None)
    parser.add_argument('--list_opts', help='Lists optional parameters.', action='store_true')
    parser.add_argument('--slippage',  help='Slippage (fixed)', type=float, default=1.0)
    parser.add_argument('--outdir',    help='Output Directory.', type=str, default=None)
    parser.add_argument('--period',    help='Time period for plots.', type=int, default=None)
    parser.add_argument('--nthreads',  help='Number of threads to process.', type=int, default=4)
    args = parser.parse_args()

    # Append paths
    strategy_map = populate_strategy_map([])
    avail_strategies = list(strategy_map.keys())

    if args.__dict__['list_opts']:
        if not args.__dict__['strategy']:
            print('--strategy is required if --list_opts is passed. Available values = {}'.format(avail_strategies))
            sys.exit(-1)
        # endif
        param_def = [ (x, strategy_map[args.__dict__['strategy']].params.__dict__[x]) \
                for x in dir(strategy_map[args.__dict__['strategy']].params) \
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
    out_dir  = args.__dict__['outdir']
    slippage = args.__dict__['slippage']
    nthreads = args.__dict__['nthreads']
    period   = args.__dict__['period']

    if out_dir == None:
        print('--outdir should be valid.')
        sys.exit(-1)
    # endif
    mkdir(out_dir)

    files = glob.glob('{}/*.csv'.format(csv_dir))
    if len(files) == 0:
        print('No csv files found.')
        sys.exit(-1)
    # endif

    ##
    ret_dict = {}
    csv_chunks = split_chunks(files, nthreads)

    # Spawn processes
    proc_list = []
    for indx in range(nthreads):
        proc_t = multiprocessing.Process(target=run_cerebro_over_csvs, args=(csv_chunks[indx], strategy,
            slippage, out_dir, period, opt_dict, indx,))
        proc_list.append(proc_t)
        proc_t.start()
    # endfor

    # Wait for all processes to end
    for indx in range(nthreads):
        proc_list[indx].join()
    # endfor

    #if csv_file:
    #    print('Writing csv report to {}'.format(csv_file))
    #    with open(rp(csv_file), 'w') as f_out:
    #        f_out.write('file,returns,sqn_score, profit_per_drawdown,drawdown_len\n')
    #        for k_t in ret_dict:
    #            sqn_score = ret_dict[k_t]['sqn_score']
    #            profit_per_ddown = ret_dict[k_t]['net_profit']/ret_dict[k_t]['max_drawdown']
    #            max_ddown_len = ret_dict[k_t]['max_drawdown_len']
    #            f_out.write('{},{},{},{},{}\n'.format(k_t, ret_dict[k_t]['rets'], sqn_score, profit_per_ddown, max_ddown_len))
    #        # endfor
    #    # endwith
    ## endif
# enddef
