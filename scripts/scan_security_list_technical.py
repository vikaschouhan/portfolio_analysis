#!/usr/bin/env python
# Author    : Vikas Chouhan (presentisgood@gmail.com)
# Copyright : Vikas Chouhan (presentisgood@gmail.com)
# License   : GPLv2
# NOTE      : Please respect the license and copyright.
#
# Right now it uses ema crossover but anything can be applied.
#
# The goal is to find out the right timings for entry in the stocks selected via
# a fundamental screener.
# Say for example you get a list of top 30 companies satisfying magic formula criteria
# (Joel Greenblatt), but still to maximize your returns you also want to apply some
# form of moving average crossover. This script is supposed to achieve things like
# that (Thus a sort of techno-fundamental screener).

from   modules import invs_core
from   modules import invs_plot
from   modules import invs_scanners
from   modules import invs_utils
import logging
from   colorama import Fore, Back, Style
import os
import argparse
import sys
import re
import datetime
import shutil

# Function to populate sec csv file in mentioned format to symbol list
def populate_sec_list(sfile):
    sec_list      = []
    l_ctr         = 0
    file_type     = None
    file_type_l   = ['nse_eqlist', 'nse_eqlist_m', 'bse_eqlist', 'nse_fo_mktlots', 'sym_name_list']

    # Return supported file types if no file passed
    if sfile == None:
        return file_type_l
    # endif

    with open(sfile, 'r') as file_h:
        for l_this in file_h:
            l_ctr = l_ctr + 1
            if l_ctr == 1:
                # Get file_type header (1st line)
                file_type = l_this.replace('\n', '').replace('\r', '').replace(' ', '')
                if file_type in file_type_l:
                    print Fore.MAGENTA + 'File type seems to be {} !!'.format(file_type) + Fore.RESET
                else:
                    print Fore.MAGENTA + 'Unsupported file type {}. Ensure that first line of csv file specifies file_type !!'.format(file_type) + Fore.RESET
                    sys.exit(-1)
                # endif
                continue
            # endif
            if re.match('^\s*#', l_this):
                continue
            # endif

            if file_type == 'bse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[2],
                               })
            elif file_type == 'nse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[2],
                                    'name' : s_arr[0],
                               })
            elif file_type == 'nse_eqlist_m':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[1],
                               })
            elif file_type == 'nse_fo_mktlots':
                if re.match('UNDERLYING', l_this) or re.match('Derivatives in', l_this):
                    continue
                # endif
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[1].replace(' ', ''),
                                    'name' : s_arr[0],
                               })
            elif file_type == 'sym_name_list':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0].replace(' ', ''),
                                    'name' : s_arr[1],
                               })
            elif file_type == None:
                continue
            # endif
        # endfor
    # endwith
    return sec_list
# enddef

def populate_sym_list(invs_dict_file, sec_list):
    # Convert inv_dot_com_db_list to dict:
    inv_dot_com_db_dict = invs_utils.parse_dict_file(invs_dict_file)
    # Generate nse dict
    nse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'nse_code' in item_this and item_this[u'nse_code']:
            nse_dict[item_this[u'nse_code']] = item_this
        # endif
    # endfor
    # Generate bse dict
    bse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'bse_code' in item_this and item_this[u'bse_code']:
            bse_dict[item_this[u'bse_code']] = item_this
        # endif
    # endfor

    # code list
    nse_keys = nse_dict.keys()
    bse_keys = [unicode(x) for x in bse_dict.keys()]

    # Search for tickers
    sec_dict = {}
    not_f_l  = []
    for sec_this in sec_list:
        sec_code = unicode(sec_this['code'], 'utf-8')
        sec_name = sec_this['name']
        # Search
        if sec_code in nse_keys:
            sec_dict[sec_code] = {
                                     'ticker' : nse_dict[sec_code][u'ticker'],
                                     'name'   : nse_dict[sec_code][u'description'],
                                 }
        elif sec_code in bse_keys:
            sec_dict[sec_code] = {
                                     'ticker' : bse_dict[sec_code][u'ticker'],
                                     'name'   : bse_dict[sec_code][u'description'],
                                 }
        else:
            not_f_l.append(sec_this)
        # endif
    # endfor
    print Back.RED + '{} not found in investing.com db'.format(not_f_l) + Back.RESET

    return sec_dict
# enddef



