The following code imports the `swarp_wrapper` class and initializes it:

```python
import swarp_wrapper.swarp_wrapper as sw
swarp = sw.Swarp()
```

The `swarp_wrapper` object has two main methods. Use

```python
swarp.mosaic_cubes()
```
to mosaic FITS data cubes, such as Position-Position-Velocity (PPV) data cubes. To mosaic FITS images (2D arrays) instead use

```python
swarp.mosaic_images()
```

In the following we list and discuss settings for the `swarp_wrapper`, which have to be set before running these methods.

```python
swarp.path_swarp = None
```

Specify a path to a directory in which the temporary files produced by `swarp_wrapper` can be saved. These files will be deleted if `remove_temporary_files` is set to `True`.

```python
swarp.list_cubes = None
```

List of filepaths to FITS cubes that should be mosaicked with the `mosaic_cubes` method.

```python
swarp.list_images = None
```
List of filepaths to FITS images that should be mosaicked with the `mosaic_images` method.

```python
swarp.swarp_configuration_file = None
```
Specify path to the SWarp configuration file. To produce a default configuration files type

```bash
SWarp -d
```

in the terminal. Use

```bash
SWarp -dd
```

to produce a default extended configuration file.

```python
swarp.filename_final = None
```

Specify the filename of the final mosaicked FITS file.

```python
swarp.verbose = True
```

Set the `verbose` parameter to `False` if you don't want status messages to be printed to the terminal.

```python
swarp.overwrite = True
```

By default already existing data files named `filename_final` are overwritten.

```python
swarp.remove_temporary_files = True
```

If the `remove_temporary_files` parameter is set to `False`, all temporary files produced by the `swarp_wrapper` will be saved (by default these files are removed after the final FITS cube or image is assembled).

```python
swarp.save_weighted_coaddition_map = True
```

By default the weighted coaddition map produced by SWarp is saved in the same directory as the final assembled FITS data cube or image.

```python
swarp.save_swarp_log = True
```

By default the log file produced by SWarp is saved in the same directory as the final assembled FITS data cube or image.

```python
swarp.restore_nans = True
```

If `restore_nans` is set to `True` all data points containing NaNs in the original FITS files will be set to NaN again.

```python
swarp.restore_keys = True
```

If `restore_keys` is set to `True` the FITS header key from the original FITS files will be restored in the FITS header of the final assembled mosaic.

```python
swarp.convert_zeros_to_nans = True
```

If `convert_zeros_to_nans` is set to `True` all data points containing zero values in the original FITS files will be set to NaN in the assembled mosaic.

```python
swarp.list_of_keys_to_remove = True
```

List of FITS header keywords to remove from the FITS header of the final assembled mosaic.
