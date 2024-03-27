import os
import pandas as pd

def extract_hystruc_results(file_path):

    hystruc_file_path = os.path.join(file_path, 'HYSTRUC.DAT')
    hydrostruct_file_path = os.path.join(file_path, 'HYDROSTRUCT.OUT')

    # Extract data from HYSTRUC.DAT file
    with open(hystruc_file_path, 'r') as file:
        lines = file.readlines()

    structures = {}

    for line in lines:
        line = line.strip().split()

        if line[0] == 'S':
            structure_name = line[1]
            if structure_name not in structures:
                structures[structure_name] = {
                    'Structure Name': structure_name,
                    'IFPROCHAN': int(line[2]),
                    'ICURVETABLE': int(line[3]),
                    'Inflow Node': int(line[4]),
                    'Outflow Node': int(line[5]),
                    'INOUTCONT': int(line[6]),
                    'HEADREFEL': float(line[7]),
                    'CLENGTH': float(line[8]),
                    'CDIAMETER': float(line[9]),
                    'TYPEC': None,
                    'TYPEEN': None,
                    'CULVERTN': None,
                    'KE': None,
                    'CUBASE': None
                }

        elif line[0] == 'F' and structure_name in structures:
            structures[structure_name].update({
                'TYPEC': int(line[1]),
                'TYPEEN': int(line[2]),
                'CULVERTN': float(line[3]),
                'KE': float(line[4]),
                'CUBASE': float(line[5])
            })

    # Extract peak discharge and time of peak discharge from HYDROSTRUCT.OUT file
    with open(hydrostruct_file_path, 'r') as file:
        for line in file:
            if 'THE MAXIMUM DISCHARGE FOR:' in line:
                parts = line.split()
                # Assuming structure name is always the fifth element after this specific phrase
                structure_index = parts.index('FOR:') + 1
                structure_name = parts[structure_index]
                # Find index for "IS:" to get the peak discharge and time of peak as next elements
                is_index = parts.index('IS:')
                peak_discharge = float(parts[is_index + 1])
                at_time_index = parts.index('AT', is_index)  # Finding 'AT' after 'IS:'
                time_of_peak = float(parts[at_time_index + 2])
                
                # If the structure name is in the structures dictionary, update it
                if structure_name in structures:
                    structures[structure_name].update({
                        'Qpeak_cfs': peak_discharge,
                        'Tpeak_hrs': time_of_peak
                    })

    # Convert the structures dictionary to a DataFrame
    df = pd.DataFrame(list(structures.values()))
    return df