# Common Wrapper over all strategies
def run_stretegy_over_all_securities(sec_dict, lag=30, res='1W', strategy_name="em2_x", period_list=[9, 14, 21],
                                     plots_dir=None, rep_file=None, plot_monthly=False, invoke_marketsmojo=True, volume_lag=10):
    csv_report_file = '~/csv_report_security_list_{}.csv'.format(datetime.datetime.now().date().isoformat()) if rep_file == None else rep_file
    csv_rep_list    = []
    g_graphs_dir    = '/graphs/'

    # Headers
    header_l        = ['Name', 'Switch Direction', 'Time Delta', 'Peek to Trough %', 'Price', 'Volume Up']
    if invoke_marketsmojo:
        header_l    = header_l + ['Valuation', 'Quality', 'Fin Trend']
    # endif

    if plots_dir:
        # Add header
        header_l    = header_l + ['Graph']

        # Other things
        plots_dir = os.path.expanduser(plots_dir)
        csv_report_file = plots_dir + '/' + os.path.basename(csv_report_file)
        if not os.path.isdir(plots_dir):
            print "{} doesn't exist. Creating it now !!".format(plots_dir)
            os.makedirs(plots_dir)
            os.makedirs(plots_dir + g_graphs_dir)
        # endif
        print 'Plots dir = {}'.format(plots_dir)
    # endif

    # Start scan
    if strategy_name == "em2_x":
        sec_list    = []
        ctr         = 0
        ctr2        = 0
        # Add csv headers
        csv_rep_list.append(header_l)

        # Hyper parameters
        period_list = [9, 14, 21] if period_list == None else period_list
        sig_mode    = "12"

        print 'Running {} strategy using lag={}, sig_mode={} & period_list={}'.format(strategy_name, lag, sig_mode, period_list)
        print Fore.MAGENTA + 'Peak to trough percentage has meaning only when trend is down to up !!' + Fore.RESET
        print Fore.GREEN + '--------------------- GENERATING REPORT --------------------------------' + Fore.RESET

        # Iterate over all security dict
        for sec_code in sec_dict.keys():
            ctr2    = ctr2 + 1
            logging.debug("{} : Running {} strategy over {}".format(ctr2, strategy_name, sec_code))
            # NOTE: Don't know what the hell I am calculating using these.
            #       They need to be reviewed
            def _c_up(d):
                return (d['c'].max() - d.iloc[-1]['c'])/d.iloc[-1]['c']
            # enddef
            def _c_dwn(d):
                return (d.iloc[-1]['c'] - d['c'].min())/d.iloc[-1]['c']
            # enddef
            def _vol_up(d, vol_lag=10):
                try:
                    return (d.iloc[-1]['v_ma'] - d.iloc[-1 - vol_lag]['v_ma'])/d.iloc[-1 - vol_lag]['v_ma']
                except:
                    return 0
                # endif
            # enddef
            # Fetch data
            d_this = invs_core.fetch_data(sec_dict[sec_code]['ticker'], res)
            # Run strategy
            logging.debug("{} : Running ema crossover function over {}".format(ctr2, sec_code))
            status, tdelta, trend_switch, d_new = invs_scanners.run_ema2(d_this, lag=lag, period_list=period_list, sig_mode=sig_mode)
            # Add volume ma
            d_v_this = invs_scanners.add_vol_ma(d_this, period_list=period_list)
            # Analyse data
            p2t_up   = _c_up(d_new)
            p2t_down = _c_dwn(d_new)
            vol_up   = _vol_up(d_v_this, vol_lag=volume_lag)
            # Print reports
            if (status==True):
                row_this = []  # This row

                if trend_switch:
                    t_swt    = "Down2Up"
                    t_switch = Fore.GREEN + "Down to Up" + Fore.RESET
                    p2t      = int(p2t_up * 100)
                else:
                    t_swt    = "Up2Down"
                    t_switch = Fore.RED + "Up to Down" + Fore.RESET
                    p2t      = int(p2t_down * 100)
                # endif

                # Add rep list entry
                row_this = row_this + [sec_dict[sec_code]['name'], t_swt, str(tdelta), str(p2t), d_this.iloc[-1]['c'], vol_up]
                if invoke_marketsmojo:
                    info_this = invs_core.pull_info_from_marketsmojo(sec_code)
                    # If nothing returned
                    if info_this == None:
                        row_this  = row_this + ['-', '-', '-']
                    else:
                        info_this = info_this[0]  # Pick only first element
                        # Add assertion
                        # FIXME : fix this assertion
                        #assert(row_this['bsecode'] == sec_code or row_this['nsecode'] == sec_code)
                        # Add to the main row
                        row_this  = row_this + [info_this['valuation'], info_this['quality'], info_this['fintrend']]
                    # endif
                # endif
                

                # Print
                sec_name = Fore.GREEN + sec_dict[sec_code]['name'] + Fore.RESET
                sys.stdout.write('{}. {} switched trend from {}, {} days ago. Peak to trough % = {}%\n'.format(ctr, sec_name, t_switch, tdelta, p2t))
                sys.stdout.flush()
                ctr = ctr + 1

                # Save plot
                if plots_dir:
                    pic_name = plots_dir + g_graphs_dir + sec_dict[sec_code]['name'].replace(' ', '_') + '.png'
                    invs_plot.gen_candlestick(d_this, period_list=period_list, title=sec_dict[sec_code]['name'], plot_period=100, file_name=pic_name)
                    # Plot monthly chart if required
                    if plot_monthly:
                        d_mon    = invs_core.fetch_data(sec_dict[sec_code]['ticker'], '1M')
                        pic_name_mon = plots_dir + g_graphs_dir + sec_dict[sec_code]['name'].replace(' ', '_') + '_monthly.png'
                        invs_plot.gen_candlestick(d_this, title=sec_dict[sec_code]['name'], plot_period=200, file_name=pic_name_mon)
                    # endif

                    # Add to csv
                    row_this = row_this + ['=HYPERLINK("file:///{}")'.format(pic_name)]
                # endif

                # Append final row to list
                csv_rep_list.append(row_this)
            # endif
        # endfor
    else:
        print "Strategy : {}, not implemented yet !!".format(strategy_name)
    # endif

    # Write to csv file
    print Fore.GREEN + '--------------------- REPORT END --------------------------------' + Fore.RESET
    print 'Writing report file to {}'.format(csv_report_file)
    with open(os.path.expanduser(csv_report_file), 'w') as f_out:
        csv_writer = csv.writer(f_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item_this in csv_rep_list:
            csv_writer.writerow(item_this)
        # endfor
    # endwith

    return csv_report_file
# enddef

# F&o Stats generator
def run_scanner_sec_stats(sec_dict, res='1m', rep_file=None):
    ctr2 = 0
    csv_rep_list    = []
    strategy_name   = 'calc_stats'
    header_l        = ['Name', 'price_spike(nearness)', 'price_spike2(fluctuation)', 'vol_spike']
    csv_report_file = '~/csv_report_stats_{}.csv'.format(datetime.datetime.now().date().isoformat()) if rep_file == None else rep_file

    print 'Running {} strategy.'.format(strategy_name)
    print Fore.GREEN + '--------------------- GENERATING REPORT --------------------------------' + Fore.RESET

    # Add header
    csv_rep_list.append(header_l)

    # Iterate over all security dict
    for sec_code in sec_dict.keys():
        logging.debug("{} : Running {} strategy over {}".format(ctr2, strategy_name, sec_code))
        # Fetch data
        d_this   = invs_core.fetch_data(sec_dict[sec_code]['ticker'], res)
        sec_name = sec_dict[sec_code]['name']

        # Calculate stats
        # Av d
        dhlc_a   = (d_this['h'] + d_this['l'] + d_this['c'])/3
        dhlc_ra  = dhlc_a.ewm(span=9).mean()
        dhlc_rad = (dhlc_a - dhlc_ra)/dhlc_ra
        dhlc_m   = dhlc_rad.max()

        # Spike 2
        dhlc_raa  = dhlc_ra.ewm(span=9).mean()
        dhlc_raad = (dhlc_ra - dhlc_raa)/dhlc_raa
        dhlc_m2   = dhlc_raad.mean()

        # Vol spike
        dhlc_r00  = dhlc_ra/dhlc_ra.shift(5)
        dhlc_r01  = dhlc_r00[::5]
        dhlc_r02  = abs(np.log(dhlc_r01.mean()))

        # Print stats
        sec_name_c = Fore.GREEN + sec_name + Fore.RESET
        print '{}. {:<50}, price_spike={}, price_spike2={}, vol_spike={}'.format(ctr2, sec_name_c, dhlc_m, dhlc_m2, dhlc_r02)

        csv_rep_list.append([ sec_name, dhlc_m, dhlc_m2, dhlc_r02 ])
        ctr2 = ctr2 + 1
    # endfor

    # Write to csv file
    print Fore.GREEN + '--------------------- REPORT END --------------------------------' + Fore.RESET
    print 'Writing report file to {}'.format(csv_report_file)
    with open(os.path.expanduser(csv_report_file), 'w') as f_out:
        csv_writer = csv.writer(f_out, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item_this in csv_rep_list:
            csv_writer.writerow(item_this)
        # endfor
    # endwith

    return csv_report_file
# enddef

#########################################################
# Main

if __name__ == '__main__':
    # Logging init
    logging.basicConfig(filename='/tmp/scan_security_list_technical.py.log', filemode='w', level=logging.DEBUG)

    dot_invs_py = '~/.investing_dot_com_security_dict.py'
    dot_invs_py_exists = False

    # Check if above file exists
    if os.path.exists(os.path.expanduser(dot_invs_py)) and os.path.isfile(os.path.expanduser(dot_invs_py)):
        dot_invs_py_exists = True
    # endif

    strategy_l = ['scanner', 'statsgen']

    parser  = argparse.ArgumentParser()
    parser.add_argument("--invs",    help="Investing.com database file (populated by eq_scan_on_investing_dot_com.py)", type=str, default=None)
    parser.add_argument("--lag",     help="Ema/Sma Crossover lag (in days)", type=int, default=10)
    parser.add_argument("--res",     help="Resolution", type=str, default='1W')
    parser.add_argument("--ma_plist",help="Moving average period list", type=str, default=None)
    parser.add_argument("--sfile",   help="Security csv file. Can be list file or bhavcopy file.", type=str, default=None)
    parser.add_argument("--plots_dir", \
            help="Directory where plots are gonna stored. If this is not passed, plots are not generated at all.", type=str, default=None)
    parser.add_argument("--plot_mon",help="Plot monthly charts.", action='store_true')
    parser.add_argument("--strategy",help="Strategy function", type=str, default='scanner')
    args    = parser.parse_args()

    if not args.__dict__["invs"]:
        if dot_invs_py_exists:
            print 'Using {} as Investing.com database file.'.format(dot_invs_py)
            invs_db_file = dot_invs_py
        else:
            print "--invs is required !!"
            sys.exit(-1)
        # endif
    else:
        print 'Using {} as Investing.com database file.'.format(args.__dict__["invs"])
        invs_db_file = args.__dict__["invs"]

        # Copy the passed file to dot_invs_py
        print 'Copying {} to {} ..'.format(invs_db_file, dot_invs_py)
        shutil.copyfile(os.path.expanduser(invs_db_file), os.path.expanduser(dot_invs_py))
    # endif
    if not args.__dict__["sfile"]:
        print "--sfile is required !! It should be one of supported types : {}".format(populate_sec_list(None))
        sys.exit(-1)
    # endif
    if not args.__dict__["ma_plist"]:
        ma_plist = [9, 14, 21]
    else:
        ma_plist = [ int(x) for x in args.__dict__["ma_plist"].split(',') ]
    # endif

    if args.__dict__["strategy"] not in strategy_l:
        print '--strategy should be one of following : {}'.format(strategy_l)
        sys.exit(-1)
    # endif
    strategy_type = args.__dict__["strategy"]

    # Vars
    invs_db_f  = os.path.expanduser(invs_db_file)
    sec_file   = args.__dict__["sfile"]
    ma_lag     = args.__dict__["lag"]
    res        = args.__dict__["res"]
    plot_m     = args.__dict__["plot_mon"]

    # Get security list from screener.in using default screen_no=17942
    sec_list   = populate_sec_list(sfile=sec_file)

    print 'Found {} securities.'.format(len(sec_list))
    sec_tick_d = populate_sym_list(invs_db_f, sec_list)
    print 'Found {} securities in investing_com database.'.format(len(sec_tick_d))

    # Run strategy function
    if strategy_type == 'scanner':
        print 'Running scanner...'
        rep_file = '~/csv_report_security_list_{}_{}_per{}_res{}_lag{}.csv'.format(os.path.basename(sec_file).split('.')[0], 
                      datetime.datetime.now().date().isoformat(), '_'.join([str(x) for x in ma_plist]), res, ma_lag)
        rep_file = run_stretegy_over_all_securities(sec_tick_d, lag=ma_lag, res=res, strategy_name="em2_x", \
                       period_list=ma_plist, plots_dir=args.__dict__["plots_dir"], rep_file=rep_file, \
                       plot_monthly=plot_m)
    elif strategy_type == 'statsgen':
        rep_file = '~/csv_report_security_list__stats_{}_{}.csv'.format(os.path.basename(sec_file).split('.')[0], 
                      datetime.datetime.now().date().isoformat())
        print 'Running statsgen...'
        rep_file = run_scanner_sec_stats(sec_tick_d, res=res, rep_file=rep_file)
    else:
        print 'No valid strategy found !!'
        sys.exit(-1)
    # endif

    # Upload to google-drive (just a temporary solution. Will change it later)
    status = check_call(['gdrive-linux-x64', 'upload', os.path.expanduser(rep_file)])

    # DEBUG
    #d_this = fetch_data(sec_tick_d[sec_tick_d.keys()[0]]['ticker'], '1W')
# endif
