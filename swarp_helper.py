import os
import numpy as np

from astropy.wcs import WCS
from astropy.io import fits


def sequence_of_leading_zeros(array):
    count_zeros = 0
    for item in array:
        if item == 0:
            count_zeros += 1
        else:
            break
    return count_zeros


def astrometry_info(filepath):
    data = fits.getdata(filepath)
    header = fits.getheader(filepath)

    wcs = WCS(header)

    sum_cols = np.sum(data, axis=0)
    sum_rows = np.sum(data, axis=1)

    zero_cols_start = sequence_of_leading_zeros(sum_cols)
    zero_cols_end = sequence_of_leading_zeros(sum_cols[::-1])

    zero_rows_start = sequence_of_leading_zeros(sum_rows)
    zero_rows_end = sequence_of_leading_zeros(sum_rows[::-1])

    size_x = sum_cols.size - zero_cols_start - zero_cols_end
    size_y = sum_rows.size - zero_rows_start - zero_rows_end

    xpix_center = zero_cols_start + (size_x - 1) / 2
    ypix_center = zero_rows_start + (size_y - 1) / 2

    xcoord_center, ycoord_center = wcs.all_pix2world(xpix_center, ypix_center, 0)

    print('CENTER {}, {}'.format(xcoord_center, ycoord_center))
    print('IMAGE_SIZE {}, {}'.format(size_x, size_y))


def get_center_coordinates_for_swarp(header):
    wcs = WCS(header)

    x_wcs_min, y_wcs_min, z_wcs_min = wcs.wcs_pix2world(0, 0, 0, 0)
    x_wcs_max, y_wcs_max, z_wcs_max = wcs.wcs_pix2world(
        header['NAXIS1'] - 1, header['NAXIS2'] - 1, 0, 0)

    x_wcs_ctr = (x_wcs_min + x_wcs_max) / 2
    y_wcs_ctr = (y_wcs_min + y_wcs_max) / 2

    return x_wcs_ctr, y_wcs_ctr
