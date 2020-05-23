import pandas as pd

################################################################
# For handling OHLCV price data
class Ohlcv(object):
    OPEN     = 'open'
    CLOSE    = 'close'
    HIGH     = 'high'
    LOW      = 'low'
    VOLUME   = 'volume'
    OHLC     = [OPEN, HIGH, LOW, CLOSE]
    OHLCV    = OHLC + [VOLUME]
    LIST_ALL = OHLCV + ['all']
    COL_MAP  = {'o': OPEN, 'h': HIGH, 'l': LOW, 'c':CLOSE, 'v':VOLUME}

    def __c_columns_to_keys(self, columns):
        cols = list(columns)
        assert len(set(cols) - set(self.COL_MAP.keys())) == 0, 'Invalid columns "{}"'.format(columns)
        return [self.COL_MAP[k] for k in cols]
    # enddef

    def __c_columns_heur1_match(self, columns, df, en=True):
        if en:
            cols_assumed = [x.lower() for x in list(columns)]
            cols_passed  = [x[0].lower() for x in df.columns.to_list()]
            assert cols_assumed == cols_passed, '>> Passed columns="{}" doesnot seem to match dataframe columns="{}"'.format(columns, df.columns)
        # endif
    # enddef

    def __init__(self, df: pd.DataFrame, columns: str='ohlcv', match_cols: bool=True):
        # Run a heuristic check on columns
        self.__c_columns_heur1_match(columns, df, match_cols)
        # Print some info
        print('>> Assumed columns="{}", CSV columns="{}". Please change if not applicable !!'.format(list(columns), df.columns.to_list()))
        # Assign data
        self.data = df
        # New column map
        new_cols = self.__c_columns_to_keys(columns)
        # Rename columns
        self.data.set_axis(new_cols, axis='columns', inplace=True)
        # Change index to datetime
        self.data.index = pd.to_datetime(self.data.index)
    # enddef

    def __getitem__(self, key):
        if key in self.OHLCV:
            return self.data[key]
        elif key == 'all':
            return self.data
        else:
            raise ValueError('Unsupported key {} in Ohlcv[]. Supported keys are = {}'.format(key, self.OHLCV))
        # endif
    # enddef

    def __repr__(self):
        return self.data.__repr__()
    # enddef

    def __str__(self):
        return self.data.__str__()
    # enddef

    @classmethod
    def from_df(cls, df, columns='ohlcv'):
        return cls(df, columns=columns)
    # enddef

    @classmethod
    def from_csv_file(cls, csv_file, columns='ohlcv'):
        return cls.from_df(pd.read_csv(csv_file, index_col=0), columns=columns)
    # enddef

    def resample(self, time_frame):
        return Ohlcv.from_df(self.data.resample(time_frame).agg({
            self.OPEN  : 'first',
            self.HIGH  : 'max',
            self.LOW   : 'min',
            self.CLOSE : 'last',
            self.VOLUME: 'sum' }), columns=self.OHLCV)
    # enddef
# endclass
