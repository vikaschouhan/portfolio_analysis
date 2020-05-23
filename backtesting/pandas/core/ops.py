import pandas as pd

#################################################
# Operations on Pandas Series
def op_crossover(s1, s2, lag=1):
    return (s1 > s2) & (s1.shift(lag) < s2.shift(lag))
# enddef

def op_crossunder(s1, s2, lag=1):
    return (s1 < s2) & (s1.shift(lag) > s2.shift(lag))
# enddef

def op_ref(s, period=1):
    return s.shift(period)
# enddef
