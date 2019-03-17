# Author  : Vikas Chouhan (presentisgood@gmail.com)
# Purpose : Common functions for final scanners

import os
import distutils.util
import shutil
import subprocess
import shlex
import uuid
import pandas as pd
import copy
import openpyxl

def rp(path):
    return os.path.expanduser(path)
# enddef

def u4():
    return str(uuid.uuid4())
# enddef

def rmtree(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    # endif
# enddef

def get_key(conf_dict, key, def_val=None, cast_to=None):
    if key in conf_dict:
        value = conf_dict[key]
    elif def_val:
        value = def_val
    else:
        value = None
    # endif

    if value == None or cast_to == None:
        return value
    # endif

    if cast_to is bool:
        return distutils.util.strtobool(value) if isinstance(value, str) else value
    else:
        return cast_to(value)
    # endif
# enddef

def check_config(conf_dict):
    conf_keys = ['out_dir', 'resolution', 'invs_file', 'db_file',
            'num_threads', 'strategy' ]
    if set(conf_keys) > set(conf_dict.keys()):
        print('one are more keys from {} are missing in config file.'.format(conf_keys))
        sys.exit(-1)
    # endif
# enddef

def run_scanner(config_json):
    output_dir  = rp(get_key(config_json, 'out_dir', cast_to=str))
    resolution  = get_key(config_json, 'resolution', cast_to=str)
    invs_file   = rp(get_key(config_json, 'invs_file', cast_to=str))
    sec_file    = rp(get_key(config_json, 'db_file', cast_to=str))
    down_csvs   = get_key(config_json, 'download_csvs', False, cast_to=bool)
    n_threads   = get_key(config_json, 'num_threads', 2, cast_to=int)
    strategy    = get_key(config_json, 'strategy', cast_to=str)
    strat_opts  = get_key(config_json, 'strategy_opts', cast_to=str)
    csv_backup  = get_key(config_json, 'csv_backup', True, cast_to=bool)
    look_back   = get_key(config_json, 'look_back', 4, cast_to=int)
    plot_period = get_key(config_json, 'plot_period', 500, cast_to=int)

    csv_dir     = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + '_{}_csv'.format(resolution)
    if strat_opts:
        results_dir = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + \
                '__{}__{}'.format(resolution, strategy) + '__{}'.format(strat_opts.replace('=', '_'))
    else:
        results_dir = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + \
                '__{}__{}'.format(resolution, strategy)
    # endif
    plots_dir   = results_dir + '/plots'
    report_file = results_dir + '/report.csv'

    if down_csvs:
        rmtree(csv_dir)
    # endif

    rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    print('resolution        = {}'.format(resolution))
    print('invs_file         = {}'.format(invs_file))
    print('sec_file          = {}'.format(sec_file))
    print('download_csvs     = {}'.format(down_csvs))
    print('csv_dir           = {}'.format(csv_dir))
    print('results_dir       = {}'.format(results_dir))
    print('plots_dir         = {}'.format(plots_dir))
    print('report_file       = {}'.format(report_file))
    print('strategy          = {}'.format(strategy))
    print('strat_opts        = {}'.format(strat_opts))
    print('look_back         = {}'.format(look_back))

    if down_csvs:
        print('Generating CSV files....')
        py_cmd = 'python3 scripts/gen_csvs_technical.py --invs {invs_file} \
                --res {resolution} --sfile {sec_file} --odir {out_dir}'.format(invs_file=invs_file,
                    resolution=resolution, sec_file=sec_file, out_dir=csv_dir)
        print('Running CMD: {}'.format(py_cmd))
        subprocess.call(shlex.split(py_cmd))
    # endif

    # Take backup if suggested
    if csv_backup:
        print('Taking csv files backup.')
        py_cmd = 'tar -cvjf {backup_file}.tar.bz2 {csv_dir}'.format(backup_file=csv_dir, csv_dir=csv_dir)
        print('Running CMD: {}'.format(py_cmd))
        subprocess.call(shlex.split(py_cmd))
    # endif

    # Run backtester only when strategy is specified.
    if strategy:
        print('Running backtester...')
        strat_arg = '' if strat_opts == None else '--opt {}'.format(strat_opts)
        py_cmd = 'python3 backtesting/backtrader_screener.py --csvdir {csv_dir} --strategy {strategy} \
            --outdir {plots_dir} --nthreads {num_threads} --period {plot_period}  --repfile {report_file} {strat_arg} \
            --lag {look_back}'.format(
                csv_dir=csv_dir, strategy=strategy, plots_dir=plots_dir, num_threads=n_threads,
                plot_period=plot_period, report_file=report_file, strat_arg=strat_arg, look_back=look_back)
        print('Running CMD: {}'.format(py_cmd))
        subprocess.call(shlex.split(py_cmd))
    # endif

    # Prepare final_sheet
    final_rep_file = os.path.splitext(report_file)[0] + '_final.xlsx'
    prepare_final_sheet(report_file, final_rep_file)

    return final_rep_file
# enddef

def run_scanner_fno_keys(config_json):
    fno_search_key_list = ['fno_gainers', 'fno_losers']

    check_config(config_json)
    output_dir = rp(get_key(config_json, 'out_dir', cast_to=str))
    fno_keys   = get_key(config_json, 'fno_keys', def_val=[], cast_to=list)
    rfile_d    = {}

    for search_key in fno_keys:
        if search_key not in fno_search_key_list:
            raise ValueError('fno_search_keys should be one of {}'.format(fno_search_key_list))
        # endif
    # endif

    for search_key in fno_keys:
        # Create report file
        rep_file = '{}/fno___{}.csv'.format(output_dir, search_key)

        # Get file
        py_cmd = 'python3 scripts/scan_nse_live_analysis.py --ofile {out_file} --key {search_key}'.format(
                out_file=rep_file, search_key=search_key)
        print('Running CMD: {}'.format(py_cmd))
        subprocess.call(shlex.split(py_cmd))

        # Override some params first
        print('Overriding db_file to {}'.format(rep_file))
        config_json["db_file"] = rep_file
        print('Setting to download csvs.')
        config_json["download_csvs"] = True

        # Run algo
        gen_report_file = run_scanner(config_json)
        rfile_d[search_key] = gen_report_file
    # endfor

    # Print reports
    print('Report files are generated as follows')
    for indx, key in enumerate(rfile_d):
        print('{}. {} -> {}'.format(indx, key, rfile_d[key]))
    # endfor
# enddef

# Wrapper
def run_scanner_main(config_json):
    if 'fno_keys' in config_json:
        print('fno_keys found in config. Running "run_scanner_fno_keys()".')
        return run_scanner_fno_keys(config_json)
    else:
        print('Running "run_scanner()"')
        return run_scanner(config_json)
    # endif
# enddef

# Trim final report. Remove ignore columns
def prepare_final_sheet(report_file, final_report_file=None, sort_by='peak_to_tough'):
    dframe = pd.read_csv(report_file)
    dframe_org = copy.copy(dframe)
    dframe = dframe[dframe['take_trade'] == 'take']
    
    # sort
    if sort_by and sort_by in dframe.columns:
        dframe.sort_values(by=[sort_by], ascending=False, inplace=True)
    # endif

    fmt_dict = { 
        'buy': 'background-color: green', 
        'sell': 'background-color: red', 
    } 
    def fmt(data, fmt_dict): 
        return data.replace(fmt_dict)
    # enddef
                                                                                                                                                                
    styled = dframe.style.apply(fmt, fmt_dict=fmt_dict, subset=['trade'])                                                                                           
    # Write to excel
    final_rep_file = os.path.splitext(report_file)[0] + '_trimmed.xlsx' \
            if final_report_file == None else final_report_file
    print('Writing final report to {}'.format(final_rep_file))

    with pd.ExcelWriter(final_rep_file, engine='openpyxl') as xls_writer:
        styled.to_excel(xls_writer, sheet_name='trimmed', startrow=0, startcol=0)
        dframe_org.to_excel(xls_writer,sheet_name='full',startrow=0 , startcol=0)
    # endwith
# endif

