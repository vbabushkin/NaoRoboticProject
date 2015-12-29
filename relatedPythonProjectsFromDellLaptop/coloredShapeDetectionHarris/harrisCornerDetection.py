__author__ = 'vahan'

from scipy import *
from scipy import signal
import Image
import filtertools
import harris


im = array(Image.open('/home/vahan/PycharmProjects/visionForLegoGame/images/initialImage.jpg').convert("L"))
harrisim = harris.compute_harris_response(im)
filtered_coords = harris.get_harris_points(harrisim,6)
harris.plot_harris_points(im, filtered_coords)
