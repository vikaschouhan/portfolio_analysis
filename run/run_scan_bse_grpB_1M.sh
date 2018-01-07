rm -rf ~/candles_bse_group_B_1M
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --ma_plist '9,14,21' --lag 180 --res 1M --sfile scripts/db/bse_group_B.csv --plots_dir ~/candles_bse_group_B_1M
