
# Python wrapper for SWarp (swarp_wrapper)

## About
The ``swarp_wrapper`` is a Python wrapper for [SWarp](http://www.astromatic.net/software/swarp), a program that resamples and co-adds together FITS images using any arbitrary astrometric projection defined in the [WCS standard](https://fits.gsfc.nasa.gov/fits_wcs.html).

The aim of the ``swarp_wrapper`` is to provide easy-to-use Python scripts for combining FITS data cubes and FITS images.

All credit for SWarp and its original Fortran implementation is due to [Bertin et al. 2002](https://ui.adsabs.harvard.edu/abs/2002ASPC..281..228B/abstract) and should be acknowledged as such.

For tips on how to get started with the ``swarp_wrapper`` see the section [Getting started](#gettingstarted) further below. See also the official [SWarp documentation](https://www.astromatic.net/pubsvn/software/swarp/trunk/doc/swarp.pdf) for more details on the settings for astrometric projections.

### Version

The currently recommended version of the ``swarp_wrapper`` is v0.1. See the [swarp_wrapper Changelog](CHANGES.md) for an overview of the major changes and improvements introduced by newer versions currently in development.

New updates to the code are first tested and developed in the ``dev`` branch. Users cloning the ``dev`` branch should beware that these versions are not guaranteed to be stable.

## Installation

### Dependencies

To use ``swarp_wrapper`` you must have a working installation of SWarp on your operating system. You can find the necessary installation files for SWarp [here](https://github.com/astromatic/swarp). Moreover, you will need the following packages to run the ``swarp_wrapper``. We list the version of each package which we know to be compatible with the ``swarp_wrapper``.

* [python 3.5](https://www.python.org/)
* [astropy (v3.0.4)](http://www.astropy.org/)
* [numpy (v1.14.2)](http://www.numpy.org/)
* [tqdm (v4.19.4)](https://tqdm.github.io/)

If you do not already have Python 3.5, you can install the [Anaconda Scientific Python distribution](https://store.continuum.io/cshop/anaconda/), which comes pre-loaded with numpy.

### Download the swarp_wrapper

Download the swarp_wrapper using git `$ git clone https://github.com/mriener/swarp_wrapper.git`


### Installing Dependencies on Linux

Install pip for easy installation of python packages:

```bash
sudo apt-get install python-pip
```

Then install the required python packages:

```bash
sudo pip install astropy numpy tqdm
```

### Installing Dependencies on OSX

Install pip for easy installation of python packages:

```bash
sudo easy_install pip
```

Then install the required python packages:

```bash
sudo pip install astropy numpy tqdm
```

<a id="gettingstarted"></a>
## Getting started

The [SETTINGS.md](SETTINGS.md) file gives an overview about settings for the ``swarp_wrapper``.

The `example` directory contains two example scripts on how to mosaic FITS data cubes and FITS image files.

## Feedback

If you should find that the ``swarp_wrapper`` does not perform as intended for your dataset or if you should come across bugs or have suggestions for improvement, please get into contact with us or open a new Issue or Pull request.

## Contributing to GaussPy+

To contribute to the ``swarp_wrapper``, see [Contributing to the swarp_wrapper](CONTRIBUTING.md)
