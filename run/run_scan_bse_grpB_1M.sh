tgt_dir=~/sc_db_github_files/candles_bse_group_B_1M
rm -rf $tgt_dir
mkdir -p $tgt_dir
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --opts='ema_fast_period=9,ema_slow_period=14' --lag 180 --res 1M --sfile scripts/db/bse_group_B.csv --plots_dir $tgt_dir
