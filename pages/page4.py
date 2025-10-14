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
        marker_color='beige',
        text=[f"{v:.1f}% ({results[y]['passives']})" for y, v in zip(nps_df['Year'], nps_df['Passives'])],
        textposition='inside'
    ))

    # Promoters
    fig.add_trace(go.Bar(
        x=nps_df['Year'],
        y=nps_df['Promoters'],
        name='Promoters',
        marker_color='cadetblue',
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
        title='NPS Breakdown by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Percentage', range=[0, 110]),
        legend_title_text='Category',
        height=400,
        template='simple_white'
    )

    st.plotly_chart(fig, use_container_width=True)
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
    # ==============================
    # 🎯STACKED BAR FOR FILTER
    # ==============================

    selected_filter = st.selectbox(
        "Select Filter",
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    year_options = ["2023", "2024", "2025"]
    selected_year = st.selectbox("Select Year to Display:", year_options, index=year_options.index("2025"))

    # Filter data berdasarkan tahun terpilih
    filtered_data = filtered_data[filtered_data['year'] == int(selected_year)]

    if selected_filter in filtered_data.columns:
        # Hanya ambil data yang punya NPS
        filtered_data = filtered_data.dropna(subset=['NPS'])
        filtered_data['NPS'] = pd.to_numeric(filtered_data['NPS'], errors='coerce')

        if filtered_data.empty:
            st.warning(f"No NPS data available for {selected_year}.")
        else:
            # --- Hitung jumlah & persentase tiap kategori NPS ---
            grouped = filtered_data.groupby(selected_filter).apply(lambda x: pd.Series({
                'Promoters': (x['NPS'] >= 9).mean() * 100,
                'Passives': ((x['NPS'] >= 7) & (x['NPS'] <= 8)).mean() * 100,
                'Detractors': (x['NPS'] <= 6).mean() * 100,
                'Promoters_Count': (x['NPS'] >= 9).sum(),
                'Passives_Count': ((x['NPS'] >= 7) & (x['NPS'] <= 8)).sum(),
                'Detractors_Count': (x['NPS'] <= 6).sum(),
            })).reset_index()

            # --- Confidentiality check (hapus kategori dengan total N=1) ---
            grouped['Total'] = grouped[['Promoters_Count', 'Passives_Count', 'Detractors_Count']].sum(axis=1)
            removed_rows = grouped[grouped['Total'] == 1][selected_filter].tolist()
            grouped = grouped[grouped['Total'] > 1]

            if len(removed_rows) > 0:
                st.info(f"Disclaimer: {len(removed_rows)} entry/entries in '{selected_filter.capitalize()}' were removed to protect confidentiality (N=1).")

            # --- Bentuk data long format ---
            stacked_data = grouped.melt(
                id_vars=[selected_filter],
                value_vars=['Promoters', 'Passives', 'Detractors'],
                var_name='NPS Category',
                value_name='Percentage'
            )

            stacked_counts = grouped.melt(
                id_vars=[selected_filter],
                value_vars=['Promoters_Count', 'Passives_Count', 'Detractors_Count'],
                var_name='NPS Category Count',
                value_name='Counts'
            )

            # Gabungkan count
            stacked_data['Counts'] = stacked_counts['Counts'].values

            # --- Warna kategori ---
            colors = {
                'Promoters': 'cadetblue',  
                'Passives': 'beige',   
                'Detractors': 'tomato' 
            }

            # --- Plot stacked bar ---
            fig_stacked = go.Figure()

            for category in ['Promoters', 'Passives', 'Detractors']:
                cat_data = stacked_data[stacked_data['NPS Category'] == category]
                fig_stacked.add_trace(go.Bar(
                    y=cat_data[selected_filter],
                    x=cat_data['Percentage'],
                    name=category,
                    orientation='h',
                    marker_color=colors[category],
                    text=cat_data.apply(lambda r: f"{r['Percentage']:.1f}%<br>({int(r['Counts'])})", axis=1),
                    textposition='inside'
                ))

            # --- Hitung skor NPS per kategori (Promoters - Detractors) ---
            grouped['NPS_Score'] = (grouped['Promoters'] - grouped['Detractors']).round(1)

            # --- Tambahkan annotation NPS di kanan bar ---
            for _, row in grouped.iterrows():
                fig_stacked.add_annotation(
                    x=105,
                    y=row[selected_filter],
                    text=f"{row['NPS_Score']}%",
                    showarrow=False,
                    font=dict(size=14, color="grey"),
                    align="left"
                )

            # --- Layout ---
            fig_stacked.update_layout(
                title=f"NPS Breakdown by {selected_filter.title()} ({selected_year})",
                xaxis_title="Percentage (%)",
                yaxis_title=selected_filter.title(),
                xaxis=dict(range=[0, 110]),
                barmode='stack',
                height=700,
                legend_title_text="NPS Category",
                template='simple_white'
            )

            st.plotly_chart(fig_stacked, use_container_width=True)


    # ==============================
    # 📊 TABEL PERBANDINGAN NPS (2024 vs 2025)
    # ==============================
    st.divider()
    st.markdown("##### 📋 NPS Comparison Table (2024 vs 2025)")

    # --- Ambil data dari combined_df, tapi tetap respect filter user ---
    nps_compare = combined_df.copy()

    # Terapkan filter yang sama seperti di grafik
    for col, vals in selected_filters.items():
        if col in nps_compare.columns:
            nps_compare = nps_compare[nps_compare[col].isin(vals)]

    # Hanya ambil tahun 2024 & 2025, dan data dengan NPS valid
    nps_compare = nps_compare[nps_compare['year'].isin([2024, 2025])]
    nps_compare = nps_compare.dropna(subset=['NPS'])
    nps_compare['NPS'] = pd.to_numeric(nps_compare['NPS'], errors='coerce')

    if nps_compare.empty:
        st.warning("No NPS data available for 2024 and 2025 after applying filters.")
    else:
        # --- Hitung NPS summary per demografi & tahun ---
        def calc_nps_summary(df):
            return pd.Series({
                'Detractors': (df['NPS'] <= 6).mean() * 100,
                'Promoters': (df['NPS'] >= 9).mean() * 100,
                'NPS': ((df['NPS'] >= 9).mean() - (df['NPS'] <= 6).mean()) * 100
            })

        summary = nps_compare.groupby([selected_filter, 'year'], dropna=False).apply(calc_nps_summary).reset_index()

        # --- Pisahkan data 2024 & 2025 ---
        summary_2024 = summary[summary['year'] == 2024].drop(columns=['year'])
        summary_2025 = summary[summary['year'] == 2025].drop(columns=['year'])

        # --- Gabungkan berdasarkan demografi ---
        comparison_df = pd.merge(summary_2024, summary_2025, on=selected_filter, suffixes=('_2024', '_2025'), how='outer')

        # --- Hitung perubahan NPS ---
        comparison_df['Perubahan NPS (%)'] = (comparison_df['NPS_2025'] - comparison_df['NPS_2024']).round(1)

        # --- Urutkan kolom biar rapi ---
        ordered_cols = [
            selected_filter,
            'Detractors_2024', 'Promoters_2024', 'NPS_2024',
            'Detractors_2025', 'Promoters_2025', 'NPS_2025',
            'Perubahan NPS (%)'
        ]
        comparison_df = comparison_df[[c for c in ordered_cols if c in comparison_df.columns]]

        # --- Bulatkan angka ke 1 desimal ---
        numeric_cols = ['Detractors_2024', 'Promoters_2024', 'NPS_2024',
                        'Detractors_2025', 'Promoters_2025', 'NPS_2025']
        for col in numeric_cols:
            if col in comparison_df.columns:
                comparison_df[col] = comparison_df[col].round(1)

        # --- Format kolom perubahan jadi string dan simpan nilai float untuk warna ---
        comparison_df['Change_Value'] = comparison_df['Perubahan NPS (%)']
        comparison_df['Perubahan NPS (%)'] = comparison_df['Change_Value'].apply(
            lambda v: f"{v:+.1f}% ↑" if v > 0 else (f"{v:+.1f}% ↓" if v < 0 else f"{v:+.1f}% →")
            if pd.notna(v) else "-"
        )

        # --- Styling warna untuk naik/turun ---
        def color_change(val):
            if isinstance(val, str):
                if '↑' in val:
                    return 'color: #228B22; font-weight: 600;'  # hijau
                elif '↓' in val:
                    return 'color: #B22222; font-weight: 600;'  # merah
                elif '→' in val:
                    return 'color: grey; font-weight: 600;'
            return ''

        # --- Terapkan style ---
        styled_df = (
            comparison_df
            .drop(columns=['Change_Value'])
            .style
            .applymap(color_change, subset=['Perubahan NPS (%)'])
            .format({col: "{:.1f}" for col in numeric_cols})
        )

        # --- Tampilkan dataframe dengan warna interaktif ---
        st.dataframe(styled_df, use_container_width=True)


