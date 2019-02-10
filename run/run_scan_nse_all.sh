tgt_dir=~/sc_db_github_files/candles_NSEEQ
rm -rf $tgt_dir
mkdir -p $tgt_dir
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 60 --res 1W --sfile scripts/db/nse_all_eq.csv --plots_dir $tgt_dir
