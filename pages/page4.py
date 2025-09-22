from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='NPS',
    page_icon=':🗣️:',
)

make_sidebar()

# Load and display data
df_survey, df_creds, combined_df = finalize_data()

# FILTER FROM NAVIGATION (use custom list of columns)
columns_list = [
    'unit', 'subunit', 'directorate', 'division', 'department', 'section',
    'layer', 'status', 'generation', 'gender', 'marital', 'education',
    'tenure_category', 'children', 'region', 'participation_23'
]

# SESSION STATE
if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    df_survey = df_survey[df_survey['subunit'].isin(user_units)]

    # Calculate NPS and category counts
    def calculate_nps(df):
        # Ensure NPS column is numeric
        df['NPS'] = pd.to_numeric(df['NPS'], errors='coerce')

        # Count Promoters, Passives, and Detractors
        total_responses = df['NPS'].count()
        promoters = df[(df['NPS'] >= 9)].shape[0]
        passives = df[(df['NPS'] >= 7) & (df['NPS'] <= 8)].shape[0]
        detractors = df[(df['NPS'] <= 6)].shape[0]

        # Calculate percentages
        percent_promoters = (promoters / total_responses) * 100 if total_responses > 0 else 0
        percent_passives = (passives / total_responses) * 100 if total_responses > 0 else 0
        percent_detractors = (detractors / total_responses) * 100 if total_responses > 0 else 0

        # Calculate NPS
        nps_score = percent_promoters - percent_detractors  # Calculate difference first
        nps_score = round(nps_score, 1)
        return nps_score, promoters, percent_promoters, passives, percent_passives, detractors, percent_detractors, total_responses

    nps_score, promoters, percent_promoters, passives, percent_passives, detractors, percent_detractors, total_responses = calculate_nps(df_survey)

    # Define NPS category based on score
    def categorize_nps(score):
        if score <= 0:
            return 'Needs Improvement (-100 to 0)'
        elif 0 < score <= 30:
            return 'Good (0 to 30)'
        elif 30 < score <= 70:
            return 'Great (30 to 70)'
        else:
            return 'Excellent (70 to 100)'

    nps_category = categorize_nps(nps_score)
    
    # Display NPS results and category
    st.header('Net Promoter Score Overview', divider='rainbow')
    # Apply filters to the survey data
    filtered_data, selected_filters = make_filter(columns_list, df_survey)

    # Recalculate NPS breakdown based on the filtered data
    promoters = filtered_data[filtered_data['NPS'] >= 9].shape[0]
    passives = filtered_data[(filtered_data['NPS'] >= 7) & (filtered_data['NPS'] <= 8)].shape[0]
    detractors = filtered_data[filtered_data['NPS'] <= 6].shape[0]

    total_responses = filtered_data.shape[0]
    percent_promoters = (promoters / total_responses) * 100 if total_responses > 0 else 0
    percent_passives = (passives / total_responses) * 100 if total_responses > 0 else 0
    percent_detractors = (detractors / total_responses) * 100 if total_responses > 0 else 0

    percent_promoters = (promoters / total_responses) * 100 if total_responses > 0 else 0
    percent_passives = (passives / total_responses) * 100 if total_responses > 0 else 0
    percent_detractors = (detractors / total_responses) * 100 if total_responses > 0 else 0

    nps_score = percent_promoters - percent_detractors

    # Create columns to display data in an organized way
    col1, col2 = st.columns([1, 1])

    # First column for NPS Score
    with col1:
        st.write(f"#### **NPS Score**")
        st.write(f"**{nps_score:.1f}%**")
        st.write(f"#### **NPS Category**")
        st.write(f"**{nps_category}**")

    # Middle column for breakdown of responses
    with col2:
        st.write(f"#### **NPS Breakdown**")
        st.write(f"**Promoters:** {promoters} - {percent_promoters:.2f}%")
        st.write(f"**Passives:** {passives} - {percent_passives:.2f}%")
        st.write(f"**Detractors:** {detractors} - {percent_detractors:.2f}%")
        st.write(f"**Total Responses:** {total_responses}")

    st.divider()

    # Prepare data for visualization with counts and percentages
    nps_data = pd.DataFrame({
        'Category': ['Promoters', 'Passives', 'Detractors'],
        'Count': [promoters, passives, detractors],
        'Percent': [percent_promoters, percent_passives, percent_detractors]
    })

    # Create bar chart with Plotly
    fig_nps = go.Figure()

    # Add bars
    fig_nps.add_trace(go.Bar(
        x=nps_data['Category'],
        y=nps_data['Count'],
        marker_color=['steelblue', 'skyblue', 'tomato'],
        text=nps_data['Percent'].apply(lambda x: f"{x:.1f}%"),
        textposition='outside',  # Position text outside the bar
        name='Count'
    ))

    # Update layout
    fig_nps.update_layout(
        title='NPS Breakdown',
        xaxis_title='Category',
        yaxis_title='Count',
        showlegend=False,
        height=500
    )

    # Display chart
    st.plotly_chart(fig_nps, use_container_width=True)

    # Create color-coded legend for NPS score categories
    st.markdown("###### NPS Score Categories")
    legend_columns = st.columns(4)

    categories = [
        {"label": "Needs Improvement (-100 to 0)", "color": "#c7522a"},
        {"label": "Good (0 to 30)", "color": "#e9c46a"},
        {"label": "Great (30 to 70)", "color": "#74a892"},
        {"label": "Excellent (70 to 100)", "color": "#264653"},
    ]

    # Display each category with color
    for col, category in zip(legend_columns, categories):
        col.markdown(f"<div style='background-color: {category['color']}; padding: 5px; border-radius: 4px; text-align: center;'>{category['label']}</div>", unsafe_allow_html=True)

    st.divider()

    # Check if data is available after applying filters
    selected_filters = st.selectbox(
        "Select Filter",
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    # STACKED DATA
    if selected_filters in filtered_data.columns:
        # Group the data by the selected filter and calculate counts for each NPS category
        grouped_counts = filtered_data.groupby(selected_filters).apply(lambda x: pd.Series({
            'Promoters': (x['NPS'] >= 9).sum(),
            'Passives': ((x['NPS'] >= 7) & (x['NPS'] <= 8)).sum(),
            'Detractors': (x['NPS'] <= 6).sum()
        })).reset_index()
        
        # Identify rows where the total count is exactly 1
        rows_to_remove = grouped_counts[grouped_counts[['Promoters', 'Passives', 'Detractors']].sum(axis=1) == 1]
        indices_to_remove = rows_to_remove[selected_filters].tolist()

        # Group the data by the selected filter and calculate NPS percentages
        grouped = filtered_data.groupby(selected_filters).apply(lambda x: pd.Series({
            'Promoters': (x['NPS'] >= 9).mean() * 100,
            'Passives': ((x['NPS'] >= 7) & (x['NPS'] <= 8)).mean() * 100,
            'Detractors': (x['NPS'] <= 6).mean() * 100
        })).reset_index()

        # Calculate the count of NPS categories for each group
        count_nps = filtered_data.groupby(selected_filters).apply(lambda x: pd.Series({
            'Promoters_Count': (x['NPS'] >= 9).sum(),
            'Passives_Count': ((x['NPS'] >= 7) & (x['NPS'] <= 8)).sum(),
            'Detractors_Count': (x['NPS'] <= 6).sum(),
        })).reset_index()

        # Merge the grouped percentages with the count_nps
        merged_data = pd.merge(grouped, count_nps, on=selected_filters)

        # Confidentiality check: Store original size before filtering
        original_size = merged_data.shape[0]

        # Remove rows where the total count was 1 (confidentiality protection)
        merged_data = merged_data[(merged_data[['Promoters', 'Passives', 'Detractors']].sum(axis=1) > 0)]

        # Calculate the number of rows removed
        rows_removed = original_size - merged_data.shape[0]

        # Show disclaimer if any rows were removed
        if rows_removed > 0:
            st.write(f"Disclaimer: {rows_removed} entry/entries in the '{selected_filters.capitalize()}' column were removed to protect confidentiality (N=1).")

        # Melt the merged data for both percentages and counts
        stacked_data = merged_data.melt(id_vars=selected_filters, 
                                        value_vars=['Promoters', 'Passives', 'Detractors'],
                                        var_name='NPS Category', value_name='Percentage')

        stacked_data_count = merged_data.melt(id_vars=selected_filters, 
                                            value_vars=['Promoters_Count', 'Passives_Count', 'Detractors_Count'],
                                            var_name='NPS Counts', value_name='Counts')

        # Combine both percentage and count data
        stacked_data['Counts'] = stacked_data_count['Counts']

        # Create stacked bar chart with Plotly
        fig_stacked = go.Figure()

        # Define colors for each category
        colors = {
            'Promoters': 'steelblue',
            'Passives': 'skyblue',
            'Detractors': 'tomato'
        }

        # Add bars for each NPS category
        for category in stacked_data['NPS Category'].unique():
            category_data = stacked_data[stacked_data['NPS Category'] == category]
            
            fig_stacked.add_trace(go.Bar(
                y=category_data[selected_filters],  # Use the selected filter for y-axis
                x=category_data['Percentage'],  # Percentage for x-axis
                name=f"{category}",
                text=category_data.apply(lambda row: f"{row['Percentage']:.1f}%<br>({int(row['Counts'])})", axis=1),
                textposition='inside',
                marker_color=colors[category],
                orientation='h'
            ))

        # Ensure the columns are numeric and fill missing values with 0
        grouped['Promoters'] = grouped['Promoters'].fillna(0).astype(int)
        grouped['Passives'] = grouped['Passives'].fillna(0).astype(int)
        grouped['Detractors'] = grouped['Detractors'].fillna(0).astype(int)

        # Calculate NPS score for each group, rounded to the nearest whole number
        nps_per_unit = grouped.apply(lambda row: round(((row['Promoters'] * 1 + row['Passives'] * 0 + row['Detractors'] * -1) / 100) * 100) if row['Promoters'] + row['Passives'] + row['Detractors'] != 0 else 0, axis=1)
        grouped_filtered = grouped[~grouped[selected_filters].isin(indices_to_remove)]

        # Ambil kategori yang ada di stacked_data supaya angka NPS cuma muncul buat kategori yang ditampilkan
        valid_categories = stacked_data[selected_filters].unique()

        for unit_name in valid_categories:
            # Ambil data spesifik untuk kategori yang masih ada
            row = grouped_filtered[grouped_filtered[selected_filters] == unit_name]

            if not row.empty:  # Pastikan ada datanya
                promoters = row['Promoters'].values[0]
                detractors = row['Detractors'].values[0]

                # Hitung NPS sesuai dengan kategori yang ada
                nps = round(((promoters - detractors) / 100) * 100)

                # Tambahkan annotation hanya jika kategori valid
                fig_stacked.add_annotation(
                    x=1.03,  # Tetap di kanan
                    y=unit_name,
                    xref="paper", yref="y",
                    text=f'{nps}%',  # Sesuai dengan data bar
                    showarrow=False,
                    font=dict(size=14, color="grey"),
                    align="left"
                )


        # Update layout of the chart
        fig_stacked.update_layout(
            title=f'NPS Breakdown by {selected_filters.title()}',
            xaxis_title='Percentage',
            yaxis_title=selected_filters.title(),
            barmode='stack',
            height=600,
            width=1000
        )

        # Display the stacked bar chart
        st.plotly_chart(fig_stacked, use_container_width=True)
