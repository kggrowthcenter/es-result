from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
from scipy import stats
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title='Satisfaction', page_icon=':👍:')
make_sidebar()

# Load data
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

# -----------------------
# Configuration / mappings
# -----------------------
satisfaction_columns = [
    'SAT', 'average_kd', 'average_ki', 'average_kr',
    'average_pr', 'average_tu', 'average_ke'
]

satisfaction_columns_item = [
    'KD0', 'KD1', 'KD2', 'KD3', 'KE0', 'KE1', 'KE2', 'KE3',
    'KI0', 'KI1', 'KI2', 'KI3', 'KI4', 'KI5',
    'KR0', 'KR1', 'KR2', 'KR3', 'KR4', 'KR5',
    'PR0', 'PR1', 'PR2',
    'TU0', 'TU1', 'TU2', 'TU3'
]

satisfaction_mapping = {
    'SAT': 'Overall Satisfaction',
    'average_kd': 'Kebutuhan Dasar',
    'average_ki': 'Kontribusi Individu',
    'average_kr': 'Kerjasama',
    'average_pr': 'Pertumbuhan',
    'average_tu': 'Tujuan',
    'average_ke': 'Keterlekatan'
}

satisfaction_mapping_item = {k: k for k in satisfaction_columns_item}

columns_list = [
    'unit', 'subunit', 'directorate', 'site', 'division',  'department', 'section',
    'layer', 'work_contract', 'generation', 'gender', 'tenure_category', 'region'
]

prefix_mapping = {
    "SAT": "Overall Satisfaction",
    "KD": "Kebutuhan Dasar",
    "KI": "Kontribusi Individu",
    "KR": "Kerjasama",
    "PR": "Pertumbuhan",
    "TU": "Tujuan",
    "KE": "Keterlekatan"
}

score_labels = {
    "1": "Sangat Tidak Setuju",
    "2": "Tidak Setuju",
    "3": "Netral",
    "4": "Setuju",
    "5": "Sangat Setuju"
}

# -----------------------
# Utility: highlight function (reused)
# -----------------------
def highlight_progress(val):
    """Return background color style for progress cells."""
    if pd.isna(val):
        return ''
    try:
        v = float(val)
    except Exception:
        return ''
    if v > 0:
        return 'background-color: #d4edda; color: #155724;'  # light green
    elif v < 0:
        return 'background-color: #f8d7da; color: #721c24;'  # light red
    else:
        return 'background-color: #e2e3e5; color: #383d41;'  # grey for zero

