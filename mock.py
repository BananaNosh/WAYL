import numpy


def get_random_gaze_positions(count, x_range=range(1600), y_range=range(900)):
    xs = numpy.random.choice(x_range, count)
    ys = numpy.random.choice(y_range, count)
    return list(zip(xs.astype(int), ys.astype(int)))
