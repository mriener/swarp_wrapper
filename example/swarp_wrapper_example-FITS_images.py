import os

import swarp_wrapper.swarp_wrapper as sw


dirpath = 'path/to/FITS_image_files'

list_cubes = []

#  the following assumes that we have nine FITS images named
#  data-image-*.fits that we want to mosaic
for i in range(1, 10):
    filename = 'data-image-{}.fits'.format(i)
    list_cubes.append(os.path.join(dirpath, filename))

swarp = sw.Swarp()
swarp.path_swarp = dirpath
#  the configuration file needs to be produced individually for each mosaic
#  type 'SWarp -d' in the terminal to produce a default configuration file
swarp.swarp_configuration_file = 'config.swarp'
swarp.list_images = list_cubes
swarp.filename_final = 'data-image-mosaicked.fits'
swarp.mosaic_images()
