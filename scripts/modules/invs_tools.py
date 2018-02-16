from   sklearn.cluster import MeanShift, estimate_bandwidth
import numpy as np
import pandas as pd

# Support resistance lines
def supp_res(j_data, n_samples=200, column='c'):
    data = j_data.as_matrix(columns=[column])

    bandwidth = estimate_bandwidth(data, quantile=0.1, n_samples=n_samples)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data)

    #Calculate Support/Resistance
    ml_results = []
    for k in range(len(np.unique(ms.labels_))):
        my_members = ms.labels_ == k
        values = data[my_members, 0]
        #print values

        # find the edges
        ml_results.append(min(values))
        ml_results.append(max(values))
    # endfor

    # Sort then convert to pandas Series
    ml_results.sort()
    return pd.Series(ml_results)
# enddef
