import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from data_processing import finalize_data
from navigation import make_sidebar, make_filter

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title='IPA', page_icon='📕')
make_sidebar()

# ==============================
# LOAD DATA
# ==============================
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()
df_all = {"2025": df_survey25, "2024": df_survey24, "2023": df_survey23}

st.header('Importance–Performance Analysis (IPA)', divider='rainbow')

# ==============================
# SELECT YEAR
# ==============================
selected_year = st.selectbox("Pilih tahun survei:", options=list(df_all.keys()), index=0)
df = df_all[selected_year].copy()
df = df[df['submit_date'].notna() & (df['submit_date'] != "")]

# ==============================
# USER ACCESS FILTER
# ==============================
if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    df = df[df['subunit'].isin(user_units)]

# ==============================
# FILTER TAMBAHAN
# ==============================
columns_list = [
    'unit', 'subunit', 'directorate', 'division', 'department', 'section',
    'layer', 'status', 'generation', 'gender', 'marital', 'education',
    'tenure_category', 'children', 'region', 'participation_23'
]

selected_filters = make_filter(columns_list, df, key_prefix="ipa_filter")

for col, values in selected_filters.items():
    if values:
        df = df[df[col].isin(values)]

st.write(f"Jumlah data setelah filter: {df.shape[0]} responden")

# ==============================
# DEFINISI VARIABEL
# ==============================
independent_vars = [
    'KD1', 'KD2', 'KD3', 'KI1', 'KI2', 'KI3', 'KI4', 'KI5',
    'KR1', 'KR2', 'KR3', 'KR4', 'KR5',
    'PR1', 'PR2', 'TU1', 'TU2',
    'KE1', 'KE2', 'KE3'
]

df = df.dropna(subset=['SAT'] + independent_vars)
if df.empty:
    st.warning("Tidak ada data yang memenuhi filter saat ini.")
    st.stop()



# ==============================
# ANALISIS IMPORTANCE - PERFORMANCE (disamakan dengan coworker)
# ==============================
performance_mean = df['SAT'].mean()
importance_mean = df[independent_vars].mean()

# Standardisasi dan regresi
scaler = StandardScaler()
X = scaler.fit_transform(df[independent_vars])
y = scaler.fit_transform(df[['SAT']]).flatten()

model = LinearRegression()
model.fit(X, y)

# Using the Standardized Beta (St B) coefficients for Importance (not absolute values)
importance_values = model.coef_  # Standardized beta coefficients as importance

# Construct the correlation_df DataFrame with Standardized Beta (St B) values
correlation_df = pd.DataFrame({
    'Factor': independent_vars,
    'Importance': [round(beta, 3) for beta in importance_values],  # Directly using St B as importance
    'Performance': [round(beta, 3) for beta in importance_mean.values]
})

# Midpoint thresholds for dynamic quadrants
importance_min, importance_max = correlation_df['Importance'].min(), correlation_df['Importance'].max()
performance_min, performance_max = correlation_df['Performance'].min(), correlation_df['Performance'].max()

importance_midpoint = (importance_max + importance_min) / 2
performance_midpoint = (performance_max + performance_min) / 2


# ==============================
# KATEGORI QUADRANT (sama 1:1)
# ==============================
def classify_factor_dynamic(importance, performance, imp_mid, perf_mid):
    if importance > imp_mid and performance > perf_mid:
        return 'Leverage'
    elif importance > imp_mid and performance <= perf_mid:
        return 'Improve'
    elif importance <= imp_mid and performance > perf_mid:
        return 'Nice to have'
    else:
        return 'Low priority'

correlation_df['Category'] = [
    classify_factor_dynamic(row['Importance'], row['Performance'], importance_midpoint, performance_midpoint)
    for _, row in correlation_df.iterrows()
]

# ==============================
# SCATTER PLOT
# ==============================
st.subheader(f"GRAFIK IPA {selected_year}")

fig, ax = plt.subplots(figsize=(10, 6))

# Warna per kategori (sama seperti coworker)
color_map = {
    'Leverage': '#2ca02c',
    'Improve': '#d62728',
    'Nice to have': '#1f77b4',
    'Low priority': '#ff7f0e'
}

for category, data in correlation_df.groupby('Category'):
    ax.scatter(data['Performance'], data['Importance'], 
               label=category, color=color_map.get(category, 'gray'), s=100, alpha=0.8)

# Label faktor
for i, row in correlation_df.iterrows():
    ax.text(row['Performance'] + 0.01, row['Importance'], row['Factor'], fontsize=9, ha='left', va='bottom')

# Garis tengah
ax.axhline(y=importance_midpoint, color='green', linestyle='--', label="Importance Midpoint")
ax.axvline(x=performance_midpoint, color='red', linestyle='--', label="Performance Midpoint")

# Label dan style
ax.set_xlabel('Performance (Mean of SAT)', fontsize=12, labelpad=10)
ax.set_ylabel('Importance (Standardized Beta)', fontsize=12, labelpad=10)
ax.set_title('Importance–Performance Analysis', fontsize=16, pad=20)
ax.grid(True, linestyle='--', alpha=0.5)
#ax.legend(loc='lower right', bbox_to_anchor=(1, 0), fontsize=10, markerscale=1.5)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))



plt.tight_layout()
st.pyplot(fig)

# ==============================
# TABEL HASIL IPA
# ==============================
st.markdown(f"##### Tabel hasil IPA {selected_year}")
st.dataframe(correlation_df, use_container_width=True)
