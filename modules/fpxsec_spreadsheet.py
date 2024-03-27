import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import re

def extract_hydrograph_data_corrected(file_path):
    """
    Extracts hydrograph data (time and discharge) from the specified file, integrating the maximum discharge
    at its correct time position.
    """
    hydrograph_data = {}
    max_discharge_info = {}  # Store max discharge info for each section
    current_section = None  # Initialize the current_section variable

    with open(file_path, 'r') as file:
        for line in file:
            # Check for the line with maximum discharge information
            if 'THE MAXIMUM DISCHARGE FROM CROSS SECTION' in line:
                match = re.search(r'THE MAXIMUM DISCHARGE FROM CROSS SECTION\s*(\d+) IS:\s*([\d.]+) CFS AT TIME:\s*([\d.]+)', line)
                if match:
                    section = int(match.group(1))
                    max_discharge = float(match.group(2))
                    max_time = float(match.group(3))
                    max_discharge_info[section] = (max_time, max_discharge)
                continue

            # Check for the start of a hydrograph section
            if 'HYDROGRAPH AND FLOODPLAIN HYDRAULICS' in line:
                match = re.search(r'FOR CROSS SECTION NO:\s*(\d+)', line)
                if match:
                    current_section = int(match.group(1))
                    hydrograph_data[current_section] = []
                continue

            # Detect the start of the data (after the column headers)
            if 'TIME' in line and 'DISCHARGE' in line:
                continue  # Skip the header line

            # Extract data if in a data section
            if current_section is not None:
                try:
                    parts = line.split()
                    time = float(parts[0])
                    discharge = float(parts[5])
                    hydrograph_data[current_section].append((time, discharge))
                except (IndexError, ValueError):
                    # Handle lines that do not contain valid data
                    continue

    # Convert lists to pandas DataFrames and integrate max discharge
    for section in hydrograph_data:
        df = pd.DataFrame(hydrograph_data[section], columns=['Time', 'Discharge'])
        if section in max_discharge_info:
            df = integrate_max_discharge_in_df(df, max_discharge_info[section])
        hydrograph_data[section] = df

    return hydrograph_data

def integrate_max_discharge_in_df(hydrograph_data, max_discharge_info):
    """
    Integrates the maximum discharge information into the DataFrame at its correct time position.
    """
    max_time, max_discharge = max_discharge_info

    # Check if the max time already exists in the DataFrame
    if max_time in hydrograph_data['Time'].values:
        hydrograph_data.loc[hydrograph_data['Time'] == max_time, 'Discharge'] = max_discharge
    else:
        # Insert a new row for the maximum discharge
        new_row = pd.DataFrame({'Time': [max_time], 'Discharge': [max_discharge]})
        hydrograph_data = pd.concat([hydrograph_data, new_row], ignore_index=True)
        hydrograph_data = hydrograph_data.sort_values(by='Time').reset_index(drop=True)

    return hydrograph_data

def plot_hydrograph(data, section, plot_file_path):
    """
    Creates a hydrograph plot for a given section.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(data['Time'], data['Discharge'], label='Discharge')
    max_discharge = data['Discharge'].max()
    max_time = data[data['Discharge'] == max_discharge]['Time'].iloc[0]
    plt.title(f'Hydrograph for Section {section}')
    plt.xlabel('Time (hours)')
    plt.ylabel('Discharge (cfs)')
    plt.grid(True)
    plt.annotate(f'Max Discharge: {max_discharge} cfs at {max_time} hrs',
                 xy=(max_time, max_discharge), xytext=(max_time, max_discharge + 0.05 * max_discharge),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 ha='center')
    plt.savefig(plot_file_path)
    plt.close()

def export_hydrographs_to_excel_small_plots(hydrograph_data, folder_path, file_path):
    """
    Exports hydrograph data to an Excel file with separate sheets for each cross section's data and plots.
    """
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Export each cross section's data to a different sheet
        for section, data in hydrograph_data.items():
            # Export data
            data_sheet_name = f"Section {section} Data"
            data.to_excel(writer, sheet_name=data_sheet_name, index=False)

            # Create and save plot
            plot_file_name = f"section_{section}_plot.png"
            plot_file_path = os.path.join(folder_path, plot_file_name)
            plot_hydrograph(data, section, plot_file_path)

            # Add plot to the Excel file on a new sheet with reduced size
            plot_sheet_name = f"Section {section} Plot"
            workbook = writer.book
            plot_sheet = workbook.create_sheet(plot_sheet_name)
            img = Image(plot_file_path)

            # Reduce the size of the image to 1/4
            img.width, img.height = img.width / 2, img.height / 2
            plot_sheet.add_image(img, 'A1')

def hycross_spreadsheet(folder_path):
    file_path = os.path.join(folder_path, 'HYCROSS.OUT')  # Replace with your input file path
    output_excel_path = os.path.join(folder_path, 'fpxsec_hydrographs.xlsx')  # Replace with your output file path

    # Extracting hydrograph data
    extracted_data = extract_hydrograph_data_corrected(file_path)

    # Exporting to Excel
    export_hydrographs_to_excel_small_plots(extracted_data, folder_path, output_excel_path)
