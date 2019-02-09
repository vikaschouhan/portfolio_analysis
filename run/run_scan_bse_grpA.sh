tgt_dir=~/sc_db_github_files/candles_bse_group_A_14_21
rm -rf $tgt_dir
mkdir -p $tgt_dir
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile scripts/db/bse_group_A.csv --plots_dir $tgt_dir --opts ema_fast_period=14,ema_slow_period=21,ema_opt_period=9
