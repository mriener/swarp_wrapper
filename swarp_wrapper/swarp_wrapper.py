#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import numpy as np

from astropy.io import fits
from pprint import pprint
from tqdm import tqdm

from .fits_header_functions import remove_additional_axes, change_header, restore_header_keys, transform_header_from_crota_to_pc


class Swarp(object):
    def __init__(self):
        self.path_swarp = None
        self.list_cubes = None
        self.list_images = None
        self.swarp_configuration_file = None
        self.filename_final = None

        self.max_channels = None

        self.verbose = True
        self.overwrite = True
        self.remove_temporary_files = True
        self.save_weighted_coaddition_map = True
        self.save_swarp_log = True
        self.restore_nans = True
        self.restore_keys = True
        self.convert_zeros_to_nans = False
        self.list_of_keys_to_remove = []

    def say(self, message):
        """Diagnostic messages."""
        if self.verbose:
            print(message)

    def check_settings(self):
        if self.path_swarp is None:
            raise Exception("Need to specify 'path_swarp'")
        if not os.path.exists(self.path_swarp):
            os.makedirs(self.path_swarp)
        if self.swarp_configuration_file is None:
            raise Exception("Need to specify 'swarp_configuration_file', i.e. the path to the SWarp configuration file.")
        if (self.list_cubes is None) and (self.list_images is None):
            raise Exception("Need to supply either 'list_cubes' (= list of paths to spectral cubes) or 'list_images' (list of paths to images)")
        if self.filename_final is not None:
            if self.filename_final.endswith('.fits'):
                self.filename_final = self.filename_final[:-5]

        self.restore_cdelt_keys = False

    def clean_up(self):
        if self.list_cubes is not None:
            path_log_file = os.path.join(self.path_slices, 'swarp.xml')
            path_weighted_coadditon_map = os.path.join(
                self.path_slices, 'coadd.weight.fits')
        elif self.list_images is not None:
            path_log_file = os.path.join(self.path_swarp, 'swarp.xml')
            path_weighted_coadditon_map = os.path.join(
                self.path_swarp, 'coadd.weight.fits')

        if self.save_swarp_log:
            path_log_file_new = os.path.join(
                self.path_swarp, '{}.xml'.format(self.filename_final))
            os.system('mv {} {}'.format(path_log_file, path_log_file_new))
        else:
            os.system('rm {}'.format(path_log_file))

        if self.save_weighted_coaddition_map:
            path_weighted_coadditon_map_new = os.path.join(
                self.path_swarp, '{}.coadd.weight.fits'.format(
                    self.filename_final))
            os.system('mv {} {}'.format(path_weighted_coadditon_map,
                                        path_weighted_coadditon_map_new))
        else:
            os.system('rm {}'.format(path_weighted_coadditon_map))

    def initialize_cube_mosaicking(self):
        if self.list_cubes is None:
            raise Exception("Need to supply either 'list_cubes' (= list of paths to spectral cubes)")

        self.path_channels = os.path.join(self.path_swarp, 'channels')
        if not os.path.exists(self.path_channels):
            os.makedirs(self.path_channels)

        self.path_slices = os.path.join(self.path_swarp, 'slices')
        if not os.path.exists(self.path_slices):
            os.makedirs(self.path_slices)

        self.list_of_channels = []
        for channel in range(self.max_channels):
            self.list_of_channels.append('channel_{:04d}'.format(channel))

    def mosaic_cubes(self):
        self.check_settings()
        self.max_channels = self.check_channels()
        self.initialize_cube_mosaicking()
        self.slice_cubes()
        self.swarp_slices()
        self.assemble_cube()
        self.clean_up()

        if self.remove_temporary_files:
            os.system('rm -r {}'.format(self.path_slices))
            os.system('rm -r {}'.format(self.path_channels))

        self.restore_values()

    def mosaic_images(self):
        self.check_settings()
        self.assemble_image()
        self.clean_up()
        self.restore_values()

    def slice_cubes(self):
        total = len(self.list_cubes)
        for i, path_to_cube in enumerate(self.list_cubes):
            self.dirname = os.path.dirname(path_to_cube)
            self.file = os.path.basename(path_to_cube)
            self.filename, self.file_extension = os.path.splitext(self.file)

            end = '\r'
            if i + 1 == total:
                end = '\n'
            if self.verbose:
                print("slicing cube {}...".format(self.filename), end=end)

            data = fits.getdata(path_to_cube)
            header = fits.getheader(path_to_cube)

            if len(data.shape) == 4:
                data, header = remove_additional_axes(
                    data, header)

            if i == 0:
                self.header = header.copy()

            for channel in range(self.max_channels):
                if channel > (header['NAXIS3'] - 1):
                    # create 2D array with nan values
                    slice_data = np.empty(
                            (header['NAXIS2'], header['NAXIS1']))
                    slice_data[:] = np.NAN
                else:
                    slice_data = data[channel, :, :]
                slice_header = change_header(header.copy())

                suffix = 'channel_{:04d}'.format(channel)

                filename = '{}_{}.fits'.format(
                        self.filename, suffix)
                path_to_file = os.path.join(self.path_channels, filename)

                fits.writeto(path_to_file, slice_data, header=slice_header,
                             overwrite=self.overwrite)

    def check_channels(self):
        list_channels = []
        for path_to_cube in self.list_cubes:
            header = fits.getheader(path_to_cube)
            list_channels.append(header['NAXIS3'])
        return max(list_channels)

    def swarp_slices(self):
        self.say("swarp slices...")

        self.list_slices = []

        pbar = tqdm(total=len(self.list_of_channels))
        for channel in self.list_of_channels:
            pbar.update(1)
            nameListFiles = os.path.join(
                    self.path_channels, '*{}*'.format(channel))
            filename = '{}.fits'.format(channel)
            self.list_slices.append(filename)
            cwd = os.getcwd()
            os.chdir(self.path_slices)
            os.system('swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                    a=nameListFiles, b=self.swarp_configuration_file, c=filename))
            os.chdir(cwd)
        pbar.close()

    def assemble_cube(self):
        self.say("assembling final cube...")
        os.chdir(self.path_slices)

        start = True
        pbar = tqdm(total=len(self.list_slices))
        for idx, filename in enumerate(self.list_slices):
            pbar.update(1)
            data = fits.getdata(filename)
            header = fits.getheader(filename)
            if start:
                start = False
                header = restore_header_keys(
                    header, self.header, remove_keys=self.list_of_keys_to_remove)
                array = self.initialize_array(header)

            array[idx, :, :] = data
        pbar.close()

        if self.filename_final is None:
            self.filename_final = 'swarp_final'

        os.chdir(self.path_swarp)

        path_to_file = os.path.join(
                self.path_swarp, '{}.fits').format(self.filename_final)
        fits.writeto(path_to_file, array, header=header,
                     overwrite=self.overwrite)

    def assemble_image(self):
        self.say("list of {} input images:".format(len(self.list_images)))
        if self.verbose:
            pprint(self.list_images)
        self.say("assembling final image...")

        self.header = fits.getheader(self.list_images[0])

        os.chdir(self.path_swarp)
        if isinstance(self.list_images, list):
            string = ''
            for img in self.list_images:
                string += img + ' '
            self.list_images = string
        filename = os.path.join(
            self.path_swarp, '{}.fits'.format(self.filename_final))

        os.system(
            'swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                a=self.list_images, b=self.swarp_configuration_file, c=filename))

    def initialize_array(self, header):
        x = header['NAXIS1']
        y = header['NAXIS2']
        z = int(self.max_channels)

        array = np.zeros([z, y, x], dtype=np.float32)

        return array

    def restore_values(self):
        os.chdir(self.path_swarp)

        data = fits.getdata(self.filename_final + '.fits')
        header = fits.getheader(self.filename_final + '.fits')

        if self.restore_nans:
            self.say("restoring NaN values...")
            data[data < -1e5] = np.nan

        if self.convert_zeros_to_nans:
            self.say("converting zero values to NaNs...")
            data[data == 0] = np.nan

        if self.restore_keys:
            self.say("restoring FITS header keys...")
            header = restore_header_keys(
                header, self.header, remove_keys=self.list_of_keys_to_remove)

        header = transform_header_from_crota_to_pc(header)

        path_to_file = os.path.join(
                self.path_swarp, '{}.fits'.format(self.filename_final))
        self.say("saved '{}' in {}".format(
            self.filename_final, self.path_swarp))

        fits.writeto(path_to_file, data, header=header,
                     overwrite=self.overwrite)