# -----------------------
# Authorization / scoping by user
# -----------------------
if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]
    df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]
    df_survey23 = df_survey23[df_survey23['subunit'].isin(user_units)]

    st.header('Satisfaction Score', divider='rainbow')

    # Item-level toggle
    item_level_analysis = st.checkbox("Check to analyze at item level", value=False)

    # Choose columns based on toggle
    if item_level_analysis:
        data = {
            "Code": [
                "KD", "KD0", "KD1", "KD2", "KD3", "KE", "KE0", "KE1", "KE2", "KE3", "KI", "KI0", 
                "KI1", "KI2", "KI3", "KI4", "KI5", "KR", "KR0", "KR1", "KR2", "KR3", "KR4", 
                "KR5", "PR", "PR0", "PR1", "PR2", "TU", "TU0", "TU1", "TU2", "TU3"
            ],
            "Description": [
                "Kebutuhan Dasar",
                "Saya merasa perusahaan ini sudah memenuhi segala kebutuhan kerja dasar yang saya miliki.",
                "Saya memahami secara jelas bagaimana ekspektasi kerja yang diharapkan kepada saya (Ekspektasi mengacu kepada, namun tidak terbatas pada KPI).",
                "Saya meyakini perusahaan ini akan memenuhi segala kebutuhan kerja untuk mendukung saya mencapai performa terbaik.",
                "Saya merasa perusahaan ini berkomitmen memfasilitasi kesejahteraan kehidupan saya.",
                "Keterlekatan",
                "Saya memiliki keterlekatan mendalam dengan perusahaan ini sebagai tempat bekerja saya.",
                "Saya bisa melihat diri saya tetap bekerja di perusahaan ini sekitar setahun ke depan.",
                "Saya terdorong untuk bekerja sebaik mungkin demi menjaga keberlangsungan perusahaan ini.",
                "Saya merasa bangga dengan perusahaan ini.",
                "Kontribusi Individu",
                "Saya merasa perusahaan ini sudah sangat baik dalam memfasilitasi kebutuhan saya untuk berkontribusi dalam ranah pekerjaan.",
                "Saya selalu diberikan kesempatan-kesempatan dalam pekerjaan yang memungkinkan saya menunjukkan kemampuan terbaik saya.",
                "Saya merasa ada orang-orang di perusahaan ini yang mengakui dan memuji bahwa pekerjaan saya bernilai.",
                "Saya didorong oleh orang-orang di perusahaan ini untuk memiliki otonomi dalam membuat keputusan-keputusan di pekerjaan saya.",
                "Saya merasa ada orang-orang di perusahaan ini yang menghargai saya selayaknya manusia.",
                "Saya merasa ada orang-orang di perusahaan ini yang mendorong saya untuk berkembang.",
                "Kerjasama",
                "Saya merasa bisa bekerjasama dengan sangat baik bersama orang-orang di perusahaan ini.",
                "Saya merasa orang-orang di perusahaan ini memperlakukan saya secara adil, terlepas apapun perbedaan yang ada dalam diri saya.",
                "Saya merasa pendapat apapun yang saya berikan pasti akan diperhitungkan oleh orang-orang di perusahaan ini.",
                "Saya melihat pekerjaan saya berharga karena akan menjadi energi yang mendorong perusahaan ini mencapai visi dan misinya.",
                "Saya melihat rekan-rekan kerja saya memiliki komitmen yang tinggi dalam menuntaskan pekerjaan dengan kualitas yang baik.",
                "Saya memiliki sahabat baik di perusahaan ini.",
                "Pertumbuhan",
                "Saya merasa perusahaan ini adalah tempat bertumbuh saya yang paling ideal.",
                "Saya mendapatkan bimbingan dari orang-orang di perusahaan ini terkait dengan proses pertumbuhan saya.",
                "Saya diberikan bekal dan kesempatan untuk bisa memajukan karir dan pertumbuhan saya di perusahaan ini.",
                "Tujuan",
                "Saya menemukan tujuan hidup saya di dalam perusahaan ini.",
                "Saya merasa tujuan baik 'Mencerahkan kehidupan bangsa' selaras dengan tujuan hidup saya sendiri.",
                "Saya memiliki keterikatan emosi dengan tujuan 'Mencerahkan kehidupan bangsa'.",
                "Saya merasa nilai-nilai perusahaan diterapkan dalam aktivitas pekerjaan sehari-hari di unit kerja saya."
            ]
        }
        
        # Create a DataFrame for the table
        df_description = pd.DataFrame(data)

        # Reset the index and drop it to hide it
        df_description = df_description.reset_index(drop=True)

        # Convert DataFrame to HTML without index
        table_html = df_description.to_html(escape=False, index=False)

        # Specify the rows to be bolded (for example, rows with Code 'KD0' and 'SAT')
        bold_rows = df_description[df_description['Code'].isin(['KD', 'KE', 'KI', 'KR', 'PR', 'TU'])].index

        # Apply bold styling to specific rows
        for row in bold_rows:
            table_html = table_html.replace(
                f'<tr><td>{df_description.iloc[row]["Code"]}</td>',
                f'<tr><td style="font-weight: bold;">{df_description.iloc[row]["Code"]}</td>'
            )
            table_html = table_html.replace(
                f'<td>{df_description.iloc[row]["Description"]}</td>',
                f'<td style="font-weight: bold;">{df_description.iloc[row]["Description"]}</td>'
            )

        # Display the styled table using st.markdown with unsafe_allow_html=True
        st.markdown(table_html, unsafe_allow_html=True)

        satisfaction_cols = satisfaction_columns_item
        satisfaction_map = satisfaction_mapping_item
    else:
        satisfaction_cols = satisfaction_columns
        satisfaction_map = satisfaction_mapping

    # Filters
    combined_for_filters = pd.concat([df_survey23, df_survey24, df_survey25], ignore_index=True)
    selected_filters = make_filter(columns_list, combined_for_filters, key_prefix="filter")

    def apply_selected_filters(df, selected_filters):
        if not selected_filters:
            return df.copy()
        filtered = df.copy()
        for col, values in selected_filters.items():
            if values and col in filtered.columns:
                filtered = filtered[filtered[col].isin(values)]
        return filtered

    df_survey23_filtered = apply_selected_filters(df_survey23, selected_filters)
    df_survey24_filtered = apply_selected_filters(df_survey24, selected_filters)
    df_survey25_filtered = apply_selected_filters(df_survey25, selected_filters)

    # --- CONFIDENTIALITY CHECK ---
    def confidentiality_guard(df):
        if df.shape[0] <= 1 and len(selected_filters) > 0:
            st.warning("⚠️ Data is unavailable to protect confidentiality (N ≤ 1).")
            return pd.DataFrame()
        return df

    df_survey23_filtered = confidentiality_guard(df_survey23_filtered)
    df_survey24_filtered = confidentiality_guard(df_survey24_filtered)
    df_survey25_filtered = confidentiality_guard(df_survey25_filtered)

    # Ensure numeric
    for col in satisfaction_cols:
        for df in [df_survey23_filtered, df_survey24_filtered, df_survey25_filtered]:
            if col not in df.columns:
                df[col] = pd.NA
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # -----------------------
    # Year Comparison Table
    # -----------------------
    df_avg_23 = df_survey23_filtered[satisfaction_cols].mean().round(2).reset_index()
    df_avg_23.columns = ['Dimension/Item', 'Average 2023']
    df_avg_24 = df_survey24_filtered[satisfaction_cols].mean().round(2).reset_index()
    df_avg_24.columns = ['Dimension/Item', 'Average 2024']
    df_avg_25 = df_survey25_filtered[satisfaction_cols].mean().round(2).reset_index()
    df_avg_25.columns = ['Dimension/Item', 'Average 2025']

    df_comparison = pd.merge(df_avg_23, df_avg_24, on="Dimension/Item", how="outer")
    df_comparison = pd.merge(df_comparison, df_avg_25, on="Dimension/Item", how="outer")

    df_comparison['Dimension/Item'] = df_comparison['Dimension/Item'].map(satisfaction_map).fillna(df_comparison['Dimension/Item'])
    
    df_comparison['Progress 2024'] = df_comparison['Average 2024'] - df_comparison['Average 2023']
    df_comparison['Progress 2025'] = df_comparison['Average 2025'] - df_comparison['Average 2024']

    # Count only SAT column responses
    n_23 = df_survey23_filtered['SAT'].count()
    n_24 = df_survey24_filtered['SAT'].count()
    n_25 = df_survey25_filtered['SAT'].count()
    
    n_row = pd.DataFrame({
        'Dimension/Item': ['N'],
        'Average 2023': [n_23],
        'Average 2024': [n_24],
        'Average 2025': [n_25],
        'Progress 2024': [n_24 - n_23],
        'Progress 2025': [n_25 - n_24]
    })

    df_comparison = pd.concat([df_comparison, n_row], ignore_index=True)
    
    df_comparison = df_comparison[['Dimension/Item', 'Average 2023', 'Average 2024', 'Progress 2024', 'Average 2025', 'Progress 2025']]

    st.subheader("🟣 Year-over-Year Dimension Comparison", divider="gray")
    
    styled_year = (
        df_comparison.style
        .applymap(highlight_progress, subset=['Progress 2024', 'Progress 2025'])
        .format({
            'Average 2023': '{:.2f}',
            'Average 2024': '{:.2f}',
            'Average 2025': '{:.2f}',
            'Progress 2024': '{:+.2f}',
            'Progress 2025': '{:+.2f}'
        }, na_rep='–')
    )
    st.dataframe(styled_year, use_container_width=True, hide_index=True)

    # -----------------------
    # Demography Comparison Table (Moved here)
    # -----------------------
    st.subheader("🟢 Year-over-Year Demographic Comparison", divider="gray")

    selected_dimension_for_demo_table = st.selectbox(
        "Select Dimension/Item for Demography Table:",
        options=list(satisfaction_map.keys()),
        format_func=lambda x: satisfaction_map.get(x, x),
        key="demo_table_dimension"
    )

    selected_demography_for_table = st.selectbox(
        "Select Demographic Variable:",
        options=columns_list,
        format_func=lambda x: x.capitalize(),
        key="demo_table_demography"
    )

    def summarize_by_demography(df, year, dimension_col, demo_col):
        if demo_col not in df.columns:
            return pd.DataFrame(columns=[demo_col, f'{year} Mean', f'{year} N'])
        
        temp = df.copy()
        # Handle NaN and ensure it's string for grouping
        temp[demo_col] = temp[demo_col].fillna("Missing").astype(str)

        grouped = (
            temp.groupby(demo_col)[dimension_col]
            .agg(['mean', 'count'])
            .round(2)
            .reset_index()
        )
        grouped.columns = [demo_col, f'{year} Mean', f'{year} N']
        return grouped


    demo_23 = summarize_by_demography(df_survey23_filtered, 2023, selected_dimension_for_demo_table, selected_demography_for_table)
    demo_24 = summarize_by_demography(df_survey24_filtered, 2024, selected_dimension_for_demo_table, selected_demography_for_table)
    demo_25 = summarize_by_demography(df_survey25_filtered, 2025, selected_dimension_for_demo_table, selected_demography_for_table)

    demo_merge = demo_23.merge(demo_24, on=selected_demography_for_table, how='outer')
    demo_merge = demo_merge.merge(demo_25, on=selected_demography_for_table, how='outer')

    for col in [f'{y} Mean' for y in [2023, 2024, 2025]]:
        if col in demo_merge.columns:
            demo_merge[col] = pd.to_numeric(demo_merge[col], errors='coerce')

    # 🟡 Remove rows where any N column equals 1
    n_cols = [f'{y} N' for y in [2023, 2024, 2025] if f'{y} N' in demo_merge.columns]
    rows_removed = 0
    if n_cols:
        condition = (demo_merge[n_cols] == 1).any(axis=1)
        rows_removed = condition.sum()
        demo_merge = demo_merge[~condition]

    # 📝 Confidentiality disclaimer
    if rows_removed > 0:
        st.write(
            f"Disclaimer: {rows_removed} entry/entries in the "
            f"'{selected_demography_for_table.capitalize()}' column were removed to protect confidentiality (N=1)."
        )

    # Calculate Progress
    if '2023 Mean' in demo_merge.columns and '2024 Mean' in demo_merge.columns:
        demo_merge['Progress 2024'] = demo_merge['2024 Mean'] - demo_merge['2023 Mean']
    if '2024 Mean' in demo_merge.columns and '2025 Mean' in demo_merge.columns:
        demo_merge['Progress 2025'] = demo_merge['2025 Mean'] - demo_merge['2024 Mean']

    cols = [selected_demography_for_table]
    if '2023 Mean' in demo_merge.columns: cols += ['2023 N', '2023 Mean']
    if '2024 Mean' in demo_merge.columns: cols += ['2024 N', '2024 Mean', 'Progress 2024']
    if '2025 Mean' in demo_merge.columns: cols += ['2025 N', '2025 Mean', 'Progress 2025']
    demo_merge = demo_merge[cols]

    if '2025 Mean' in demo_merge.columns:
        demo_merge = demo_merge.sort_values(by='2025 Mean', ascending=False)

    # Format table: 2 decimals for Mean/Progress, no decimals for N
    format_dict = {}
    for c in demo_merge.columns:
        if 'Mean' in c or 'Progress' in c:
            format_dict[c] = '{:.2f}'
        elif c.endswith('N'):
            format_dict[c] = '{:,.0f}'  # no decimals, thousands separator if needed

    styled_demo = (
        demo_merge.style
        .applymap(highlight_progress, subset=['Progress 2024', 'Progress 2025'])
        .format(format_dict, na_rep='–')
    )

    st.dataframe(styled_demo, use_container_width=True, hide_index=True)

    # -----------------------
    # Score Percentage charts (with year selector)
    # -----------------------
    st.subheader("🔵 Score Distribution by Dimension", divider="gray")

    selected_year_for_chart = st.radio(
        "Select Year for Score Percentage Charts:",
        options=[2023, 2024, 2025],
        index=2,  # 0 → 2023, 1 → 2024, 2 → 2025
        horizontal=True,
        key="score_percentage_year"
    )

    # Pick the filtered dataframe based on selected year
    if selected_year_for_chart == 2023:
        df_selected_year = df_survey23_filtered
    elif selected_year_for_chart == 2024:
        df_selected_year = df_survey24_filtered
    else:
        df_selected_year = df_survey25_filtered

    df_score_dimension = pd.DataFrame(columns=[1, 2, 3, 4, 5])

    for prefix, label in prefix_mapping.items():
        relevant_columns = [col for col in df_selected_year.columns if col.lower().startswith(prefix.lower())]
        if relevant_columns:
            prefix_data = df_selected_year[relevant_columns].melt(value_name='Score').drop(columns='variable')
            score_counts = (
                prefix_data['Score']
                .value_counts(normalize=True)
                .reindex(range(1, 6), fill_value=0) * 100
            ).round(1)
            df_score_dimension.loc[label] = score_counts.values

    df_score_dimension.reset_index(inplace=True)
    df_score_dimension.columns = ['Dimension', 1, 2, 3, 4, 5]
    df_score_dimension.columns = df_score_dimension.columns.astype(str)

    dimension_score_melt = df_score_dimension.melt(
        id_vars='Dimension',
        value_vars=['1', '2', '3', '4', '5'],
        var_name='Score',
        value_name='Percent'
    )

    overall_data = dimension_score_melt[dimension_score_melt['Dimension'] == 'Overall Satisfaction']
    other_data = dimension_score_melt[dimension_score_melt['Dimension'] != 'Overall Satisfaction']

    chart1 = px.bar(
        overall_data,
        x="Percent",
        y="Dimension",
        color="Score",
        orientation="h",
        text="Percent",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    chart1.update_traces(texttemplate='%{text:.1f}%', textposition='inside')

    chart2 = px.bar(
        other_data,
        x="Percent",
        y="Dimension",
        color="Score",
        orientation="h",
        text="Percent",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    chart2.update_traces(texttemplate='%{text:.1f}%', textposition='inside')

    try:
        chart1.for_each_trace(lambda t: t.update(name=score_labels[t.name]))
        chart2.for_each_trace(lambda t: t.update(name=score_labels[t.name]))
    except Exception:
        pass

    # Display charts (no expander)
    st.plotly_chart(chart1, use_container_width=True)
    st.plotly_chart(chart2, use_container_width=True)


else:
    st.warning("You are not authenticated — please log in to view this page.")
