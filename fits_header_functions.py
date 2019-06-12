import getpass
import socket
import warnings

import numpy as np

from astropy.io import fits
from astropy.wcs import WCS
from datetime import datetime


def change_header(header, format='pp', keep_axis='1', comments=[], dct_keys={}):
    """Change the FITS header of a file.

    Parameters
    ----------
    header : astropy.io.fits.Header
        Header of the FITS array.
    format : 'pp' or 'pv'
        Describes the format of the resulting 2D header: 'pp' for position-position data and 'pv' for position-velocity data.
    keep_axis : '1' or '2'
        If format is set to 'pv', this specifies which spatial axis is kept: '1' - NAXIS1 stays and NAXIS2 gets removed, '2' - NAXIS2 stays and NAXIS1 gets removed
    comments : list
        Comments that are added to the FITS header under the COMMENT keyword.
    dct_keys : dict
        Dictionary that specifies which keywords and corresponding values should be added to the FITS header.

    Returns
    -------
    astropy.io.fits.Header
        Updated FITS header.

    """
    prihdr = fits.Header()
    for key in ['SIMPLE', 'BITPIX']:
        prihdr[key] = header[key]

    prihdr['NAXIS'] = 2
    prihdr['WCSAXES'] = 2

    keys = ['NAXIS', 'CRPIX', 'CRVAL', 'CDELT', 'CUNIT', 'CROTA']

    if format == 'pv':
        keep_axes = [keep_axis, '3']
        prihdr['CTYPE1'] = '        '
        prihdr['CTYPE2'] = '        '
    else:
        keep_axes = ['1', '2']
        keys += ['CTYPE']

    for key in keys:
        if key + keep_axes[0] in header.keys():
            prihdr[key + '1'] = header[key + keep_axes[0]]
        if key + keep_axes[1] in header.keys():
            prihdr[key + '2'] = header[key + keep_axes[1]]

    for key_new, axis in zip(['CDELT1', 'CDELT2'], keep_axes):
        key = 'CD{a}_{a}'.format(a=axis)
        if key in header.keys():
            prihdr[key_new] = header[key]

    prihdr['AUTHOR'] = getpass.getuser()
    prihdr['ORIGIN'] = socket.gethostname()
    prihdr['DATE'] = (datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), '(GMT)')

    for comment in comments:
        prihdr['COMMENT'] = comment

    for key, val in dct_keys.items():
        prihdr[key] = val

    return prihdr


def update_header(header, comments=[], remove_keywords=[], update_keywords={},
                  remove_old_comments=False, write_meta=True):
    """Update FITS header.

    Parameters
    ----------
    header : astropy.io.fits.Header
        FITS header.
    comments : list
        List of comments that get written to the FITS header with the 'COMMENT' keyword.
    remove_keywords : list
        List of FITS header keywords that should be removed.
    update_keywords : dict
        Dictionary of FITS header keywords that get updated.
    remove_old_comments : bool
        Default is `False`. If set to `True`, existing 'COMMENT' keywords of the FITS header are removed.
    write_meta : bool
        Default is `True`. Adds or updates 'AUTHOR', 'ORIGIN', and 'DATE' FITS header keywords.

    Returns
    -------
    header : astropy.io.fits.Header
        Updated FITS header.

    """
    if remove_old_comments:
        while ['COMMENT'] in header.keys():
            header.remove('COMMENT')

    for keyword in remove_keywords:
        if keyword in header.keys():
            header.remove(keyword)

    for keyword, value in update_keywords.items():
        header[keyword] = value[0][1]

    if write_meta:
        header['AUTHOR'] = getpass.getuser()
        header['ORIGIN'] = socket.gethostname()
        header['DATE'] = (datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), '(GMT)')

    for comment in comments:
        header['COMMENT'] = comment

    return header


def remove_additional_axes(data, header, max_dim=3,
                           keep_only_wcs_keywords=False):
    """Remove additional axes (Stokes, etc.) from spectral cube.

    The old name of the function was 'remove_stokes'.

    Parameters
    ----------
    data : numpy.ndarray
        Data of the FITS array.
    header : astropy.io.fits.Header
        Header of the FITS array.
    max_dim : int
        Maximum number of dimensions the final data array should have. The default value is '3'.
    keep_only_wcs_keywords : bool
        Default is `False`. If set to `True`, the FITS header is stripped of all keywords other than the required minimum WCS keywords.

    Returns
    -------
    data : numpy.ndarray
        Data of the FITS array, corrected for additional unwanted axes.
    header : astropy.io.fits.Header
        Updated FITS header.

    """
    wcs = WCS(header)

    if header['NAXIS'] <= max_dim and wcs.wcs.naxis <= max_dim:
        return data, header

    warnings.warn('remove additional axes (Stokes, etc.) from cube and/or header')

    while data.ndim > max_dim:
        data = np.squeeze(data, axis=(0,))

    wcs_header_old = wcs.to_header()
    while wcs.wcs.naxis > max_dim:
        axes = range(wcs.wcs.naxis)
        wcs = wcs.dropaxis(axes[-1])
    wcs_header_new = wcs.to_header()

    if keep_only_wcs_keywords:
        hdu = fits.PrimaryHDU(data=data, header=wcs_header_new)
        return hdu.data, hdu.header

    wcs_header_diff = fits.HeaderDiff(wcs_header_old, wcs_header_new)
    header_diff = fits.HeaderDiff(header, wcs_header_new)
    update_header(header, remove_keywords=wcs_header_diff.diff_keywords[0],
                  update_keywords=header_diff.diff_keyword_values,
                  write_meta=False)

    return data, header


def add_cdelt_keys_to_header(header):
    header['CDELT1'] = header['CD1_1']
    header.remove('CD1_1')
    header.remove('CD1_2')

    header['CDELT2'] = header['CD2_2']
    header.remove('CD2_1')
    header.remove('CD2_2')

    return header


def add_keywords_spectral_axis(header_new, header_old):
    for keyword in ['CTYPE3', 'CRVAL3', 'CRPIX3', 'CDELT3', 'CUNIT3', 'CROTA3']:
        if keyword in header_old.keys():
            header_new[keyword] = header_old[keyword]
    return header_new
