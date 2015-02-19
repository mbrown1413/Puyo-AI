
from __future__ import division
import os

import cv2
import numpy
from matplotlib import pyplot
from matplotlib.colors import rgb_to_hsv

SAMPLE_DIR = "vision_training/cropped_cell_data/"

COLOR_NAMES = (
    "background",
    "nuisance",
    "red",
    "green",
    "blue",
    "yellow",
    "purple",
)

COLOR_VALUES = {
    "background": "grey",
    "nuisance": "black",
    "red": "red",
    "green": "green",
    "blue": "blue",
    "yellow": "yellow",
    "purple": "purple",
}

def plot_color(color, hsv_channel):
    yss = []
    for filename in os.listdir(os.path.join(SAMPLE_DIR, color)):

        filepath = os.path.join(SAMPLE_DIR, color, filename)
        rgb = cv2.imread(filepath).reshape((1, -1, 3))
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV) / 255

        data = [p[hsv_channel] for p in hsv.reshape((-1, 3))]

        ys, xs = numpy.histogram(data, 15, (0, 1))
        ys = numpy.append(ys, [ys[0]])
        pyplot.plot(xs, ys, color=COLOR_VALUES[color], alpha=0.1)

        yss.append(ys)

    # Average data from each sample
    ys = numpy.sum(yss, axis=0) / len(yss)

    # Plot averages with min/max error bars
    mins = numpy.min(yss, axis=0)
    maxs = numpy.max(yss, axis=0)
    errors = (numpy.abs(mins-ys), numpy.abs(maxs-ys))
    pyplot.errorbar(xs, ys, yerr=errors, linewidth=5, alpha=0.5, color=COLOR_VALUES[color])

    return ys

def plot(hsv_channel):
    histograms = {}

    for color in COLOR_NAMES:
        hist = plot_color(color, hsv_channel)
        histograms[color] = tuple(hist)[:-1]

    return histograms

def main():
    import sys
    if len(sys.argv) < 2:
        channel = "Hue"
    elif len(sys.argv) > 2:
        print "Too many arguments!"
        sys.exit()
    else:
        channel = sys.argv[1]

    CHANNEL_INDEXES = {"hue": 0, "saturation": 1, "value": 2}

    histograms = plot(CHANNEL_INDEXES[channel.lower()])

    from pprint import pprint
    pprint(histograms)

    pyplot.title("{} Frequency by Bean Color".format(channel))
    pyplot.ylabel("Frequency")
    pyplot.xlabel(channel)
    pyplot.show()


if __name__ == "__main__":
    main()
