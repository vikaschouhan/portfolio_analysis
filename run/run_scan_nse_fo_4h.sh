rm -rf ~/candles_fo_mktlots_4h
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 10 --res 4h --sfile scripts/db/fo_mktlots.csv --plots_dir ~/candles_fo_mktlots_4h
