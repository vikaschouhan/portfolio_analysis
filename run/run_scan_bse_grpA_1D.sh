tgt_dir=~/sc_db_github_files/candles_bse_grpA_1D
rm -rf $tgt_dir
mkdir -p $tgt_dir
python3 scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 20 --res 1D --sfile scripts/db/bse_group_A.csv --plots_dir $tgt_dir
