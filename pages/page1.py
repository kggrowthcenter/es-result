from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
import altair as alt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='Demography',
    page_icon='🌎',
)

make_sidebar()
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

# ==============================
# FILTER CONFIG
# ==============================
columns_list = [
    'unit', 'subunit', 'directorate', 'division', 'site', 'department', 'section',
    'layer', 'status', 'generation', 'gender', 
    'tenure_category', 'region', 'year'
]

# ==============================
# CATEGORY FUNCTION
# ==============================
def categorize(value):
    if value >= 5:
        return 'High'
    elif value <= 2:
        return 'Low'
    else:
        return None

# ==============================
# FILTER FUNCTION
# ==============================
def make_filter(columns_list, df_survey, combined_df):
    filter_columns = st.multiselect(
        'Filter the data (optional):',
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    selected_filters = {}
    filtered_data, filtered_combined = df_survey.copy(), combined_df.copy()

    for filter_col in filter_columns:
        selected_filter_value = st.multiselect(
            f'Select {filter_col.capitalize()} to filter the data:',
            options=filtered_data[filter_col].dropna().unique(),
            key=f'filter_{filter_col}'
        )
        
        if selected_filter_value:
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_filter_value)]
            filtered_combined = filtered_combined[filtered_combined[filter_col].isin(selected_filter_value)]
            selected_filters[filter_col] = selected_filter_value

    if filtered_data.shape[0] <= 1 or filtered_combined.shape[0] <= 1:
        st.write("Data is unavailable to protect confidentiality.")
        return pd.DataFrame(), pd.DataFrame(), {}

    return filtered_data, filtered_combined, selected_filters


