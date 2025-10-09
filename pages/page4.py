from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='NPS',
    page_icon='🗣️',
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
    combined_df = pd.concat([df_survey23, df_survey24, df_survey25], ignore_index=True)
    st.header('Net Promoter Score Overview', divider='rainbow')
    selected_filters = make_filter(columns_list, combined_df)

    filtered_data = combined_df.copy()
    for col, vals in selected_filters.items():
        filtered_data = filtered_data[filtered_data[col].isin(vals)]

    if filtered_data.empty:
        st.warning("No data available after applying filters.")
        st.stop()


    # ==============================
    # HITUNG NPS PER TAHUN
    # ==============================
    def calculate_nps(df):
        df['NPS'] = pd.to_numeric(df['NPS'], errors='coerce')
        total = df['NPS'].count()
        promoters = df[df['NPS'] >= 9].shape[0]
        passives = df[(df['NPS'] >= 7) & (df['NPS'] <= 8)].shape[0]
        detractors = df[df['NPS'] <= 6].shape[0]

        percent_promoters = (promoters / total) * 100 if total > 0 else 0
        percent_passives = (passives / total) * 100 if total > 0 else 0
        percent_detractors = (detractors / total) * 100 if total > 0 else 0
        nps = percent_promoters - percent_detractors
        return {
            'promoters': promoters,
            'passives': passives,
            'detractors': detractors,
            'percent_promoters': percent_promoters,
            'percent_passives': percent_passives,
            'percent_detractors': percent_detractors,
            'nps': nps,
            'total': total
        }

    results = {}
    for year in [2023, 2024, 2025]:
        df_year = filtered_data[filtered_data['year'] == year]
        results[year] = calculate_nps(df_year)

    # ==============================
    # BUAT DATAFRAME UNTUK VISUAL
    # ==============================
    nps_df = pd.DataFrame({
        'Year': [2023, 2024, 2025],
        'Detractors': [results[y]['percent_detractors'] for y in [2023, 2024, 2025]],
        'Passives': [results[y]['percent_passives'] for y in [2023, 2024, 2025]],
        'Promoters': [results[y]['percent_promoters'] for y in [2023, 2024, 2025]],
        'NPS': [results[y]['nps'] for y in [2023, 2024, 2025]]
    })

    # ==============================
    # STACKED BAR 100%
    # ==============================
    fig = go.Figure()

    # Detractors
    fig.add_trace(go.Bar(
        x=nps_df['Year'],
        y=nps_df['Detractors'],
        name='Detractors',
        marker_color='tomato',
        text=[f"{v:.1f}% ({results[y]['detractors']})" for y, v in zip(nps_df['Year'], nps_df['Detractors'])],
        textposition='inside'
    ))

    # Passives
    fig.add_trace(go.Bar(
        x=nps_df['Year'],
        y=nps_df['Passives'],
        name='Passives',
        marker_color='gold',
        text=[f"{v:.1f}% ({results[y]['passives']})" for y, v in zip(nps_df['Year'], nps_df['Passives'])],
        textposition='inside'
    ))

    # Promoters
    fig.add_trace(go.Bar(
        x=nps_df['Year'],
        y=nps_df['Promoters'],
        name='Promoters',
        marker_color='seagreen',
        text=[f"{v:.1f}% ({results[y]['promoters']})" for y, v in zip(nps_df['Year'], nps_df['Promoters'])],
        textposition='inside'
    ))

    # Tambahkan teks NPS% di atas setiap bar
    for year, nps_value in zip(nps_df['Year'], nps_df['NPS']):
        fig.add_annotation(
            x=year,
            y=105,
            text=f"<b>NPS: {nps_value:.1f}%</b>",
            showarrow=False,
            font=dict(size=14, color='black')
        )

    # Layout
    fig.update_layout(
        barmode='stack',
        title='NPS Breakdown by Year (100% Stacked)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Percentage', range=[0, 110]),
        legend_title_text='Category',
        height=600,
        template='simple_white'
    )

    st.plotly_chart(fig, use_container_width=True)
