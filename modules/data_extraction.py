# data_extraction.py

import pandas as pd
import os
from modules.utilities import time_function

@time_function
def extractModelDataToDF(file_path):
    """
    Extracts model data from various files and compiles it into a DataFrame.
    :param file_path: Path to the directory containing the model data files.
    :return: A DataFrame containing the compiled model data.
    """
    # Read DEPTH.OUT file and create DataFrame
    data_df = pd.read_csv(os.path.join(file_path, 'DEPTH.OUT'), sep=r'\s+', header=None, names=['grid_id', 'x', 'y', 'depth_max'])

    # Read INFIL.DAT file and add to DataFrame
    with open(os.path.join(file_path, 'INFIL.DAT'), 'r') as file:
        first_line = file.readline().strip()
        if first_line == '1':
            infil_method = 'Green and Ampt'
            infil_df = pd.read_csv(os.path.join(file_path, 'INFIL.DAT'), sep=r'\s+', header=None, names=['xksat', 'psif', 'dtheta', 'abstrinf', 'rtimpf', 'soil_depth'], usecols=[2, 3, 4, 5, 6, 7], skiprows=3)
            data_df['xksat'] = infil_df['xksat']
            data_df['psif'] = infil_df['psif']
            data_df['dtheta'] = infil_df['dtheta']
            data_df['abstrinf'] = infil_df['abstrinf']
            data_df['rtimpf'] = infil_df['rtimpf']
            data_df['soil_depth'] = infil_df['soil_depth']
        elif first_line == '2':
            infil_method = 'SCS Curve Number'
        elif first_line == '3':
            infil_method = 'SCS Curve Number and Green and Ampt'
        elif first_line == '4':
            infil_method = 'Horton'
        else:
            infil_method = 'None'

    # Read MANNINGS_N.DAT and add to DataFrame
    mannings_n_df = pd.read_csv(os.path.join(file_path, 'MANNINGS_N.DAT'), sep=r'\s+', header=None, names=['mannings_n'], usecols=[1])
    data_df['mannings_n'] = mannings_n_df['mannings_n']

    # Read TOPO.DAT and add to DataFrame
    topo_df = pd.read_csv(os.path.join(file_path, 'TOPO.DAT'), sep=r'\s+', header=None, names=['topo'], usecols=[2])
    data_df['topo'] = topo_df['topo']

    # Read VELFP.OUT and add to DataFrame
    velfp_df = pd.read_csv(os.path.join(file_path, 'VELFP.OUT'), sep=r'\s+', header=None, usecols=[3], names=['velocity'])
    data_df['velocity'] = velfp_df['velocity']

    # Read MAXQHYD.OUT and filter valid rows
    maxqhyd_df = pd.read_csv(os.path.join(file_path, 'MAXQHYD.OUT'), sep=r'\s+', header=None, skiprows=4)
    maxqhyd_df = maxqhyd_df[maxqhyd_df[0] >= 1]
    data_df['q_max'] = maxqhyd_df[7]
    data_df['flow_dir'] = maxqhyd_df[8]

    # Read MAXWSELEV.OUT and add to DataFrame
    maxwselev_df = pd.read_csv(os.path.join(file_path, 'MAXWSELEV.OUT'), sep=r'\s+', header=None, usecols=[3], names=['wse_max'])
    data_df['wse_max'] = maxwselev_df['wse_max']

    # Read INFIL_DEPTH.OUT and add to DataFrame
    infil_depth_df = pd.read_csv(os.path.join(file_path, 'INFIL_DEPTH.OUT'), sep=r'\s+', header=None, names=['infil_depth', 'infil_stop'], usecols=[4, 5], skiprows=1)
    data_df['infil_depth'] = infil_depth_df['infil_depth']
    data_df['infil_stop'] = infil_depth_df['infil_stop']

    # Read TIMEONEFT.OUT and add to DataFrame
    timeoneft_df = pd.read_csv(os.path.join(file_path, 'TIMEONEFT.OUT'), sep=r'\s+', header=None, names=['time_of_oneft'], usecols=[3])
    data_df['time_of_oneft'] = timeoneft_df['time_of_oneft']

    # Read TIMETWOFT.OUT and add to DataFrame
    timetwoft_df = pd.read_csv(os.path.join(file_path, 'TIMETWOFT.OUT'), sep=r'\s+', header=None, names=['time_of_twoft'], usecols=[3])
    data_df['time_of_twoft'] = timetwoft_df['time_of_twoft']

    # Read TIMETOPEAK.OUT and add to DataFrame
    timetopeak_df = pd.read_csv(os.path.join(file_path, 'TIMETOPEAK.OUT'), sep=r'\s+', header=None, names=['time_to_peak'], usecols=[3])
    data_df['time_to_peak'] = timetopeak_df['time_to_peak']

    # Read FINALVEL.OUT and add to DataFrame
    finalvel_df = pd.read_csv(os.path.join(file_path, 'FINALVEL.OUT'), sep=r'\s+', header=None, names=['final_velocity'], usecols=[3])
    data_df['final_velocity'] = finalvel_df['final_velocity']

    # Read FINALDEP.OUT and add to DataFrame
    finaldep_df = pd.read_csv(os.path.join(file_path, 'FINALDEP.OUT'), sep=r'\s+', header=None, names=['final_depth'], usecols=[3])
    data_df['final_depth'] = finaldep_df['final_depth']

    # Read FPXSEC.DAT line by line and update DataFrame
    with open(os.path.join(file_path, 'FPXSEC.DAT'), 'r') as file:
        line_number = 0
        for line in file:
            parts = line.split()
            if parts and parts[0] == 'X':
                line_number += 1
                grid_ids = [int(grid) - 1 for grid in parts[3:] if grid.isdigit()]
                for grid_id in grid_ids:
                    if grid_id >= len(data_df):
                        data_df = data_df.append(pd.Series(), ignore_index=True)
                    data_df.at[grid_id, 'fpxsec'] = line_number

    return data_df
