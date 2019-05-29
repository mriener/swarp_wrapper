#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import numpy as np

from astropy.io import fits
from tqdm import tqdm

class Swarp(object):
    def __init__(self, list_path_to_cubes, settings_file=None):
        self.list_path_to_cubes = list_path_to_cubes
        self.settings_file = settings_file

        self.max_channels = None
        self.list_of_channels = []

        self.filename_final = None

        self.verbose = True
        self.overwrite = True
        self.remove_temorary_files = True

        self.path_swarp = None

        self.list_slices = []
        self.list_of_images = None
        self.path_images = None

    def slice_cubes(self):
        self.check_channels()

        start = True
        for path_to_cube in self.list_path_to_cubes:
            self.dirname = os.path.dirname(path_to_cube)
            self.file = os.path.basename(path_to_cube)
            self.filename, self.file_extension = os.path.splitext(self.file)

            if self.verbose:
                print("slicing cube {}...".format(self.filename))

            hdu = fits.open(path_to_cube)[0]
            self.data = hdu.data
            self.header = hdu.header

            if len(self.data.shape) == 4:
                self.correct_stokes()

            self.max_channels = self.check_channels()

            if start:
                start = False

                if self.path_swarp is None:
                    self.path_swarp = os.path.join(self.dirname, 'swarp_files')

                self.path_channels = os.path.join(self.path_swarp, 'channels')
                if not os.path.exists(self.path_channels):
                    os.makedirs(self.path_channels)

                self.path_slices = os.path.join(self.path_swarp, 'slices')
                if not os.path.exists(self.path_slices):
                    os.makedirs(self.path_slices)

                for channel in range(self.max_channels):
                    self.list_of_channels.append(
                            'channel_{:04d}'.format(channel))

            for channel in range(self.max_channels):
                if channel > (self.header['NAXIS3'] - 1):
                    "create 2D array with nan values here"
                    slice_data = np.empty(
                            (self.header['NAXIS2'], self.header['NAXIS1']))
                    slice_data[:] = np.NAN
                else:
                    slice_data = self.data[channel, :, :]
                slice_header = self.make_2d_header()

                suffix = 'channel_{:04d}'.format(channel)

                filename = '{}_{}.fits'.format(
                        self.filename, suffix)
                path_to_file = os.path.join(self.path_channels, filename)

                fits.writeto(path_to_file, slice_data, header=slice_header,
                             overwrite=self.overwrite)

    def make_2d_header(self):
        header = self.header.copy()

        header['NAXIS'] = 2
        for keyword in ['NAXIS3', 'CRPIX3', 'CDELT3', 'CRVAL3',
                        'CTYPE3', 'CROTA3']:
            if keyword in header.keys():
                header.remove(keyword)
        return header

    def check_channels(self):
        list_channels = []
        for path_to_cube in self.list_path_to_cubes:
            hdu = fits.open(path_to_cube)[0]
            header = hdu.header
            list_channels.append(header['NAXIS3'])
        return max(list_channels)

    def correct_stokes(self):
        if self.verbose:
            print('correct for Stokes')
        self.data = np.squeeze(self.data, axis=(0,))
        self.header['NAXIS'] = 3
        for keyword in ['NAXIS4', 'CRPIX4', 'CDELT4', 'CRVAL4',
                        'CTYPE4', 'CROTA4']:
            if keyword in self.header.keys():
                self.header.remove(keyword)

    def swarp_slices(self):
        ""
        if self.verbose:
            print("swarp slices...")

        pbar = tqdm(total=len(self.list_of_channels))
        for channel in self.list_of_channels:
            # if self.verbose:
            #     print("slice {}...".format(channel))
            pbar.update(1)
            nameListFiles = os.path.join(
                    self.path_channels, '*{}*'.format(channel))
            filename = '{}.fits'.format(channel)
            self.list_slices.append(filename)
            cwd = os.getcwd()
            os.chdir(self.path_slices)
            os.system('swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                    a=nameListFiles, b=self.settings_file, c=filename))
            os.chdir(cwd)
            # if self.remove_temorary_files:
            #     os.system('rm {}'.format(nameListFiles))
        pbar.close()

    def assemble_cube(self):
        if self.verbose:
            print("assembling final cube...")
        os.chdir(self.path_slices)

        start = True
        pbar = tqdm(total=len(self.list_slices))
        for idx, filename in enumerate(self.list_slices):
            pbar.update(1)
            hdu = fits.open(filename)[0]
            data = hdu.data
            if start:
                start = False
                header = hdu.header
                array = self.initialize_array(header)

                header = self.correct_swarp_header(header)

            array[idx, :, :] = data
        pbar.close()

        if self.filename_final is None:
            self.filename_final = 'swarp_final'

        path_to_file = os.path.join(
                self.path_swarp, '{}.fits').format(self.filename_final)
        fits.writeto(path_to_file, array, header=header,
                     overwrite=self.overwrite)

        os.chdir(self.path_swarp)
        path_log_file = os.path.join(self.path_slices, 'swarp.xml')
        path_log_file_new = os.path.join(self.path_swarp, '{}.xml'.format(self.filename_final))
        os.system('mv {} {}'.format(path_log_file, path_log_file_new))

        if self.remove_temorary_files:
            os.system('rm -r {}'.format(self.path_slices))
            os.system('rm -r {}'.format(self.path_channels))
            # for filename in self.list_slices:
            #     os.system('rm {}'.format(filename))

    def correct_swarp_header(self, header):
        header['NAXIS'] = 3
        header['CTYPE1'] = header['CTYPE1']
        header['CUNIT1'] = header['CUNIT1']
        header['CRVAL1'] = header['CRVAL1']
        header['CRPIX1'] = header['CRPIX1']
        header['CDELT1'] = header['CD1_1']
        header.remove('CD1_1')
        header.remove('CD1_2')

        header['CTYPE2'] = header['CTYPE2']
        header['CUNIT2'] = header['CUNIT2']
        header['CRVAL2'] = header['CRVAL2']
        header['CRPIX2'] = header['CRPIX2']
        header['CDELT2'] = header['CD2_2']
        header.remove('CD2_1')
        header.remove('CD2_2')

        header['NAXIS3'] = self.header['NAXIS3']
        header['CTYPE3'] = self.header['CTYPE3']
        # header['CUNIT3'] = 'm s-1'
        header['CRVAL3'] = self.header['CRVAL3']
        header['CRPIX3'] = self.header['CRPIX3']
        header['CDELT3'] = self.header['CDELT3']

        return header

    def assemble_image(self):
        if self.verbose:
            print("assembling final image...")
        os.chdir(self.path_images)
        print(self.list_of_images)
        if isinstance(self.list_of_images, list):
            string = ''
            for img in self.list_of_images:
                string += img + ' '
            self.list_of_images = string
        filename = os.path.join(self.path_images, '{}.fits'.format(self.filename_final))
        print(filename)
        os.system('swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                a=self.list_of_images, b=self.settings_file, c=filename))

    def initialize_array(self, header):
        x = header['NAXIS1']
        y = header['NAXIS2']
        z = int(self.max_channels)

        array = np.zeros([z, y, x], dtype=np.float32)

        return array

    def restore_nan_values(self):
        if self.verbose:
            print("restoring nan values...")
        if self.path_swarp is not None:
            os.chdir(self.path_swarp)
        else:
            os.chdir(self.path_images)

        hdu = fits.open('{}.fits'.format(self.filename_final))[0]
        data = hdu.data
        header = hdu.header

        data[data < -1e5] = np.nan

        if self.path_swarp is not None:
            path_to_file = os.path.join(
                    self.path_swarp, '{}.fits'.format(self.filename_final))
            if self.verbose:
                print("saved '{}' in {}".format(self.filename_final, self.path_swarp))
        else:
            path_to_file = os.path.join(
                    self.path_images, '{}.fits'.format(self.filename_final))
            if self.verbose:
                print("saved '{}' in {}".format(self.filename_final, self.path_images))
        fits.writeto(path_to_file, data, header=header,
                     overwrite=self.overwrite)
