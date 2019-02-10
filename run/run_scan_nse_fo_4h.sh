tgt_dir=~/sc_db_github_files/candles_fo_mktlots_4h
rm -rf $tgt_dir
mkdir -p $tgt_dir
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 10 --res 4h --sfile scripts/db/fo_mktlots.csv --plots_dir $tgt_dir
