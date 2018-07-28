import os, sys

module_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(module_path)

from   ma_cross import LongShortEMA
from   donch_channel import Donch

strategy_map = {
            'ma_cross'                          : LongShortEMA,
            'donch_channel'                     : Donch,
        }
