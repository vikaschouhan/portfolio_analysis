tgt_dir=~/sc_db_github_files/dmat_9_14
rm -rf $tgt_dir
mkdir -p $tgt_dir
#python scripts/scan_dmat.py
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile ~/dmat_sym_name_list.csv --plots_dir $tgt_dir --opts ema_fast_period=9,ema_slow_period=14,ema_opt_period=21
