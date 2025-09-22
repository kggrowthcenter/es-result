import streamlit as st
import pandas as pd
import numpy as np
from fetch_data import fetch_data_survey, fetch_data_creds, fetch_data_sap

#@st.cache_data()
def finalize_data():
    df_survey = fetch_data_survey()
    df_creds = fetch_data_creds()
    df_sap = fetch_data_sap()
   
    # Example: Drop rows where 'column_name' has the value 'value_to_drop'
    df_survey = df_survey[df_survey['unit'] != '#N/A']


    df_sap_selected = df_sap[['nik', 'unit', 'subunit', 'generation','gender', 'religion','tenure', 
                              'status','directorate','division',
                              'department','section', 'position','region','marital','children',	'education','participation_23', 'layer','subdivision']]

    # List penugasan
    update_list = {
        5382: {'unit': 'CORCOMM', 'subunit': 'CORCOMM'},
        28009: {'unit': 'GOMED', 'subunit': 'GRID'},
        1536: {'unit': 'GOMED', 'subunit': 'KONTAN'},
        5135: {'unit': 'GOMED', 'subunit': 'GOMED'},
        1416: {'unit': 'YMN', 'subunit': 'UNIVERSITAS'},
        4469: {'unit': 'YMN', 'subunit': 'UNIVERSITAS'},
        1375: {'unit': 'GOMED', 'subunit': 'HARKOM'},
        1376: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        2002: {'unit': 'GOMED', 'subunit': 'GOMED'},
        2751: {'unit': 'GOMED', 'subunit': 'GRID'},
        2975: {'unit': 'GOMAN', 'subunit': 'GOMAN'},
        3316: {'unit': 'GOMED', 'subunit': 'GOMED'},
        3392: {'unit': 'GOMED', 'subunit': 'GRID'},
        3412: {'unit': 'GOMED', 'subunit': 'GOMED'},
        4520: {'unit': 'GOMED', 'subunit': 'GOMED'},
        4521: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        4982: {'unit': 'GOMAN', 'subunit': 'GOMAN'},
        5035: {'unit': 'GOMED', 'subunit': 'GRID'},
        5584: {'unit': 'GOMED', 'subunit': 'GOMED'},
        5951: {'unit': 'GOMED', 'subunit': 'GOMED'},
        6097: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        6149: {'unit': 'GOMED', 'subunit': 'GOMED'},
        10239: {'unit': 'GOMED', 'subunit': 'GOMED'},
        12691: {'unit': 'GOMED', 'subunit': 'GOMED'},
        14956: {'unit': 'GOMED', 'subunit': 'GOMED'},
        16446: {'unit': 'GOMED', 'subunit': 'GOMED'},
        18196: {'unit': 'GOMED', 'subunit': 'GOMED'},
        19474: {'unit': 'GOMED', 'subunit': 'GOMED'},
        22264: {'unit': 'GOMED', 'subunit': 'KOMPAS TV'},
        23163: {'unit': 'GOMED', 'subunit': 'GOMED'},
        24377: {'unit': 'GOMED', 'subunit': 'KOMPAS TV'},
        28962: {'unit': 'GOMED', 'subunit': 'KOMPAS TV'},
        35202: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        35318: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        35439: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        35689: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        35859: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        35896: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        39763: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        42342: {'unit': 'GOMED', 'subunit': 'GOMED'},
        62757: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        26832: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        100013: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        26822: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        100027: {'unit': 'YMN', 'subunit': 'DIGITAL'},
        100001: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        81563: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        23945: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        27259: {'unit': 'GOMED', 'subunit': 'GOMED'},
        59284: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        61032: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        24870: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        76975: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        86635: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        27011: {'unit': 'GOMED', 'subunit': 'TRIBUN'},
        74900: {'unit': 'GOMED', 'subunit': 'GRID'},
        17261: {'unit': 'GOMED', 'subunit': 'GRID'},
        1551: {'unit': 'GOMED', 'subunit': 'GRID'},
        4042: {'unit': 'GOMED', 'subunit': 'GRID'},
        37520: {'unit': 'GOMED', 'subunit': 'GRID'},
        5874: {'unit': 'GOMED', 'subunit': 'GOMED'}
    }
    
    # Iterate over the update list and update the DataFrame
    for nik, values in update_list.items():
        df_survey.loc[df_survey['nik'] == nik, ['unit', 'subunit']] = [values['unit'], values['subunit']]

    # Replacing missing value
    df_survey['directorate'] = df_survey['directorate'].replace([0,'#N/A'],'-')
    df_survey['division'] = df_survey['division'].replace(['','#N/A'],'-')
    df_survey['department'] = df_survey['department'].replace(['','#N/A',0],'-')
    df_survey['section'] = df_survey['section'].replace(['','#N/A',0],'-')
    df_survey['layer'] = df_survey['layer'].replace(['#N/A','#VALUE!'],'-')
    df_survey['marital'] = df_survey['marital'].replace({'#N/A':'-', 'Cerai':'Duda/Janda', 'Lajang':'Belum Menikah', 'Nikah':'Sudah Menikah'})
    df_survey['education'] = df_survey['education'].replace({'#N/A':'-', 'D1':'Diploma', 'D2':'Diploma', 'D3':'Diploma', 'D4':'Diploma'})
    df_survey['children'] = df_survey['children'].replace('#N/A','-')
    df_survey['unit'] = df_survey['unit'].replace('GOMED','KG MEDIA')
    df_survey['subunit'] = df_survey['subunit'].replace({'GOMED':'KG MEDIA','SIRKULASI':'HARKOM'})
    df_sap_selected['directorate'] = df_sap_selected['directorate'].replace([0,'#N/A'],'-')
    df_sap_selected['division'] = df_sap_selected['division'].replace(['','#N/A'],'-')
    df_sap_selected['department'] = df_sap_selected['department'].replace(['','#N/A',0],'-')
    df_sap_selected['section'] = df_sap_selected['section'].replace(['','#N/A',0],'-')
    df_sap_selected['layer'] = df_sap_selected['layer'].replace(['#N/A','#VALUE!'],'-')
    df_sap_selected['marital'] = df_sap_selected['marital'].replace({'#N/A':'-', 'Cerai':'Duda/Janda', 'Lajang':'Belum Menikah', 'Nikah':'Sudah Menikah'})
    df_sap_selected['education'] = df_sap_selected['education'].replace({'#N/A':'-', 'D1':'Diploma', 'D2':'Diploma', 'D3':'Diploma', 'D4':'Diploma'})
    df_sap_selected['children'] = df_sap_selected['children'].replace('#N/A','-')
    df_sap_selected['status'] = df_sap_selected['status'].replace('','-')
    df_sap_selected['participation_23'] = df_sap_selected['participation_23'].replace('#N/A','NO')
    df_sap_selected['unit'] = df_sap_selected['unit'].replace('GOMED','KG MEDIA')
    df_sap_selected['subunit'] = df_sap_selected['subunit'].replace({'GOMED':'KG MEDIA','SIRKULASI':'HARKOM'})

    # Categorizing tenure
    # Convert the 'tenure' column to numeric, replacing errors with NaN
    #df_survey['tenure'] = pd.to_numeric(df_survey['tenure'], errors='coerce')

    bins = [0, 1, 3, 6, 10, 15, 20, 25, float('inf')]
    labels = ['<1', '1-3', '3-6', '6-10', '10-15', '15-20', '20-25', '>25']

    # Apply categorization
    df_survey['tenure_category'] = pd.cut(df_survey['tenure'], bins=bins, labels=labels, right=False)
    df_sap_selected['tenure_category'] = pd.cut(df_sap_selected['tenure'], bins=bins, labels=labels, right=False)

    # Replace '#N/A' and 0 with NaN, and fill NaN in KE0 with the average of KE1, KE2, KE3
    df_survey['KE0'] = pd.to_numeric(df_survey['KE0'], errors='coerce').replace(0, np.nan)
    df_survey['KE0'] = df_survey['KE0'].fillna(df_survey[['KE1', 'KE2', 'KE3']].mean(axis=1).round(0).astype(int))


    # Calculate the average for each dimension and round to 1 decimal place
    df_survey['average_kd'] = df_survey[['KD1', 'KD2', 'KD3', 'KD0']].mean(axis=1).round(2)
    df_survey['average_ki'] = df_survey[['KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KI0']].mean(axis=1).round(2)
    df_survey['average_kr'] = df_survey[['KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'KR0']].mean(axis=1).round(2)
    df_survey['average_pr'] = df_survey[['PR1', 'PR2', 'PR0']].mean(axis=1).round(2)
    df_survey['average_tu'] = df_survey[['TU1', 'TU2', 'TU0']].mean(axis=1).round(2)
    df_survey['average_ke'] = df_survey[['KE1', 'KE2', 'KE3', 'KE0']].mean(axis=1).round(2)

    # Mapping untuk layer
    layer_mapping = {
        'Group 5 Str Layer 1': 'Director',
        'Group 5': 'Professional setara Director (Consultant)',
        'Group 4 Str Layer 2': 'General Manager',
        'Group 4': 'Professional setara GM (Advisor)',
        'Group 3 Str Layer 3B': 'Senior Manager',
        'Group 3 Str Layer 3A': 'Manager',
        'Group 3': 'Professional setara Manager (Specialist)',
        'Group 2 Str Layer 4': 'Superintendent',
        'Group 2': 'Officer',
        'Group 1 Str Layer 5': 'Team Leader',
        'Group 1': 'Pelaksana',
        '-' :'-'
    }

    df_survey['layer'] = df_survey['layer'].map(layer_mapping)
    df_sap_selected['layer'] = df_sap_selected['layer'].map(layer_mapping)

    # Calculate overall satisfaction by averaging all items directly and round to 1 decimal place
    #df_survey['overall_satisfaction'] = df_survey[['KD1', 'KD2', 'KD3', 'KD0', 
    #                                                    'KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KI0',
    #                                                    'KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'KR0',
    #                                                    'PR1', 'PR2', 'PR0',
    #                                                    'TU1', 'TU2', 'TU0',
    #                                                    'KE1', 'KE2', 'KE3', 'KE0']].mean(axis=1).round(1)

    #with st.expander('df_survey'):
    #    st.dataframe(df_survey.sample(50))

    #columns_list = [
    #    'unit', 'subunit', 'directorate', 'division', 'department', 'section',
    #    'layer', 'status', 'generation', 'gender', 'marital', 'education',
    #    'tenure_category', 'children', 'region', 'participation_23'
    #]

    #st.write("Unique values for each column in columns_list:")
    #for column in columns_list:
    #    if column in df_survey.columns:
    #        unique_values = df_survey[column].unique()
    #        with st.expander(f"{column.capitalize()}"):
    #            st.write(unique_values)
    #    else:
    #        with st.expander(f"{column.capitalize()}"):
    #            st.write("Column not available in the data.")
    combined_df = pd.concat([df_survey, df_sap_selected], ignore_index=True)
    return df_survey, df_creds, combined_df

