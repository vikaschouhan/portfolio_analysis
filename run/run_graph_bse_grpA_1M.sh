tgt_dir=~/sc_db_github_files/monthly_plots_bse_groupA
rm -rf $tgt_dir
python3 scripts/scan_security_list_technical.py --sfile scripts/db/bse_group_A.csv --strategy graphgen --res 1M --plots_dir $tgt_dir --plot_period 100 --fig_ratio 2
