import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import os

# Assuming the extract_hystruc function and extractModelDataToDF function are defined elsewhere
# and imported here.

def create_hystruc_shapefile(hystruc_df, model_data_df, coord_system, output_path):
    # Merge the hystruc dataframe with the model data dataframe to get x, y coordinates for inflow and outflow nodes
    # This assumes the model_data_df has 'grid_id', 'x', 'y' columns
    merged_df = pd.merge(hystruc_df, model_data_df[['grid_id', 'x', 'y']], left_on='Inflow Node', right_on='grid_id', how='left')
    merged_df.rename(columns={'x': 'inflow_x', 'y': 'inflow_y'}, inplace=True)
    merged_df = pd.merge(merged_df, model_data_df[['grid_id', 'x', 'y']], left_on='Outflow Node', right_on='grid_id', how='left', suffixes=('', '_outflow'))
    merged_df.rename(columns={'x': 'outflow_x', 'y': 'outflow_y'}, inplace=True)

    # Create a GeoDataFrame with a LineString from inflow to outflow for each structure
    gdf = gpd.GeoDataFrame(merged_df, geometry=[LineString([[row['inflow_x'], row['inflow_y']], [row['outflow_x'], row['outflow_y']]]) for index, row in merged_df.iterrows()], crs=f"EPSG:{coord_system}")

    # Export the GeoDataFrame to a shapefile
    output_filename = os.path.join(output_path, 'hystruc_lines.shp')
    gdf.to_file(output_filename)