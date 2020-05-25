import  numpy as np
cimport numpy as np
cimport cython

ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef __np_trail_fixed_loss(DTYPE_t[:] pos, DTYPE_t[:] price, double x, DTYPE_t[:] _loss):
    cdef int rn_indx    = 0   # Running first index
    cdef double rn_max  = 0.0 # Running maximum
    cdef double rn_min  = 0.0 # Running minium

    # Iterate over all elements
    for indx in range(len(pos)):
        if indx == 0:
            rn_pos    = pos[indx]
            rn_indx   = indx
        elif pos[indx] != pos[indx-1]:
            rn_pos    = pos[indx]
            rn_indx   = indx
        # endif

        # Calculate running maximums and minimums
        if price[indx] > price[rn_indx]:
            rn_max = price[indx]
        elif price[indx] < price[rn_indx]:
            rn_min = price[indx]
        else:
            pass
        # endif
      
        # Calculate trailing loss 
        if rn_pos > 0: # If current position is long
            _loss[indx] = rn_max - pos[indx]*x
        elif rn_pos < 0: # If current position is short
            _loss[indx] = rn_min - pos[indx]*x
        # endif
    # endfor
# enddef 

cpdef np.ndarray np_trail_fixed_loss(np.ndarray[DTYPE_t, ndim=1] pos, np.ndarray[DTYPE_t, ndim=1] price, x: double):
    cdef np.ndarray[DTYPE_t, ndim=1] _loss = np.zeros_like(price)
    cdef DTYPE_t[:] __loss = _loss
    cdef DTYPE_t[:] __pos  = pos
    cdef DTYPE_t[:] __price = price

    __np_trail_fixed_loss(__pos, __price, x,  __loss)

    return _loss
# enddef
