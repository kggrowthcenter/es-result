from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
import altair as alt
from scipy import stats
import pandas as pd
import plotly.express as px
import numpy as np


st.set_page_config(
    page_title='Satisfaction',
    page_icon=':👍:', 
)

make_sidebar()

df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

st.write(len(df_survey24))

st.write(len(df_survey23))

# Satisfaction dimensions and items
satisfaction_columns = ['SAT', 'average_kd', 'average_ki', 'average_kr', 'average_pr', 'average_tu', 'average_ke']
satisfaction_columns_item = ['KD0', 'KD1', 'KD2', 'KD3', 'KE0', 'KE1', 'KE2', 'KE3', 'KI0', 'KI1', 'KI2', 'KI3', 'KI4', 'KI5', 'KR0', 'KR1', 'KR2', 'KR3', 'KR4', 'KR5', 'PR0', 'PR1', 'PR2', 'TU0', 'TU1', 'TU2', 'TU3']  # Replace with actual item-level columns

satisfaction_mapping = {
    'SAT': 'Overall Satisfaction',
    'average_kd': 'Kebutuhan Dasar',
    'average_ki': 'Kontribusi Individu',
    'average_kr': 'Kerjasama',
    'average_pr': 'Pertumbuhan',
    'average_tu': 'Tujuan',
    'average_ke': 'Keterlekatan'
}

satisfaction_mapping_item = {
    'KD0': 'KD0',
    'KD1': 'KD1',
    'KD2': 'KD2',
    'KD3': 'KD3',
    'KE0': 'KE0',
    'KE1': 'KE1',
    'KE2': 'KE2',
    'KE3': 'KE3',
    'KI0': 'KI0',
    'KI1': 'KI1',
    'KI2': 'KI2',
    'KI3': 'KI3',
    'KI4': 'KI4',
    'KI5': 'KI5',
    'KR0': 'KR0',
    'KR1': 'KR1',
    'KR2': 'KR2',
    'KR3': 'KR3',
    'KR4': 'KR4',
    'KR5': 'KR5',
    'PR0': 'PR0',
    'PR1': 'PR1',
    'PR2': 'PR2',
    'TU0': 'TU0',
    'TU1': 'TU1',
    'TU2': 'TU2',
    'TU3': 'TU3'
}

columns_list = [
    'unit', 'subunit', 'directorate', 'division', 'site', 'department', 'section',
    'layer', 'status', 'generation', 'gender', 
    'tenure_category', 'region', 'year'
]

# Mapping of user-friendly labels
prefix_mapping = {
    "SAT": "Overall Satisfaction",
    "KD": "Kebutuhan Dasar",
    "KI": "Kontribusi Individu",
    "KR": "Kerjasama",
    "PR": "Pertumbuhan",
    "TU": "Tujuan",
    "KE": "Keterlekatan"
}

# Define custom labels for the legend
score_labels = {
    "1": "Sangat Tidak Setuju",
    "2": "Tidak Setuju",
    "3": "Netral",
    "4": "Setuju",
    "5": "Sangat Setuju"
}

