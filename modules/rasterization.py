# rasterization.py

import numpy as np
import rasterio
from rasterio.transform import from_origin
from modules.utilities import time_function

@time_function
def create_raster_from_gdf(geo_df, column, raster_file, cell_size):
    x_coords = geo_df.geometry.x.to_numpy()
    y_coords = geo_df.geometry.y.to_numpy()
    values = geo_df[column].to_numpy()

    xmin, ymin, xmax, ymax = geo_df.total_bounds
    xmin -= cell_size / 2
    xmax += cell_size / 2
    ymin -= cell_size / 2
    ymax += cell_size / 2
    nrows = int(np.ceil((ymax - ymin) / cell_size))
    ncols = int(np.ceil((xmax - xmin) / cell_size))

    transform = from_origin(xmin, ymax, cell_size, cell_size)
    raster = np.full((nrows, ncols), np.nan)

    for x, y, value in zip(x_coords, y_coords, values):
        col_idx = int(np.floor((x - xmin - cell_size / 2) / cell_size))
        row_idx = int(np.floor((ymax - y - cell_size / 2) / cell_size))
        if 0 <= row_idx < nrows and 0 <= col_idx < ncols:
            raster[row_idx, col_idx] = value

    with rasterio.open(
        raster_file, 'w',
        driver='GTiff',
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=raster.dtype,
        crs=geo_df.crs,
        transform=transform,
    ) as dst:
        dst.write(raster, 1)
    return raster_file