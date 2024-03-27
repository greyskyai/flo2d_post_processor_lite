import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

def filter_model_data(model_data):
    """Filter model data for non-zero fpxsec values and return sorted unique fpxsec IDs."""
    fpxsec_grids = model_data[pd.notna(model_data['fpxsec'])]
    fpxsec_ids = fpxsec_grids['fpxsec'].drop_duplicates().sort_values()
    return fpxsec_ids

def create_linestring_from_data(df, fpxsec_id):
    """Create a LineString geometry from dataframe coordinates."""
    points = [Point(float(row['x']), float(row['y'])) for _, row in df.iterrows()]
    return LineString(points)

def create_geodataframe(fpxsec_ids, model_data, fpxsec_results):
    """Create a GeoDataFrame with LineStrings and corresponding attributes."""
    rows = []
    for fpxsec_id in fpxsec_ids:
        df = model_data[model_data['fpxsec'] == fpxsec_id]
        line = create_linestring_from_data(df, fpxsec_id)  # Pass fpxsec_id for debugging
        result_row = fpxsec_results.loc[fpxsec_results['fpxs_id'] == fpxsec_id].iloc[0]
        row = result_row.to_dict()
        row['geometry'] = line
        rows.append(row)

    gdf = gpd.GeoDataFrame(rows, columns=fpxsec_results.columns.tolist() + ['geometry'])
    return gdf


def save_geodataframe_to_shapefile(gdf, f_path, coord_system):
    """Save the GeoDataFrame to a shapefile."""
    shapefile_path = os.path.join(f_path, 'FLO2D_SHP', 'fpxsec.shp')
    os.makedirs(os.path.join(f_path, 'FLO2D_SHP'), exist_ok=True)
    gdf.to_file(shapefile_path, crs=f"EPSG:{coord_system}")
    return shapefile_path

def get_shapefile_associated_paths(shp_path):
    import os
    directory, shp_filename = os.path.split(shp_path)
    base_filename, _ = os.path.splitext(shp_filename)
    all_files = os.listdir(directory)
    associated_files = [os.path.join(directory, file)
                        for file in all_files if file.startswith(base_filename)]
    return associated_files


def create_fpxsec_shapefile(f_path, coord_system, model_data, fpxsec_results):
    """Main function to create a shapefile from model data and fpxsec results."""
    fpxsec_ids = filter_model_data(model_data)
    gdf = create_geodataframe(fpxsec_ids, model_data, fpxsec_results)

    gdf.crs = f"EPSG:{coord_system}"
    shp_path = save_geodataframe_to_shapefile(gdf, f_path, coord_system)
    shapefile = get_shapefile_associated_paths(shp_path)
    return shapefile
