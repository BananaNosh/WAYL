import numpy as np
cimport cython

# @cython.boundscheck(False)
def cy_convolve(unsigned char[:, ::1] im, double[:, ::1] kernel, Py_ssize_t[:, ::1] points):
    cdef Py_ssize_t i, j, y, x, n, ks = kernel.shape[0]
    cdef Py_ssize_t npoints = points.shape[0]
    cdef double[::1] responses = np.zeros(npoints, dtype='f8')

    for n in range(npoints):
        y = points[n, 0]
        x = points[n, 1]
        for i in range(ks):
            for j in range(ks):
                print(i, j, x, y)
                responses[n] += im[y+i, x+j] * kernel[i, j]
    return np.asarray(responses)