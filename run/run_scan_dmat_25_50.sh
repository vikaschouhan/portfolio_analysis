rm -rf ~/dmat_25_50
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile ~/dmat_sym_name_list.csv --plots_dir ~/dmat_25_25 --opts ema_fast_period=25,ema_slow_period=50
