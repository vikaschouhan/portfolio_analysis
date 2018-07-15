rm -rf ~/screener_in
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile ~/screener_in_report.csv --plots_dir ~/screener_in
