# Author : Vikas Chouhan (presentisgood@gmail.com)
# 2020

import  numpy as np
cimport numpy as np
cimport cython

ctypedef np.float64_t DTYPE_t

cdef double __calc_stop_fixed(double p, double l, double x):
    return p - l*x
# enddef

cdef double __calc_stop_perc(double p, double l, double x):
    return p * (1 - l*x/100)
# enddef

cdef double __max(double __x, double __y):
    if __x > __y:
        return __x
    else:
        return __y
    # endif
# enddef

cdef double __min(double __x, double __y):
    if __x < __y:
        return __x
    else:
        return __y
    # endif
# enddef

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef __np_trail_stop(DTYPE_t[:] pos, DTYPE_t[:] price, double x, DTYPE_t[:] _loss, int perc_loss=0):
    cdef int rn_indx    = 0   # Running first index
    cdef double rn_max  = 0.0 # Running maximum
    cdef double rn_min  = 0.0 # Running minium
    cdef double loss_t  = 0.0
    cdef double (*loss_fn)(double, double, double)

    if perc_loss:
        loss_fn = __calc_stop_perc
    else:
        loss_fn = __calc_stop_fixed
    # endif

    # Iterate over all elements
    for indx in range(len(pos)):
        if indx == 0:
            rn_pos    = pos[indx]
            rn_indx   = indx
            rn_max    = price[rn_indx]
            rn_min    = price[rn_indx]
        elif pos[indx] != pos[indx-1]:
            rn_pos    = pos[indx]
            rn_indx   = indx
            rn_max    = price[rn_indx]
            rn_min    = price[rn_indx]
        else:
            # Calculate running maximums and minimums
            if price[indx] > price[indx-1]:
                rn_max = price[indx]
            elif price[indx] < price[indx-1]:
                rn_min = price[indx]
            else:
                pass
            # endif
        # endif
      
        # Calculate trailing loss 
        if rn_pos > 0: # If current position is long
            _loss[indx] = _loss[indx-1]
            loss_t = loss_fn(rn_max, pos[indx], x)
            if loss_t > _loss[indx]:
                _loss[indx] = loss_t
            # endif
        elif rn_pos < 0: # If current position is short
            _loss[indx] = _loss[indx-1]
            loss_t = loss_fn(rn_min, pos[indx], x)
            if loss_t < _loss[indx]:
                _loss[indx] = loss_t
            # endif
        # endif
    # endfor
# enddef

cpdef np.ndarray np_trail_fixed_stop(np.ndarray[DTYPE_t, ndim=1] pos, np.ndarray[DTYPE_t, ndim=1] price, x: double):
    cdef np.ndarray[DTYPE_t, ndim=1] _loss = np.zeros_like(price)
    cdef DTYPE_t[:] __loss = _loss
    cdef DTYPE_t[:] __pos  = pos
    cdef DTYPE_t[:] __price = price

    __np_trail_stop(__pos, __price, x,  __loss, 0)

    return _loss
# enddef

cpdef np.ndarray np_trail_perc_stop(np.ndarray[DTYPE_t, ndim=1] pos, np.ndarray[DTYPE_t, ndim=1] price, x: double):
    cdef np.ndarray[DTYPE_t, ndim=1] _loss = np.zeros_like(price)
    cdef DTYPE_t[:] __loss = _loss
    cdef DTYPE_t[:] __pos  = pos
    cdef DTYPE_t[:] __price = price

    __np_trail_stop(__pos, __price, x,  __loss, 1)

    return _loss
# enddef

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef __np_ind_supertrend(DTYPE_t[:] __high, DTYPE_t[:] __low, DTYPE_t[:] __close, DTYPE_t[:] __atr, double mult, DTYPE_t[:] __strend):
    cdef DTYPE_t[:] __f_up  = __high.copy()
    cdef DTYPE_t[:] __f_dn  = __high.copy()
    cdef DTYPE_t[:] __tpos  = __high.copy()
    cdef double __avg_t = 0.0
    cdef double __bas_u = 0.0
    cdef double __bas_l = 0.0

    for i in range(len(__high)):
        __avg_t      = (__high[i] + __low[i])/2
        __bas_u      = __avg_t - mult * __atr[i]
        __bas_l      = __avg_t + mult * __atr[i]
        __f_up[i]    = __max(__bas_u, __f_up[i-1]) if __close[i-1] > __f_up[i-1] else __bas_u
        __f_dn[i]    = __min(__bas_l, __f_dn[i-1]) if __close[i-1] < __f_dn[i-1] else __bas_l
        __tpos[i]    = 1.0 if __close[i] > __f_dn[i-1] else -1.0 if __close[i] < __f_up[i-1] else __tpos[i-1]
        __strend[i]  = __f_up[i] if __tpos[i] == 1.0 else __f_dn[i] if __tpos[i] == -1.0 else __strend[i-1]
    # endfor
# enddef

cpdef np.ndarray np_ind_supertrend(np.ndarray[DTYPE_t, ndim=1] high, np.ndarray[DTYPE_t, ndim=1] low,
    np.ndarray[DTYPE_t, ndim=1] close, np.ndarray[DTYPE_t, ndim=1] atr, mult: double):
    cdef np.ndarray[DTYPE_t, ndim=1] _strend = np.zeros_like(high)
    cdef DTYPE_t[:] __strend = _strend
    cdef DTYPE_t[:] __high   = high
    cdef DTYPE_t[:] __low    = low
    cdef DTYPE_t[:] __close  = close
    cdef DTYPE_t[:] __atr    = atr

    __np_ind_supertrend(__high, __low, __close, __atr, mult, __strend)

    return _strend
# enddef
