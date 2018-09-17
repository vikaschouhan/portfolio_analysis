rm -rf ~/dmat_9_14
#python scripts/scan_dmat.py
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile ~/dmat_sym_name_list.csv --plots_dir ~/dmat_9_14 --opts ema_fast_period=9,ema_slow_period=14,ema_opt_period=21
