import numpy as np
from cy_partial_convolution import cy_convolve


def partial_convolve(im, kernel, points):
    ks = kernel.shape[0]//2
    data = np.pad(im, ks, mode='constant', constant_values=0)
    return cy_convolve(data, kernel, points)