import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from navigation import make_sidebar, make_filter
from data_processing import finalize_data

# ==============================
# Page & Sidebar
# ==============================
st.set_page_config(page_title='Gallup Engagement', page_icon=':bar_chart:')
make_sidebar()

# ==============================
# Load & Authenticate
# ==============================
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

if not st.session_state.get('authentication_status'):
    st.warning("You are not authenticated — please log in to view this page.")
    st.stop()

username = st.session_state['username']
user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')

df_survey23 = df_survey23[df_survey23['subunit'].isin(user_units)]
df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]
df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]

# ==============================
# Header
# ==============================
st.header("🟣 Gallup Engagement Index", divider="rainbow")

# Define Gallup items
gallup_items = [
    "KD1", "KD2", "KI1", "KI2", "KI4", "KI5",
    "KR2", "KR3", "KR4", "KR5", "PR1", "PR2"
]

filter_columns = [
    'unit', 'subunit', 'directorate', 'site', 'division', 'department',
    'section', 'layer', 'work_contract', 'generation', 'gender',
    'tenure_category', 'region'
]

# ==============================
# Filter Section
# ==============================
combined = pd.concat([df_survey23, df_survey24, df_survey25], ignore_index=True)
selected_filters = make_filter(filter_columns, combined, key_prefix="gallup_filter")

def apply_selected_filters(df, selected_filters):
    if not selected_filters:
        return df
    for col, values in selected_filters.items():
        if values and col in df.columns:
            df = df[df[col].isin(values)]
    return df

df23 = apply_selected_filters(df_survey23, selected_filters)
df24 = apply_selected_filters(df_survey24, selected_filters)
df25 = apply_selected_filters(df_survey25, selected_filters)

# ==============================
# Year Selector
# ==============================
selected_year = st.radio(
    "Select Year:",
    options=[2023, 2024, 2025],
    horizontal=True,
    index=2
)
df_selected = {2023: df23, 2024: df24, 2025: df25}[selected_year].copy()

# ==============================
# Compute Gallup Engagement Category
# ==============================
existing_cols = [c for c in gallup_items if c in df_selected.columns]
if not existing_cols:
    st.error("No Gallup items found in the dataset.")
    st.stop()

df_selected['Gallup_Avg'] = df_selected[existing_cols].mean(axis=1, skipna=True)

def categorize_gallup(score):
    if pd.isna(score):
        return np.nan
    if score <= 2.75:
        return "Actively Disengaged"
    elif score <= 4.24:
        return "Not Engaged"
    else:
        return "Actively Engaged"

df_selected['Engagement Category'] = df_selected['Gallup_Avg'].apply(categorize_gallup)

if df_selected.shape[0] <= 1:
    st.warning("⚠️ Data unavailable to protect confidentiality (N ≤ 1).")
    st.stop()

# ==============================
# Year-Specific Gallup Benchmarks
# ==============================
gallup_benchmark_data = {
    2023: {
        "Global":  {"Actively Disengaged": 18, "Not Engaged": 59, "Actively Engaged": 23},
        "SEA":     {"Actively Disengaged": 6, "Not Engaged": 68, "Actively Engaged": 26}
    },
    2024: {
        "Global":  {"Actively Disengaged": 15, "Not Engaged": 62, "Actively Engaged": 23},
        "SEA":     {"Actively Disengaged": 8, "Not Engaged": 67, "Actively Engaged": 26}
    },
    2025: {
        "Global":  {"Actively Disengaged": 17, "Not Engaged": 62, "Actively Engaged": 21},
        "SEA":     {"Actively Disengaged": 8, "Not Engaged": 67, "Actively Engaged": 26}
    },
}

# ==============================
# Construct Benchmark Table
# ==============================
benchmarks = pd.DataFrame([
    {
        "Group": f"Global Gallup {selected_year}",
        **gallup_benchmark_data[selected_year]["Global"]
    },
    {
        "Group": f"Southeast Asia {selected_year}",
        **gallup_benchmark_data[selected_year]["SEA"]
    },
    {
        "Group": "KG",
        "Actively Disengaged": np.nan,
        "Not Engaged": np.nan,
        "Actively Engaged": np.nan
    }
])

# --- KG (whole company) distribution ---
df_all_raw = {2023: df_survey23, 2024: df_survey24, 2025: df_survey25}[selected_year].copy()
df_all_raw['Gallup_Avg'] = df_all_raw[existing_cols].mean(axis=1, skipna=True)
df_all_raw['Engagement Category'] = df_all_raw['Gallup_Avg'].apply(categorize_gallup)
kg_dist = (
    df_all_raw['Engagement Category']
    .value_counts(normalize=True)
    .reindex(["Actively Disengaged", "Not Engaged", "Actively Engaged"], fill_value=0)
    * 100
)
benchmarks.loc[
    benchmarks['Group'] == "KG",
    ["Actively Disengaged", "Not Engaged", "Actively Engaged"]
] = kg_dist.values

