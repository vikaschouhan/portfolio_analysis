rm -rf ~/candles_nse_intraday_supertrend_rsi

echo "Analysing FNO GAINERS....."
python scripts/scan_nse_live_analysis.py --ofile /tmp/__x.csv --key fno_gainers
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 10 --res 5m --sfile /tmp/__x.csv --plots_dir ~/candles_nse_intraday_supertrend_rsi --strategy scanner --strategy_name supertrend_rsi_long

echo "Analysing FNO LOSERS....."
python scripts/scan_nse_live_analysis.py --ofile /tmp/__y.csv --key fno_losers
python scripts/scan_security_list_technical.py --invs scripts/db/investing_dot_com_security_dict.py --lag 10 --res 5m --sfile /tmp/__y.csv --plots_dir ~/candles_nse_intraday_supertrend_rsi --strategy scanner --strategy_name supertrend_rsi_short