# Extract the logged-in user's unit after authentication
if st.session_state.get('authentication_status'):
    # Retrieve the username from session state
    username = st.session_state['username']

    # Get the user's units from the credentials and split by commas
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    st.write(user_units)
    # Filter the survey data by the user's units (checking if unit is in user's units)
    df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]
    df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]

    # SECTION - SATISFACTION SCORE
    st.header('Satisfaction Score', divider='rainbow')

    # Add checkbox to toggle analysis level
    item_level_analysis = st.checkbox("Check to analyze at item level", value=False)

    # If the checkbox is selected, display descriptions in a table
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

    # Choose columns and mapping based on the selected analysis level
    if item_level_analysis:
        satisfaction_columns = satisfaction_columns_item
        satisfaction_mapping = satisfaction_mapping_item
        prefix_mapping = satisfaction_mapping_item
    else:
        satisfaction_columns = satisfaction_columns
        satisfaction_mapping = satisfaction_mapping
        prefix_mapping = prefix_mapping

    # ==============================
    # DATASETS
    # ==============================
    datasets = {
        "2024": df_survey24,
        "2025": df_survey25
    }

    # ==============================
    # FILTERS (apply to both datasets) - call make_filter once
    # ==============================
    # pass a combined dataframe so filter options include all possible values across years
    combined_for_filters = pd.concat([df_survey24, df_survey25], ignore_index=True)
    selected_filters = make_filter(columns_list, combined_for_filters, key_prefix="filter")  # returns dict

    def apply_selected_filters(df, selected_filters):
        if not selected_filters:
            return df.copy()
        filtered = df.copy()
        for col, values in selected_filters.items():
            if not values:
                continue
            # Only attempt to filter if column exists in this dataframe
            if col in filtered.columns:
                filtered = filtered[filtered[col].isin(values)]
        return filtered

    # Apply to both datasets
    df_survey24_filtered = apply_selected_filters(df_survey24, selected_filters)
    df_survey25_filtered = apply_selected_filters(df_survey25, selected_filters)

    # ==============================
    # Add missing satisfaction columns as NaN
    # ==============================
    for col in satisfaction_columns:
        if col not in df_survey24_filtered.columns:
            df_survey24_filtered[col] = pd.NA
        if col not in df_survey25_filtered.columns:
            df_survey25_filtered[col] = pd.NA

    # Convert all satisfaction columns to numeric (so mean() works)
    for col in satisfaction_columns:
        df_survey24_filtered[col] = pd.to_numeric(df_survey24_filtered[col], errors='coerce')
        df_survey25_filtered[col] = pd.to_numeric(df_survey25_filtered[col], errors='coerce')
    
    # ==============================
    # COMPARISON TABLE (2024 vs 2025)
    # ==============================

    # Compute averages
    df_avg_24 = df_survey24_filtered[satisfaction_columns].mean().round(2).reset_index()
    df_avg_24.columns = ['Dimension/Item', 'Average 2024']

    df_avg_25 = df_survey25_filtered[satisfaction_columns].mean().round(2).reset_index()
    df_avg_25.columns = ['Dimension/Item', 'Average 2025']

    # Merge 2024 & 2025
    df_comparison = pd.merge(df_avg_24, df_avg_25, on="Dimension/Item", how="outer")

    # Map user-friendly names (if applicable)
    df_comparison['Dimension/Item'] = df_comparison['Dimension/Item'].map(satisfaction_mapping).fillna(df_comparison['Dimension/Item'])

    # Calculate difference
    df_comparison['Difference'] = df_comparison['Average 2025'] - df_comparison['Average 2024']

    # Filter hanya yang punya submit_date (bukan NaN dan bukan string kosong)
    respondents_24 = df_survey24_filtered[
        df_survey24_filtered['submit_date'].notna() & (df_survey24_filtered['submit_date'] != "")
    ]

    respondents_25 = df_survey25_filtered[
        df_survey25_filtered['submit_date'].notna() & (df_survey25_filtered['submit_date'] != "")
    ]

    # Hitung N
    n_24 = len(respondents_24)
    n_25 = len(respondents_25)

    # Build N row
    n_row = pd.DataFrame({
        'Dimension/Item': ['N'],
        'Average 2024': [n_24],
        'Average 2025': [n_25],
        'Difference': [None]
    })

    # Concatenate N row to the comparison table
    df_comparison = pd.concat([df_comparison, n_row], ignore_index=True)

    # Display the table without the default index
    st.subheader("Year Comparison", divider="gray")

    st.dataframe(
        df_comparison.reset_index(drop=True),  # drop old index
        use_container_width=True,
        hide_index=True  # 🚀 hides the index column completely
    )

    # ==============================
    # Choose dataset for charts (based on year filter inside selected_filters)
    # ==============================
    # selected_filters.get('year') will be a list (because make_filter uses multiselect for year)
    selected_years = selected_filters.get('year', [])

    if not selected_years:
        # no year selected → default to 2025 (or you can default to both by uncommenting concat below)
        selected_year = "2025"
        df_survey = df_survey25_filtered
    elif len(selected_years) == 1:
        selected_year = selected_years[0]
        df_survey = df_survey24_filtered if selected_year == "2024" else df_survey25_filtered
    else:
        # both years selected → combine for charts (you may also choose to default to one year)
        selected_year = ", ".join(selected_years)
        df_survey = pd.concat([df_survey24_filtered, df_survey25_filtered], ignore_index=True)

    # keep the old variable name used later in your code
    filtered_data = df_survey

    # SECTION - Dimension/Item COMPARISON
    st.subheader(f'Dimension/Item Comparison', divider='gray')

    # ==============================
    # MEAN CALCULATION (use filtered_data)
    # ==============================
    
    # Ensure blanks are treated as NaN
    filtered_data['submit_date'] = filtered_data['submit_date'].replace("", pd.NA)

    # Count only rows with a non-null submitted_on
    sample_size = filtered_data['submit_date'].notna().sum()

    # Build a readable filter display (human friendly)
    if selected_filters:
        filter_display_parts = []
        # Add Year explicitly if selected
        if "year" in selected_filters and selected_filters["year"]:
            filter_display_parts.append(f"Year: {', '.join(map(str, selected_filters['year']))}")
        else:
            # Default year = 2025 if not selected
            filter_display_parts.append("Year: 2025")

        # Add other filters
        for col, vals in selected_filters.items():
            if col == "year":  # already handled
                continue
            if vals:
                filter_display_parts.append(f"{col.capitalize()}: {', '.join(map(str, vals))}")

        filter_display = " | ".join(filter_display_parts)

    else:
        # No filters at all → default to Year 2025
        filter_display = "Year: 2025"

    # Calculate the average satisfaction scores for each dimension and overall satisfaction
    df_avg_dimensions = filtered_data[satisfaction_columns].mean().round(2).reset_index()
    df_avg_dimensions.columns = ['dimension', 'average_score']
    df_avg_dimensions['dimension'] = df_avg_dimensions['dimension'].map(satisfaction_mapping)
    df_avg_dimensions = df_avg_dimensions.sort_values(by='average_score', ascending=False)

    # MEAN CHART
    
    # Create the bar chart with no hover data
    dimension_mean = px.bar(
        df_avg_dimensions,
        x='dimension',
        y='average_score',
        text='average_score',                    # Display score labels on each bar
        hover_data={}                            # Disable tooltips by passing an empty dictionary
    )

    # Customize appearance, setting color conditionally for "Overall Satisfaction"
    dimension_mean.update_traces(
        texttemplate='%{text:.2f}',              # Format labels to 1 decimal
        marker_color=[
            '#A020F0' if dim == 'Overall Satisfaction' else '#1f77b4' 
            for dim in df_avg_dimensions['dimension']
        ],
        textposition='outside'
    )

    # Configure layout, fully removing the title
    dimension_mean.update_layout(
        title_text=f"Mean Score of {filter_display} (N={sample_size})",
        xaxis_title=" ",
        yaxis_title=" ",
        xaxis=dict(tickangle=0, tickfont=dict(size=10)),
        yaxis=dict(range=[0, df_avg_dimensions['average_score'].max() + 1])
    )

    # Display in Streamlit
    st.plotly_chart(dimension_mean, use_container_width=True)

    # SCORE CALCULATION

    # Initialize an empty DataFrame for the result
    df_score_dimension = pd.DataFrame(columns=[1, 2, 3, 4, 5])

    # Sort dimensions by average score and exclude "Overall Satisfaction"
    sorted_dimensions = (
        df_avg_dimensions
        .sort_values(by='average_score', ascending=False)
        ['dimension']
        .loc[lambda x: x != "Overall Satisfaction"]
        .tolist()
    )

    # Iterate through each prefix in the mapping
    for prefix, label in prefix_mapping.items():
        # Filter columns that start with the prefix
        relevant_columns = [col for col in filtered_data.columns if col.lower().startswith(prefix.lower())]
        
        # Subset the DataFrame to only the relevant columns
        if relevant_columns:
            prefix_data = filtered_data[relevant_columns].melt(value_name='Score').drop(columns='variable')
            
            # Count the occurrences of each score (1 to 5)
            score_counts = (prefix_data['Score'].value_counts(normalize=True).reindex(range(1, 6), fill_value=0) * 100).round(1)
            
            # Add the counts as a new row in the result DataFrame
            df_score_dimension.loc[label] = score_counts.values

    # Display the final DataFrame
    df_score_dimension.reset_index(inplace=True)
    df_score_dimension.columns = ['Dimension', 1, 2, 3, 4, 5]
    df_score_dimension.columns = df_score_dimension.columns.astype(str)

    # Transform data for Altair
    dimension_score_melt = df_score_dimension.melt(
        id_vars='Dimension',
        value_vars=['1', '2', '3', '4', '5'],
        var_name='Score',
        value_name='Percent'
    )

    # SCORE CHART

    # Separate the data for Overall Satisfaction and other dimensions
    overall_satisfaction_data = dimension_score_melt[dimension_score_melt['Dimension'] == 'Overall Satisfaction']
    other_dimensions_data = dimension_score_melt[dimension_score_melt['Dimension'] != 'Overall Satisfaction']

    # Create the Plotly stacked bar chart for Overall Satisfaction
    chart1 = px.bar(
        overall_satisfaction_data,
        x="Percent",
        y="Dimension",
        color="Score",
        orientation="h",
        text="Percent",  # Add labels to display percentages
        color_discrete_sequence=px.colors.sequential.Purples,  # Use a distinct color for Overall Satisfaction
        title=" ",
    )

    # Update layout for chart1
    chart1.update_traces(texttemplate='%{text:.1f}%', textposition='inside')  # Format labels and position inside bars
    chart1.update_layout(
        xaxis_title=" ",
        yaxis_title=" ",
        legend_title=" ",
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=-0.2,  # Position below the chart
            xanchor="center",
            x=0.5
        ),
        bargap=0.02
    )

    # Create the Plotly stacked bar chart for other dimensions
    chart2 = px.bar(
        other_dimensions_data,
        x="Percent",
        y="Dimension",
        color="Score",
        orientation="h",
        text="Percent",  # Add labels to display percentages
        color_discrete_sequence=px.colors.sequential.Blues,  # Use a distinct color for other dimensions
        title=" ",
        category_orders={"Dimension": sorted_dimensions}  # Order dimensions by sorted average score
    )

    # Update layout for chart2
    chart2.update_traces(texttemplate='%{text:.1f}%', textposition='inside')  # Format labels and position inside bars
    chart2.update_layout(
        xaxis_title=" ",
        yaxis_title=" ",
        legend_title=" ",
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=-0.2,  # Position below the chart
            xanchor="center",
            x=0.5
        ),
        bargap=0.02
    )

    # Update the legend text using the custom labels
    chart1.for_each_trace(lambda t: t.update(name=score_labels[t.name]))
    chart2.for_each_trace(lambda t: t.update(name=score_labels[t.name]))

    # Display charts in Streamlit
    with st.expander('Score Percentage'):
        st.plotly_chart(chart1, use_container_width=True)
        st.plotly_chart(chart2, use_container_width=True)
    
    # SECTION - SATISFACTION COMPARED BY DEMOGRAPHY

    # Display subheader
    st.subheader(f'Demography Comparison', divider='gray')

    # FILTER 2
    # User selection for comparison column and satisfaction dimension
    satisfaction_column = st.selectbox(
        'Select the dimension/item to display:',
        options=list(satisfaction_mapping.keys()),
        format_func=lambda x: satisfaction_mapping.get(x, x)
    )

    comparison_column = st.selectbox(
        'Select the column for comparison:',
        options=columns_list,
        format_func=lambda x: x.capitalize()  # Capitalizes the comparison column name for display
    )


    # MEAN 2 CALCULATION
 
    # Calculate the overall average for the selected satisfaction column
    overall_average = filtered_data[satisfaction_column].mean().round(2)

    # Calculate the total sample size (N)
    total_n = filtered_data[satisfaction_column].count()

    # Display the overall average and total N before the bar chart
    #st.metric(label=f"Overall Average for {satisfaction_mapping[satisfaction_column]}", 
    st.metric(label=f"Total Mean", 
            value=f"{overall_average} (N= {total_n})")

    # Group by the selected column, calculate average satisfaction score and count (N)
    df_avg_demography = filtered_data.groupby(comparison_column).agg(
        avg_satisfaction=(satisfaction_column, 'mean'),
        count=(satisfaction_column, 'count')
    ).round(2).reset_index()

    # Confidentiality check: Store original size before filtering
    original_size = df_avg_demography.shape[0]

    # Confidentiality check: Remove rows where N=1
    df_avg_demography = df_avg_demography[df_avg_demography['count'] > 1]

    # Calculate the number of rows removed
    rows_removed = original_size - df_avg_demography.shape[0]

    # If any rows were removed, show the disclaimer
    if rows_removed > 0:
        st.write(f"Disclaimer: {rows_removed} entry/entries in the '{comparison_column.capitalize()}' column were removed to protect confidentiality (N=1).")

    # Determine sorting behavior based on comparison_column
    if comparison_column in ['layer', 'tenure_category']:
        # Sort by the comparison column itself
        df_avg_demography = df_avg_demography.sort_values(by=comparison_column, ascending=False)
    else:
        # Sort by average satisfaction score in descending order
        df_avg_demography = df_avg_demography.sort_values(by='avg_satisfaction', ascending=True)

    # MEAN 2 CHART

    # Calculate a dynamic height with a minimum threshold
    min_height = 300  # Set a minimum height (adjust as necessary)
    dynamic_height = max(len(df_avg_demography) * 40, min_height)  # Ensure height is at least min_height

    # Create the bar chart with no hover data
    demography_mean = px.bar(
        df_avg_demography,
        y=comparison_column,
        x='avg_satisfaction',
        hover_data={}                            # Disable tooltips by passing an empty dictionary
    )

    # Customize appearance, setting color conditionally for "Overall Satisfaction"
    demography_mean.update_traces(
        texttemplate='%{x:.2f} (N=%{customdata[0]})',  # Customize label format
        customdata=df_avg_demography[['count']].values,  # Pass count as custom data for use in texttemplate
        marker_color='#1f77b4',
        textposition='outside'
    )

    # Configure layout, fully removing the title
    demography_mean.update_layout(
        title_text=f'{satisfaction_mapping[satisfaction_column]} compared by {comparison_column.capitalize()}',                           # Ensure no title is displayed
        yaxis_title=" ",
        xaxis_title=" ",
        yaxis=dict(tickangle=0, tickfont=dict(size=10)),  # Adjust x-axis label font size
        xaxis=dict(range=[0, df_avg_demography['avg_satisfaction'].max() + 1]),  # Adjust y-axis range
        height=dynamic_height  # Set the dynamic height
    )

    # Display in Streamlit
    st.plotly_chart(demography_mean, use_container_width=True)

    # Check if 'layer' is selected
    if 'layer' in comparison_column:
        st.write("""
        - **Group 1** = Pelaksana
        - **Group 1 Str Layer 5** = Team Leader
        - **Group 2** = Professional setara Officer
        - **Group 2 Str Layer 4** = Superintendent
        - **Group 3** = Professional setara Manager (Specialist / Senior Officer)
        - **Group 3 Str Layer 3A** = Manager
        - **Group 3 Str Layer 3B** = Senior Manager
        - **Group 4** = Professional setara GM (Advisor)
        - **Group 4 Str Layer 2** = GM / Senior GM / Vice GM / Deputy GM / Vice Rector
        - **Group 5** = Professional setara Director (Consultant)
        - **Group 5 Str Layer 1** = CEO / Director / Vice Director / Deputy Director / Vice President / Assistant Vice President / Rector
        """)

    # SCORE 2 CALCULATION

    # Adjust the sorting behavior based on the comparison_column for the list
    if comparison_column in ['layer', 'tenure_category']:
        # Sort by the comparison column itself and get the list
        sorted_demography = df_avg_demography.sort_values(by=comparison_column, ascending=True)[comparison_column].tolist()
    else:
        # Sort by avg_satisfaction and get the list
        sorted_demography = df_avg_demography.sort_values(by='avg_satisfaction', ascending=False)[comparison_column].tolist()

    # Automatically set the prefix based on the selected dimension
    prefix = [key for key, value in prefix_mapping.items() if value == satisfaction_mapping[satisfaction_column]]
    if prefix:
        selected_prefix = prefix[0]  # Select the first match if available
    else:
        st.warning("No matching prefix found for this dimension.")
        selected_prefix = None  # Default to None if no match

    # Filter columns based on selected prefix
    if selected_prefix:
        # Filter columns based on the selected prefix
        filtered_columns = [col for col in df_survey.columns if col.startswith(selected_prefix) and col != comparison_column]

        # Melt the DataFrame to long format for the selected prefix
        df_long = filtered_data.melt(id_vars=comparison_column, value_vars=filtered_columns,
                                var_name='Question', value_name='Score')

    # Melt the DataFrame to long format
    df_long = filtered_data.melt(id_vars=comparison_column, value_vars=filtered_columns,
                            var_name='Question', value_name='Score')

    # Count the scores
    score_counts = df_long.groupby([comparison_column, 'Score']).size().unstack(fill_value=0)

    # Filter out rows where the sum of values across columns is 1
    score_counts = score_counts[score_counts.sum(axis=1) > 1]

    # Calculate percentages
    percentage_counts = score_counts.div(score_counts.sum(axis=1), axis=0) * 100

    percentage_counts = percentage_counts.reset_index()
    
    # Convert only numeric column headers to integers and remove decimal points
    percentage_counts.columns = [
        str(int(float(str(col)))) if str(col).replace('.', '', 1).isdigit() else str(col)
        for col in percentage_counts.columns
    ]
    
        # Ensure all score columns exist
    if '1' not in percentage_counts:
        percentage_counts['1'] = 0
    if '2' not in percentage_counts:
        percentage_counts['2'] = 0
    if '3' not in percentage_counts:
        percentage_counts['3'] = 0
    if '4' not in percentage_counts:
        percentage_counts['4'] = 0
    if '5' not in percentage_counts:
        percentage_counts['5'] = 0

    # Ensure the correct order of columns before renaming
    percentage_counts = percentage_counts[[comparison_column, '1', '2', '3', '4', '5']]

    # Transform data for Altair
    melted_counts = percentage_counts.melt(
        id_vars=comparison_column,
        value_vars=['1', '2', '3', '4', '5'],
        var_name='Score',
        value_name='Percent'
    )

    # SCORE 2 CHART

    # Create the Plotly stacked bar chart
    fig = px.bar(
        melted_counts,
        x="Percent",
        y=comparison_column,
        color="Score",
        orientation="h",
        text="Percent",                   # Add labels to display percentages
        color_discrete_sequence=px.colors.sequential.Blues,
        title=" ",
        category_orders={comparison_column: sorted_demography}  # Order dimensions by sorted average score
    )

    # Update layout for label display and legend position
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')   # Format labels and position inside bars
    fig.update_layout(
        xaxis_title=" ",
        yaxis_title=" ",
        legend_title=" ",
        legend=dict(
            orientation="h",              # Horizontal legend
            yanchor="top",
            y=-0.2,                       # Position below the chart
            xanchor="center",
            x=0.5
        ),
        bargap=0.02,
        height=dynamic_height  # Set the dynamic height
    )

    # Update the legend text using the custom labels
    fig.for_each_trace(lambda t: t.update(name=score_labels[t.name]))

    # Display in Streamlit
    with st.expander('Score Percentage'):
        st.plotly_chart(fig, use_container_width=True)

    # SECTION - ADDITIONAL
    st.subheader(f'Additional', divider='gray')

    # SECTION - MEAN DIFFERENCE TEST
    df_survey24_filtered["year"] = 2024
    df_survey25_filtered["year"] = 2025

    df_survey = pd.concat([df_survey24_filtered, df_survey25_filtered], ignore_index=True)

    # Only keep rows with valid submit_date (not NaN, not empty, not whitespace)
    valid_mask = df_survey['submit_date'].notna() & (df_survey['submit_date'].astype(str).str.strip() != "")

    # New expander for testing mean differences
    with st.expander("Uji Beda Rata-rata Kelompok", expanded=False):
        st.subheader("Apakah terdapat perbedaan rata-rata kepuasan antar kelompok?", divider='gray')

        # User selects a dimension or overall satisfaction for testing mean difference
        test_dimension = st.selectbox(
            "Pilih dimensi/item kepuasan yang ingin diuji beda:",
            options=satisfaction_columns,
            format_func=lambda x: satisfaction_mapping.get(x, x)
        )

        # User selects a grouping variable (e.g., unit, gender, etc.)
        group_column = st.selectbox(
            "Pilih demografi yang ingin diuji beda:",
            options=columns_list,
            format_func=lambda x: x.capitalize()
        )

        # User selects the specific groups to compare
        selected_groups = st.multiselect(
            f"Pilih kelompok {group_column.capitalize()} yang ingin diuji beda:",
            options=df_survey[group_column].unique(),
            key='group_selection'
        )

        # Checkbox for comparing a specific group against the overall group
        compare_with_overall = st.checkbox("Bandingkan dengan Total KG")

        if compare_with_overall and len(selected_groups) == 1:
            group_data = df_survey[(df_survey[group_column] == selected_groups[0]) & valid_mask][test_dimension]
            overall_data = df_survey[valid_mask][test_dimension]

            # Calculate means and sample sizes
            mean_group = group_data.mean()
            mean_overall = overall_data.mean()
            n_group = group_data.notna().sum()
            n_overall = overall_data.notna().sum()

            # Perform t-test
            t_stat, p_value = stats.ttest_ind(group_data, overall_data, equal_var=False)

            # Display
            st.write(f"***{selected_groups[0]}** - **Rata-rata:** {mean_group:.2f}, **Total responden:** {n_group}*")
            st.write(f"***Total KG - Rata-rata:** {mean_overall:.2f}, **Total responden:** {n_overall}*")
            st.write(f"**t-statistic:** {t_stat:.4f}, **p-value:** {p_value:.4f}")

            test_dimension_label = satisfaction_mapping.get(test_dimension, test_dimension)
            if p_value < 0.05:
                st.success(f"Terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara {selected_groups[0]} dan Total KG (p < 0.05).")
            else:
                st.info(f"Tidak terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara {selected_groups[0]} dan Total KG (p ≥ 0.05).")

        elif len(selected_groups) == 2:
            group1_data = df_survey[(df_survey[group_column] == selected_groups[0]) & valid_mask][test_dimension]
            group2_data = df_survey[(df_survey[group_column] == selected_groups[1]) & valid_mask][test_dimension]

            mean_group1 = group1_data.mean()
            mean_group2 = group2_data.mean()
            n_group1 = group1_data.notna().sum()
            n_group2 = group2_data.notna().sum()

            t_stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=False)

            st.write(f"***{selected_groups[0]}** - **Rata-rata:** {mean_group1:.2f}, **Total responden:** {n_group1}*")
            st.write(f"***{selected_groups[1]}** - **Rata-rata:** {mean_group2:.2f}, **Total responden:** {n_group2}*")
            st.write(f"**t-statistic:** {t_stat:.4f}, **p-value:** {p_value:.4f}")

            test_dimension_label = satisfaction_mapping.get(test_dimension, test_dimension)
            if p_value < 0.05:
                st.success(f"Terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara {selected_groups[0]} dan {selected_groups[1]} (p < 0.05).")
            else:
                st.info(f"Tidak terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara {selected_groups[0]} dan {selected_groups[1]} (p ≥ 0.05).")

        elif len(selected_groups) > 2:
            filtered_anova_data = df_survey[(df_survey[group_column].isin(selected_groups)) & valid_mask]

            groups_data = [filtered_anova_data[filtered_anova_data[group_column] == group][test_dimension] for group in selected_groups]

            means = [g.mean() for g in groups_data]
            ns = [g.notna().sum() for g in groups_data]

            f_stat, p_value = stats.f_oneway(*groups_data)

            for group, mean, n in zip(selected_groups, means, ns):
                st.write(f"***{group}** - **Mean:** {mean:.2f}, **N responden:** {n}*")
            st.write(f"**F-statistic:** {f_stat:.4f}, **p-value:** {p_value:.4f}")

            test_dimension_label = satisfaction_mapping.get(test_dimension, test_dimension)
            if p_value < 0.05:
                st.success(f"Terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara kelompok-kelompok yang dipilih (p < 0.05).")
            else:
                st.info(f"Tidak terdapat perbedaan rata-rata {test_dimension_label} yang signifikan antara kelompok-kelompok yang dipilih (p ≥ 0.05).")

    # Example of extracting respondents in 2024 only (with valid submit_date)
    df_2024 = df_survey[(df_survey['year'] == 2024) & valid_mask]

