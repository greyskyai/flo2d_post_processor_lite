# vectorization.py

import geopandas as gpd
from modules.utilities import time_function

@time_function
def convert_gdf_to_shapefile(geo_df, output_path, coord_system, columns=None):
    """
    Convert a GeoDataFrame to a shapefile. Optionally select specific columns.
    :param geo_df: GeoDataFrame to be converted.
    :param output_path: Output file path for the shapefile.
    :param columns: Optional list of columns to include. If None, all columns are included.
    """
    if columns is not None:
        geo_df = geo_df[columns + ['geometry']]
        geo_df = geodf.crs(f"EPSG: {coord_system}")
    flo2d_data = geo_df.to_file(output_path, driver='ESRI Shapefile')

    return flo2d_data

# Additional vector-related functions can be added here in the future.
