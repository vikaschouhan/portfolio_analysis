#!/usr/bin/env python3
import argparse
import json
import os, sys
import shutil
import subprocess
import shlex
import distutils.util

def rp(path):
    return os.path.expanduser(path)
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

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--config_file',    help='json config file', type=str, default=None)
    parser.add_argument('--override',       help='override json params', type=str, default=None)
    args = parser.parse_args()

    if not args.__dict__['config_file']:
        print('--config_file is required !!')
        sys.exit(-1)
    # endif

    config_file = args.__dict__['config_file']
    config_json = json.load(open(config_file, 'r'))
    override    = args.__dict__['override']

    args_dict   = {}
    if override:
        try:
            args_dict = dict([x.split('=') for x in override.split(';')])
        except:
            print('args {} not in proper format'.format(override))
            sys.exit(-1)
        # endtry
    # endif

    # Checks
    check_config(config_json)

    # Ovveride
    config_json = {**config_json, **args_dict}
    print(config_json)

    output_dir  = rp(get_key(config_json, 'out_dir', cast_to=str))
    resolution  = get_key(config_json, 'resolution', cast_to=str)
    invs_file   = get_key(config_json, 'invs_file', cast_to=str)
    sec_file    = get_key(config_json, 'db_file', cast_to=str)
    down_csvs   = get_key(config_json, 'download_csvs', False, cast_to=bool)
    n_threads   = get_key(config_json, 'num_threads', 2, cast_to=int)
    strategy    = get_key(config_json, 'strategy', cast_to=str)
    strat_opts  = get_key(config_json, 'strategy_opts', cast_to=str)
    csv_backup  = get_key(config_json, 'csv_backup', True, cast_to=bool)

    csv_dir     = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + '_{}_csv'.format(resolution)
    if strat_opts:
        results_dir = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + \
                '_{}_{}'.format(resolution, strategy) + '_{}'.format(strat_opts.replace(',', '_'))
    else:
        results_dir = output_dir + '/' + os.path.splitext(os.path.basename(sec_file))[0] + \
                '_{}_{}'.format(resolution, strategy)
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

    if down_csvs:
        print('Generating CSV files....')
        py_cmd = 'python3 scripts/gen_csvs_technical.py --invs {invs_file} \
                --res {resolution} --sfile {sec_file} --odir {out_dir}'.format(invs_file=invs_file,
                    resolution=resolution, sec_file=sec_file, out_dir=csv_dir)
        subprocess.call(shlex.split(py_cmd))
    # endif

    # Take backup if suggested
    if csv_backup:
        print('Taking csv files backup.')
        py_cmd = 'tar -cvjf {backup_file}.tar.bz2 {csv_dir}'.format(backup_file=csv_dir, csv_dir=csv_dir)
        subprocess.call(shlex.split(py_cmd))
    # endif

    print('Running backtester...')
    strat_arg = '' if strat_opts == None else '--opt {}'.format(strat_opts)
    py_cmd = 'python3 backtesting/backtrader_screener.py --csvdir {csv_dir} --strategy {strategy} \
        --outdir {plots_dir} --nthreads {num_threads} --period 200  --repfile {report_file} {strat_arg}'.format(
            csv_dir=csv_dir, strategy=strategy, plots_dir=plots_dir, num_threads=n_threads,
            report_file=report_file, strat_arg=strat_arg)
    subprocess.call(shlex.split(py_cmd))
# enddef