# ==============================
# MAIN SECTION
# ==============================
if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')

    # Filter each dataset based on user access
    df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]
    df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]
    df_survey23 = df_survey23[df_survey23['subunit'].isin(user_units)]

    # Add year column
    df_survey25['year'] = 2025
    df_survey24['year'] = 2024
    df_survey23['year'] = 2023

    # Combine all years
    combined_df = pd.concat([df_survey23, df_survey24, df_survey25], ignore_index=True)

    # Add satisfaction categories
    for d in [df_survey23, df_survey24, df_survey25]:
        d['category_sat'] = d['SAT'].apply(categorize)

    st.header('Demography Overview', divider='rainbow')

    # ==============================
    # SATISFACTION FILTER
    # ==============================
    high_satisfaction = st.checkbox("Profil Karyawan Puas (Skor 5)")
    low_satisfaction = st.checkbox("Profil Karyawan Tidak Puas (Skor 1 dan 2)")

    if high_satisfaction:
        combined_df = combined_df[combined_df['category_sat'] == 'High']
        st.subheader('High Satisfaction Demography')
    elif low_satisfaction:
        combined_df = combined_df[combined_df['category_sat'] == 'Low']
        st.subheader('Low Satisfaction Demography')
    else:
        st.subheader('All Demography')

    # ==============================
    # FILTER SECTION
    # ==============================
    filtered_data, filtered_combined, selected_filters = make_filter(columns_list, combined_df, combined_df)

    def apply_selected_filters(df, selected_filters):
        if not selected_filters:
            return df.copy()
        filtered = df.copy()
        for col, values in selected_filters.items():
            if not values:
                continue
            if col in filtered.columns:
                filtered = filtered[filtered[col].isin(values)]
        return filtered

    # Apply filters to each year
    df_survey23_filtered = apply_selected_filters(df_survey23, selected_filters)
    df_survey24_filtered = apply_selected_filters(df_survey24, selected_filters)
    df_survey25_filtered = apply_selected_filters(df_survey25, selected_filters)

    #st.write("Selected filters:", selected_filters)
    #st.write("Combined filtered rows:", len(filtered_combined))


    # ==============================
    # 📊 METRICS SECTION
    # ==============================
    st.markdown("#### 📈 Metrics Overview by Year")

    def calc_participants(df, year_label):
        if df.empty:
            return {'year': year_label, 'participants': 0, 'total': 0, 'percentage': 0}
        df = df.copy()
        total = df['nik'].nunique()
        participants = df.loc[df['submit_date'].notna() & (df['submit_date'] != ""), 'nik'].nunique()
        percentage = (participants / total * 100) if total > 0 else 0
        return {'year': year_label, 'participants': participants, 'total': total, 'percentage': round(percentage, 1)}

    yearly_data = []
    for year, df in [("2023", df_survey23_filtered), ("2024", df_survey24_filtered), ("2025", df_survey25_filtered)]:
        yearly_data.append(calc_participants(df, year))

    df_yearly = pd.DataFrame(yearly_data)

    # --- 100% stacked bar chart ---
    st.markdown("###### 🧩 Participation Rate Comparison")
    colors = {
        "Participants": "#1A2B4C",
        "Non-participants": "#EAD8C0"
    }

    fig = go.Figure()
    for label, color in zip(["Participants", "Non-participants"], ["#1A2B4C", "#EAD8C0"]):
        if label == "Participants":
            y_values = df_yearly['percentage']
        else:
            y_values = 100 - df_yearly['percentage']
        fig.add_trace(go.Bar(
            x=df_yearly['year'],
            y=y_values,
            name=label,
            text=[f"{v:.1f}%" for v in y_values],
            textposition='inside',
            marker_color=colors[label]
        ))

    fig.update_layout(
        barmode='stack',
        yaxis=dict(title="Percentage", range=[0, 100]),
        xaxis=dict(title="Year"),
        legend=dict(orientation="h", y=-0.2),
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==============================
    # 🎯 DYNAMIC METRIC BY FILTER
    # ==============================
    st.markdown("#### 🎛️ Participation by Selected Attribute")

    column_list = [
        'unit', 'subunit', 'directorate', 'division', 'site', 'department', 'section',
        'layer', 'status', 'generation', 'gender',
        'tenure_category', 'region'
    ]

    unit_column = st.selectbox("Select the demography by:", column_list)

    # Gabungkan semua tahun
    combined_years = pd.concat([
        df_survey23_filtered.assign(year="2023"),
        df_survey24_filtered.assign(year="2024"),
        df_survey25_filtered.assign(year="2025")
    ], ignore_index=True)

    if unit_column in combined_years.columns:
        df_filtered = combined_years.copy()

        # Hitung peserta dan total unik per unit per tahun
        grouped = (
            df_filtered.groupby(['year', unit_column])
            .agg(
                total_participant=('nik', 'nunique'),
                participant=('submit_date', lambda x: x.notna().sum())
            )
            .reset_index()
        )

        # Hitung persentase
        grouped['percentage'] = grouped['participant'] / grouped['total_participant'] * 100

        # Pivot agar tiap tahun jadi kolom
        pivot_df = grouped.pivot(index=unit_column, columns='year', values='participant').fillna(0)

        # Normalisasi ke 100% (tiap unit total = 100)
        pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
        pivot_df = pivot_df.reset_index()

        # Untuk label jumlah peserta
        participant_counts = grouped.pivot(index=unit_column, columns='year', values='participant').fillna(0)
        participant_counts = participant_counts.reset_index()

        # Plot horizontal stacked bar
        fig2 = px.bar(
            pivot_df,
            y=unit_column,
            x=['2023', '2024', '2025'],
            barmode='stack',
            orientation='h',
            title=f'Participation Distribution by {unit_column.capitalize()}',
            color_discrete_map={
                '2023': 'lightsteelblue',  
                '2024': 'antiquewhite',  
                '2025': 'midnightblue' 
            }
        )

        # Tambahkan label xxx%(n)
        for trace, year in zip(fig2.data, ['2023', '2024', '2025']):
            trace.customdata = participant_counts[year]
            trace.texttemplate = '%{x:.1f}% (%{customdata})'
            trace.textposition = 'inside'

        fig2.update_layout(
            xaxis=dict(title="Percentage (%)", range=[0, 100]),
            yaxis=dict(title=unit_column.capitalize(), categoryorder='total ascending'),
            height=700,
            template="plotly_white",
            legend_title_text="Year",
            bargap=0.2
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning(f"Column '{unit_column}' not found in data.")