# ==============================
# Helper function to compute % table
# ==============================
def compute_percentage(df, group_col):
    """Return % distribution by Engagement Category for a group variable."""
    if not group_col or group_col not in df.columns:
        return pd.DataFrame()
    group_counts = (
        df.groupby([group_col, "Engagement Category"])
        .size()
        .unstack(fill_value=0)
    )
    group_perc = group_counts.div(group_counts.sum(axis=1), axis=0) * 100
    group_perc = group_perc.reindex(columns=["Actively Disengaged", "Not Engaged", "Actively Engaged"], fill_value=0)
    group_perc.reset_index(inplace=True)
    group_perc.rename(columns={group_col: "Group"}, inplace=True)
    return group_perc

# ==============================
# SECTION 1 — Overall Comparison
# ==============================
st.subheader("🌍 Overall Comparison", divider="gray")

rows_section1 = [
    benchmarks.loc[benchmarks['Group'] == f"Global Gallup {selected_year}"],
    benchmarks.loc[benchmarks['Group'] == f"Southeast Asia {selected_year}"],
    benchmarks.loc[benchmarks['Group'] == "KG"],
]

# Add Unit-level breakdown if available
if "unit" in df_selected.columns:
    unit_perc = compute_percentage(df_selected, "unit")
    if not unit_perc.empty:
        rows_section1.append(unit_perc)

comparison_df1 = pd.concat(rows_section1, ignore_index=True)

melted1 = comparison_df1.melt(
    id_vars=["Group"],
    value_vars=["Actively Disengaged", "Not Engaged", "Actively Engaged"],
    var_name="Engagement Category",
    value_name="Percent"
)

order1 = [f"Global Gallup {selected_year}", f"Southeast Asia {selected_year}", "KG"]
if "unit" in df_selected.columns:
    order1 += sorted(df_selected["unit"].dropna().unique().tolist())
melted1["Group"] = pd.Categorical(melted1["Group"], categories=order1, ordered=True)

fig1 = px.bar(
    melted1,
    x="Group",
    y="Percent",
    color="Engagement Category",
    text=melted1["Percent"].round(0).astype(int).astype(str) + "%",
    color_discrete_map={
        "Actively Disengaged": "#e74c3c",
        "Not Engaged": "#f1c40f",
        "Actively Engaged": "#2ecc71"
    },
)
fig1.update_layout(
    barmode="stack",
    yaxis=dict(title="%", range=[0, 100]),
    xaxis_title=None,
    legend_title=None,
    height=550,
    title=""
)
fig1.update_traces(textposition="inside", insidetextanchor="middle")
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# SECTION 2 — Detailed Breakdown
# ==============================
breakdown_var = st.selectbox(
    "🔍 Breakdown by (choose variable):",
    options=[None] + filter_columns,
    index=filter_columns.index("subunit") + 1 if "subunit" in filter_columns else 0
)
st.subheader("🏢 Detailed Breakdown", divider="gray")

if breakdown_var and breakdown_var in df_selected.columns:
    section2 = compute_percentage(df_selected, breakdown_var)
    if section2.empty:
        st.info("No data available for this breakdown.")
    else:
        melted2 = section2.melt(
            id_vars=["Group"],
            value_vars=["Actively Disengaged", "Not Engaged", "Actively Engaged"],
            var_name="Engagement Category",
            value_name="Percent"
        )
        order2 = sorted(df_selected[breakdown_var].dropna().unique().tolist())
        melted2["Group"] = pd.Categorical(melted2["Group"], categories=order2, ordered=True)

        fig2 = px.bar(
            melted2,
            x="Group",
            y="Percent",
            color="Engagement Category",
            text=melted2["Percent"].round(0).astype(int).astype(str) + "%",
            color_discrete_map={
                "Actively Disengaged": "#e74c3c",
                "Not Engaged": "#f1c40f",
                "Actively Engaged": "#2ecc71"
            },
        )
        fig2.update_layout(
            barmode="stack",
            yaxis=dict(title="%", range=[0, 100]),
            xaxis_title=None,
            legend_title=None,
            height=550,
            title=""
        )
        fig2.update_traces(textposition="inside", insidetextanchor="middle")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Select a breakdown variable above to show the detailed section.")
