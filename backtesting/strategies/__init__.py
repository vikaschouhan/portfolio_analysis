import os, sys

module_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_path)

from   ma_cross import LongShortEMA
from   donch_channel import Donch
from   donch_bas_crossover import DonchBasCrossOver
from   donch_breakout_long_bascross_short import DonchLongOnly1
from   ema_ema1_cross import EMA_EMA1
from   ren3_cross import Ren3Cross, Ren3FCross, Ren3HCross
from   supertrend_rsi import SupertrendRSILong, SupertrendRSIShort

strategy_map = {
            'ma_cross'                                                  : LongShortEMA,
            'donch_channel'                                             : Donch,
            'donch_bas_cross'                                           : DonchBasCrossOver,
            'donch_breakout_long_bascross_short'                        : DonchLongOnly1,
            'ema_ema1_cross'                                            : EMA_EMA1,
            'ren3_cross'                                                : Ren3Cross,
            'ren3h_cross'                                               : Ren3HCross,
            'ren3f_cross'                                               : Ren3FCross,
            'supertrend_rsi_long'                                       : SupertrendRSILong,
            'supertrend_rsi_short'                                      : SupertrendRSIShort,
        }
