import os, sys

module_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_path)

from   ma_cross import LongShortEMA
from   donch_channel import Donch
from   ema_ema1_cross import EMA_EMA1
from   ren3_cross import Ren3Cross, Ren3FCross, Ren3HCross

strategy_map = {
            'ma_cross'                          : LongShortEMA,
            'donch_channel'                     : Donch,
            'ema_ema1_cross'                    : EMA_EMA1,
            'ren3_cross'                        : Ren3Cross,
            'ren3h_cross'                       : Ren3HCross,
            'ren3f_cross'                       : Ren3FCross,
        }
