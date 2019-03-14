#!/usr/bin/env python3
import json
import os, sys
from   common import run_scanner_main, check_config
import easygui_qt as egui
import glob
import subprocess

if __name__ == '__main__':
    curr_path     = os.path.dirname(os.path.abspath(__file__))
    config_path   = curr_path + '/configs'
    conf_files    = glob.glob1(config_path, '*.json')

    if len(conf_files) == 0:
        egui.show_message('No config files found in {} !!'.format(config_path))
        sys.exit(-1)
    # endif

    # Select config
    config_t      = egui.get_choice('Select config to run.', choices=conf_files)
    if config_t == None:
        egui.show_message('No choice selected !!')
        sys.exit(-1)
    # endif
    down_csvs     = egui.get_yes_or_no('Download csv files ??')
    open_final    = egui.get_yes_or_no('Open final report file ?')

    # Override
    config_json   = json.load(open(config_path + '/' + config_t))
    config_json['download_csvs'] = down_csvs
    
    # Checks
    check_config(config_json)

    # Invoke scanner
    report_file = run_scanner_main(config_json)
    if open_final:
        subprocess.call(['xdg-open', report_file])
    # endif
# enddef
