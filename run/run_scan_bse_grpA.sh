rm -rf ~/candles_bse_group_A_14_21
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile scripts/db/bse_group_A.csv --plots_dir ~/candles_bse_group_A --ma_plist 14,21
