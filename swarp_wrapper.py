#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import numpy as np

from astropy.io import fits
from tqdm import tqdm

class Swarp(object):
    def __init__(self, listPathToCubes, settingsFile=None):
        self.listPathToCubes = listPathToCubes
        self.settingsFile = settingsFile

        self.maxChannels = None
        self.listOfChannels = []

        self.filenameFinal = None

        self.verbose = True
        self.overwrite = True
        self.removeTemporaryFiles = True

        self.pathSwarp = None

        self.listSlices = []
        self.listOfImages = None
        self.pathImages = None

    def slice_cubes(self):
        self.check_channels()

        start = True
        for pathToCube in self.listPathToCubes:
            self.dirname = os.path.dirname(pathToCube)
            self.file = os.path.basename(pathToCube)
            self.filename, self.fileExtension = os.path.splitext(self.file)

            if self.verbose:
                print("slicing cube {}...".format(self.filename))

            hdu = fits.open(pathToCube)[0]
            self.data = hdu.data
            self.header = hdu.header

            if len(self.data.shape) == 4:
                self.correct_stokes()

            self.maxChannels = self.check_channels()

            if start:
                start = False

                if self.pathSwarp is None:
                    self.pathSwarp = os.path.join(self.dirname, 'swarp_files')

                self.pathChannels = os.path.join(self.pathSwarp, 'channels')
                if not os.path.exists(self.pathChannels):
                    os.makedirs(self.pathChannels)

                self.pathSlices = os.path.join(self.pathSwarp, 'slices')
                if not os.path.exists(self.pathSlices):
                    os.makedirs(self.pathSlices)

                for channel in range(self.maxChannels):
                    self.listOfChannels.append(
                            'channel_{:04d}'.format(channel))

            for channel in range(self.maxChannels):
                if channel > (self.header['NAXIS3'] - 1):
                    "create 2D array with nan values here"
                    sliceData = np.empty(
                            (self.header['NAXIS2'], self.header['NAXIS1']))
                    sliceData[:] = np.NAN
                else:
                    sliceData = self.data[channel, :, :]
                sliceHeader = self.make_2d_header()

                suffix = 'channel_{:04d}'.format(channel)

                filename = '{}_{}.fits'.format(
                        self.filename, suffix)
                pathToFile = os.path.join(self.pathChannels, filename)

                fits.writeto(pathToFile, sliceData, header=sliceHeader,
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
        listChannels = []
        for pathToCube in self.listPathToCubes:
            hdu = fits.open(pathToCube)[0]
            header = hdu.header
            listChannels.append(header['NAXIS3'])
        return max(listChannels)

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

        pbar = tqdm(total=len(self.listOfChannels))
        for channel in self.listOfChannels:
            # if self.verbose:
            #     print("slice {}...".format(channel))
            pbar.update(1)
            nameListFiles = os.path.join(
                    self.pathChannels, '*{}*'.format(channel))
            filename = '{}.fits'.format(channel)
            self.listSlices.append(filename)
            cwd = os.getcwd()
            os.chdir(self.pathSlices)
            os.system('swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                    a=nameListFiles, b=self.settingsFile, c=filename))
            os.chdir(cwd)
            # if self.removeTemporaryFiles:
            #     os.system('rm {}'.format(nameListFiles))
        pbar.close()

    def assemble_cube(self):
        if self.verbose:
            print("assembling final cube...")
        os.chdir(self.pathSlices)

        start = True
        pbar = tqdm(total=len(self.listSlices))
        for idx, filename in enumerate(self.listSlices):
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

        if self.filenameFinal is None:
            self.filenameFinal = 'swarp_final'

        pathToFile = os.path.join(
                self.pathSwarp, '{}.fits').format(self.filenameFinal)
        fits.writeto(pathToFile, array, header=header,
                     overwrite=self.overwrite)

        os.chdir(self.pathSwarp)
        pathLogfile = os.path.join(self.pathSlices, 'swarp.xml')
        pathLogfileNew = os.path.join(self.pathSwarp, '{}.xml'.format(self.filenameFinal))
        os.system('mv {} {}'.format(pathLogfile, pathLogfileNew))

        if self.removeTemporaryFiles:
            os.system('rm -r {}'.format(self.pathSlices))
            os.system('rm -r {}'.format(self.pathChannels))
            # for filename in self.listSlices:
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
        os.chdir(self.pathImages)
        print(self.listOfImages)
        if isinstance(self.listOfImages, list):
            string = ''
            for img in self.listOfImages:
                string += img + ' '
            self.listOfImages = string
        filename = os.path.join(self.pathImages, '{}.fits'.format(self.filenameFinal))
        print(filename)
        os.system('swarp {a} -c {b} -IMAGEOUT_NAME {c} -VERBOSE_TYPE QUIET'.format(
                a=self.listOfImages, b=self.settingsFile, c=filename))

    def initialize_array(self, header):
        x = header['NAXIS1']
        y = header['NAXIS2']
        z = int(self.maxChannels)

        array = np.zeros([z, y, x], dtype=np.float32)

        return array

    def restore_nan_values(self):
        if self.verbose:
            print("restoring nan values...")
        if self.pathSwarp is not None:
            os.chdir(self.pathSwarp)
        else:
            os.chdir(self.pathImages)

        hdu = fits.open('{}.fits'.format(self.filenameFinal))[0]
        data = hdu.data
        header = hdu.header

        data[data < -1e5] = np.nan

        if self.pathSwarp is not None:
            pathToFile = os.path.join(
                    self.pathSwarp, '{}.fits'.format(self.filenameFinal))
            if self.verbose:
                print("saved '{}' in {}".format(self.filenameFinal, self.pathSwarp))
        else:
            pathToFile = os.path.join(
                    self.pathImages, '{}.fits'.format(self.filenameFinal))
            if self.verbose:
                print("saved '{}' in {}".format(self.filenameFinal, self.pathImages))
        fits.writeto(pathToFile, data, header=header,
                     overwrite=self.overwrite)
