import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import toml

# Fetch data
@st.cache_resource()
def fetch_data_survey():
    secret_info = st.secrets["sheets"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('Employee Survey 2024')
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    df_survey = pd.DataFrame(data)
    return df_survey

@st.cache_resource()
def fetch_data_creds():
    secret_info = st.secrets["sheets"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('Dashboard Credentials')
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    df_creds = pd.DataFrame(data)
    return df_creds

@st.cache_resource()
def fetch_data_sap():
    secret_info = st.secrets["sheets"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('Employee Not Done')
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    df_sap = pd.DataFrame(data)
    return df_sap
