tgt_dir=~/sc_db_github_files/nse_fo_15m_csv
rm -rf $tgt_dir
mkdir -p $tgt_dir
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --strategy csvgen --res 15m --sfile scripts/db/fo_mktlots.csv --plots_dir $tgt_dir
