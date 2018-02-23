rm -rf ~/candles_bse_grpA_1D
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 20 --res 1D --sfile scripts/db/bse_group_A.csv --plots_dir ~/candles_bse_grpA_1D
