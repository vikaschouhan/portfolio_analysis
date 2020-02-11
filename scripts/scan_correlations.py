import numpy as np
import os, sys
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
from   modules.utils import *
from   modules.plot import *

def calculate_corr_matrices(df_map, corr_range=(0.75, 1.0)):
    # Filter all prices by close only
    df_map = filter_asset_csvs(df_map, filter_col=col_close)
    # Drop all NAN rows
    df_map = df_map.dropna(axis=0, how='any')
    # Calculate log returns
    df_map_log = np.log(df_map).diff()
    
    # Drop all nans
    df_map_log = dropna(df_map_log)
    
    # Calculate correlation matrix
    corr_mat   = df_map_log.corr(method='pearson')
    
    # Filter rows and columns for which correlation > 0.75
    corr_mat_f = dropna(corr_mat[corr_mat.gt(corr_range[0]) & corr_mat.lt(corr_range[1])])

    return corr_mat_f
# enddef

def write_corr_results(corr_mat, out_dir):
    mkdir(out_dir)
    corr_mat_file   = '{}/corr_mat.xlsx'.format(out_dir)
    corr_mat_imfile = '{}/corr_mat.png'.format(out_dir)

    # Write xlsx
    df_to_excel({'corr_sheet': corr_mat}, corr_mat_file)
    # Plot heatmap
    plot_conf_mat(corr_mat, corr_mat_imfile, vmin=-1.0, vmax=1.0)
# enddef

def analyse_all(csv_dir, out_dir, ts_list=['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M']):
    mkdir(out_dir)

    # Read all unsampled data first
    print('>> Reading unsampled data for all csvs from {}'.format(csv_dir))
    df_map = read_all_asset_csvs(csv_dir, column_map=col_map, resample_period=None)

    for ts_t in ts_list:
        print('>> Resampling data for sampling period = {}'.format(ts_t))
        dmap_t   = resample_asset_data(df_map, resample_period=ts_t)

        # Calculate corr matrix
        corr_mat = calculate_corr_matrices(dmap_t, corr_range=(0.75, 1.0))

        # If dataframe is empty, continue 
        if corr_mat.empty:
            continue
        # endif

        # Dump stats
        out_dir_t = '{}/{}'.format(out_dir, ts_t)
        print('>> Writing results for {} in {}'.format(ts_t, out_dir_t))
        write_corr_results(corr_mat, out_dir_t)
    # endfor
# enddef

if __name__ == '__main__':
    parser  = argparse.ArgumentParser()
    parser.add_argument('--csv_dir',  help='Csv dir', type=str, default=None)
    parser.add_argument('--out_dir',  help='Output dir', type=str, default=None)
    args = parser.parse_args()

    csv_dir = rp(args.__dict__['csv_dir'])
    out_dir = rp(args.__dict__['out_dir'])

    if csv_fir is None or out_dir is None:
        print('All arguments required !!')
        sys.exit(-1)
    # endif

    analyse_all(csv_dir, out_dir) 
# enddef
