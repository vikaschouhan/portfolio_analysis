tgt_dir=~/sc_db_github_files/daily_plots_bse_groupA
rm -rf $tgt_dir
python3 scripts/scan_security_list_technical.py --sfile scripts/db/bse_group_A.csv --strategy graphgen --res 1D --plots_dir $tgt_dir --plot_period 200 --fig_ratio 2
