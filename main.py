import os
import pandas as pd
from modules.data_extraction import extractModelDataToDF
from modules.hycross_extraction import extract_fpxsec_results
from modules.geospatial import convertToGeoDataFrame, calculate_cell_size
from modules.rasterization import create_raster_from_gdf
from modules.vectorization import convert_gdf_to_shapefile
from modules.fpxsec_vectorization import create_fpxsec_shapefile
from modules.utilities import create_required_folders
from modules.hystruc_vectorization import create_hystruc_shapefile
from modules.hystruc_extraction import extract_hystruc_results
from modules.fpxsec_spreadsheet import hycross_spreadsheet


# Define file paths
file_path = r"C:\Users\Anichols\OneDrive - Atwell LLC\Desktop\ironwood"
coord_system = 2223
raster_outpath = os.path.join(file_path, 'flo2d_rasters')
shp_outpath = os.path.join(file_path, 'flo2d_shp')
folders = [raster_outpath, shp_outpath]

# Create required directories
create_required_folders(folders)

# Extract data from files and create DataFrame
model_data = extractModelDataToDF(file_path)
fpxsec_grids = model_data[pd.notna(model_data['fpxsec'])]

# Convert DataFrame to GeoDataFrame
geo_df = convertToGeoDataFrame(model_data)

# Save GeoDataFrame to shapefile
#flo2d_data_shp = os.path.join(shp_outpath, 'flo2d_data.shp')
#convert_gdf_to_shapefile(geo_df, flo2d_data_shp, coord_system)

# Extract floodplain cross section results from HYCROSS.OUT
fpxsec_results = extract_fpxsec_results(file_path)

# Save floodplain cross section results to shapefile
create_fpxsec_shapefile(file_path, coord_system, model_data, fpxsec_results)

# Create HYCROSS.OUT spreadsheet
hycross_spreadsheet(file_path)

# Save hydraulic structure results to shapefile
hystruc_df = extract_hystruc_results(file_path)
create_hystruc_shapefile(hystruc_df, model_data, coord_system, shp_outpath)

# Calculate cell size for raster creation
cell_size = calculate_cell_size(geo_df)

# Create rasters for each specified column
columns = ['depth_max', 'xksat', 'psif', 'dtheta',
           'abstrinf', 'rtimpf', 'soil_depth', 'velocity',
             'q_max', 'wse_max', 'infil_depth', 'infil_stop',
               'time_of_oneft', 'time_of_twoft', 'time_to_peak', 'mannings_n',
                 'topo', 'final_velocity', 'final_depth',
              ]
for column in columns:
    raster_file = os.path.join(raster_outpath, f'{column}.tif')
    create_raster_from_gdf(geo_df, column, raster_file, cell_size)

print("Processing completed successfully.")