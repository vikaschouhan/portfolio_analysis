from   sklearn.cluster import MeanShift, estimate_bandwidth
import numpy as np
import pandas as pd
import invs_utils

# Support resistance lines
def supp_res(j_data, n_samples=200, mode='c', ema_period=None):
    if ema_period:
        d_n = invs_utils.d_ema(j_data, ema_period, mode=mode)
    else:
        d_n = invs_utils.s_mode(j_data, mode)
    # endif

    # Reshape to appropriate shape
    d_n = d_n.values.reshape((len(d_n), 1))

    bandwidth = estimate_bandwidth(d_n, quantile=0.1, n_samples=n_samples)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(d_n)

    #Calculate Support/Resistance
    ml_results = []
    for k in range(len(np.unique(ms.labels_))):
        my_members = ms.labels_ == k
        values = d_n[my_members, 0]
        #print values

        # find the edges
        ml_results.append(min(values))
        ml_results.append(max(values))
    # endfor

    # Sort then convert to pandas Series
    ml_results.sort()
    return pd.Series(ml_results)
# enddef

def pivots0(j_data):
    PP = pd.Series((j_data['h'] + j_data['l'] + j_data['c']) / 3)
    R1 = pd.Series(2 * PP - j_data['l'])
    S1 = pd.Series(2 * PP - j_data['h'])
    R2 = pd.Series(PP + j_data['h'] - j_data['l'])
    S2 = pd.Series(PP - j_data['h'] + j_data['l'])
    R3 = pd.Series(j_data['h'] + 2 * (PP - j_data['l']))
    S3 = pd.Series(j_data['l'] - 2 * (j_data['l'] - PP))
    psr = {'PP':PP, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}
    return psr
# enddef
