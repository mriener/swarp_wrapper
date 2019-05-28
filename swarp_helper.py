import os
import numpy as np

from astropy.wcs import WCS
from astropy.io import fits

def astrometry_info(filepath):
    data = fits.getdata(filepath)
    header = fits.getheader(filepath)

    wcs = WCS(header)

    sum_cols = np.sum(data, axis=0)
    nonzero_cols = np.count_nonzero(sum_cols)
    sum_rows = np.sum(data, axis=1)
    nonzero_rows = np.count_nonzero(sum_rows)

    x_offset = 0
    for item in sum_cols:
        if item == 0:
            x_offset += 1
        else:
            break

    y_offset = 0
    for item in sum_rows:
        if item == 0:
            y_offset += 1
        else:
            break

    xpix_center = x_offset + (nonzero_cols - 1) / 2
    ypix_center = y_offset + (nonzero_rows - 1) / 2

    xcoord_center, ycoord_center = wcs.all_pix2world(xpix_center, ypix_center, 0)

    print('CENTER {}, {}'.format(xcoord_center, ycoord_center))
    print('IMAGE_SIZE {}, {}'.format(nonzero_cols, nonzero_rows))
