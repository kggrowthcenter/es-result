import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
from data_processing import finalize_data
from navigation import make_sidebar, make_filter

# Streamlit page setup
st.set_page_config(page_title='Statistical Analysis', page_icon='📊')
make_sidebar()

# Load data
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]
    df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]
    df_survey23 = df_survey23[df_survey23['subunit'].isin(user_units)]

    df_all = {
        "2025": df_survey25,
        "2024": df_survey24,
        "2023": df_survey23
    }

    st.header('Statistical Analysis', divider='rainbow')

    # --- Apply Filter (like Categorization page) ---
    # --- Year selection ---
    selected_year = st.selectbox("Select survey year:", options=list(df_all.keys()), index=0)
    df = df_all[selected_year].copy()
    df = df[df['submit_date'].notna() & (df['submit_date'] != "")]

    columns_list = [
        'unit', 'subunit', 'directorate', 'division', 'department', 'section',
        'layer', 'status', 'generation', 'gender', 'marital', 'education',
        'tenure_category', 'children', 'region', 'participation_23'
    ]

    selected_filters = make_filter(columns_list, df, key_prefix="corr_filter")

    st.write(f"Data shape after filter: {df.shape[0]} rows × {df.shape[1]} columns")

    # ======================================================
    # SECTION 1 — CORRELATION TEST (MULTIPLE VARIABLES)
    # ======================================================
    st.subheader("🔗 Correlation Test (Multiple Variables)", divider='gray')
    

    # Get numeric columns, but exclude ID-like or irrelevant ones
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    exclude_cols = ['nik', 'tenure']  # add any others as needed
    numeric_cols = [c for c in numeric_cols if c.lower() not in [e.lower() for e in exclude_cols]]


    # Define satisfaction variables
    satisfaction_columns = [
        'SAT', 'NPS', 'EMO', 'average_kd', 'average_ki', 'average_kr',
        'average_pr', 'average_tu', 'average_ke'
    ]
    satisfaction_columns_item = [
        'SAT', 'NPS', 'EMO',
        'KD0', 'KD1', 'KD2', 'KD3', 'KE0', 'KE1', 'KE2', 'KE3',
        'KI0', 'KI1', 'KI2', 'KI3', 'KI4', 'KI5',
        'KR0', 'KR1', 'KR2', 'KR3', 'KR4', 'KR5',
        'PR0', 'PR1', 'PR2',
        'TU0', 'TU1', 'TU2', 'TU3'
    ]

    # Filter only existing columns
    satisfaction_columns = [c for c in satisfaction_columns if c in df.columns]
    satisfaction_columns_item = [c for c in satisfaction_columns_item if c in df.columns]

    if len(numeric_cols) < 2:
        st.warning("Not enough numeric columns for correlation test.")
    else:
        # Buttons to quickly fill multiselect
        col1, col2, col3 = st.columns(3)
        with col1:
            use_all_items = st.button("Select All Satisfaction Items")
        with col2:
            use_all_dimensions = st.button("Select All Dimensions")
        with col3:
            clear_selection = st.button("Clear Selection")

        # Initialize session state for persistent selection
        if "selected_vars" not in st.session_state:
            st.session_state.selected_vars = []

        # Handle button actions
        if use_all_items:
            st.session_state.selected_vars = satisfaction_columns_item
        elif use_all_dimensions:
            st.session_state.selected_vars = satisfaction_columns
        elif clear_selection:
            st.session_state.selected_vars = []

        # Multiselect always visible
        selected_vars = st.multiselect(
            "Select numeric variables to test correlation:",
            options=numeric_cols,
            default=st.session_state.selected_vars,
            key="corr_multiselect"
        )

        # Run correlation
        if len(selected_vars) < 2:
            st.info("Please select at least two variables to calculate correlations.")
        else:
            corr_matrix = df[selected_vars].corr(method='pearson').round(3)
            st.write("### 📊 Correlation Matrix")
            st.dataframe(corr_matrix)

            # Heatmap visualization
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1,
                title=f"Correlation Heatmap ({selected_year})"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Pairwise significance test
            st.markdown("### 🧪 Significance Test (Pairwise)")
            results = []
            for i in range(len(selected_vars)):
                for j in range(i + 1, len(selected_vars)):
                    x = df[selected_vars[i]].dropna()
                    y = df[selected_vars[j]].dropna()
                    common_idx = x.index.intersection(y.index)
                    x, y = x.loc[common_idx], y.loc[common_idx]
                    if len(x) > 2:
                        r, p = stats.pearsonr(x, y)
                        results.append({
                            "Var1": selected_vars[i],
                            "Var2": selected_vars[j],
                            "r": round(r, 3),
                            "p-value": round(p, 4),
                            "Significant (p<0.05)": "✅" if p < 0.05 else "–"
                        })
            st.dataframe(pd.DataFrame(results))

    # ======================================================
    # SECTION 2 — MEAN DIFFERENCE TEST
    # ======================================================
    st.subheader("📈 Mean Difference Test", divider='gray')

    # Exclude ID-like or irrelevant numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    exclude_cols = ['nik', 'tenure', 'serial', 'id', 'employee_id']
    numeric_cols = [c for c in numeric_cols if c.lower() not in [e.lower() for e in exclude_cols]]

    # Get categorical columns for grouping
    group_cols = df.select_dtypes(exclude=np.number).columns.tolist() + ["tenure_category", "layer", "year"]
    group_cols = sorted(list(set(group_cols)))  # remove duplicates & sort

    if len(numeric_cols) == 0 or len(group_cols) == 0:
        st.warning("Not enough variables for mean difference test.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            numeric_var = st.selectbox("Select numeric variable:", numeric_cols)
        with col2:
            group_var = st.selectbox("Select grouping variable:", group_cols)

        # --- Let user choose specific groups from selected variable
        available_groups = sorted(df[group_var].dropna().unique().tolist())
        selected_groups = st.multiselect(
            f"Select which {group_var} groups to include:",
            options=available_groups,
            default=[]
        )

        df_clean = df[df[group_var].isin(selected_groups)][[numeric_var, group_var]].dropna()

        # --- Optional: compare between years
        compare_years = st.checkbox("Enable year comparison (2023–2025)")
        if compare_years:
            years_selected = st.multiselect(
                "Select years to compare:",
                options=list(df_all.keys()),
                default=["2024", "2025"]
            )

        # --- Run test button
        if st.button("Run Mean Difference Test"):
            if compare_years and len(years_selected) >= 2:
                # Combine selected years
                df_combined = []
                for y in years_selected:
                    d = df_all[y][['year', numeric_var]].copy()
                    d = d[d[numeric_var].notna()]
                    df_combined.append(d)
                df_combined = pd.concat(df_combined)

                st.write(f"**Comparing {numeric_var} between years: {', '.join(years_selected)}**")

                # T-test if only 2 years, else ANOVA
                unique_years = df_combined['year'].unique()
                if len(unique_years) == 2:
                    y1, y2 = unique_years
                    data1 = df_combined[df_combined['year'] == y1][numeric_var]
                    data2 = df_combined[df_combined['year'] == y2][numeric_var]
                    t_stat, pval = stats.ttest_ind(data1, data2, equal_var=False)
                    cohen_d = (data1.mean() - data2.mean()) / np.sqrt(((data1.std() ** 2) + (data2.std() ** 2)) / 2)
                    interpretation = (
                        "small" if abs(cohen_d) < 0.3 else
                        "medium" if abs(cohen_d) < 0.5 else
                        "large"
                    )
                    st.markdown(f"""
                    **T-test result:**  
                    • t = {t_stat:.3f}, p = {pval:.4f}  
                    • Mean ({y1}) = {data1.mean():.2f}, SD = {data1.std():.2f}  
                    • Mean ({y2}) = {data2.mean():.2f}, SD = {data2.std():.2f}  
                    • Effect size (Cohen’s d) = {cohen_d:.3f} → *{interpretation} effect*
                    """)
                    st.info("✅ Significant difference" if pval < 0.05 else "⚪ No significant difference")
                else:
                    group_data = [df_combined[df_combined['year'] == y][numeric_var] for y in unique_years]
                    f_stat, pval = stats.f_oneway(*group_data)
                    st.write(f"**ANOVA result:** F = {f_stat:.3f}, p = {pval:.4f}")
                    st.info("✅ Significant difference among years" if pval < 0.05 else "⚪ No significant difference among years")

            else:
                # --- Within selected dataset, by group_var and selected groups
                n_groups = len(selected_groups)
                st.write(f"**Number of groups:** {n_groups}")

                if n_groups < 2:
                    st.warning("Need at least 2 groups for comparison.")
                else:
                    group_stats = df_clean.groupby(group_var)[numeric_var].agg(['mean', 'std', 'count']).reset_index()
                    st.markdown("### 📊 Group Summary (Mean ± SD)")
                    st.dataframe(group_stats.style.format({'mean': '{:.2f}', 'std': '{:.2f}'}))

                    if n_groups == 2:
                        g1, g2 = selected_groups
                        data1 = df_clean[df_clean[group_var] == g1][numeric_var]
                        data2 = df_clean[df_clean[group_var] == g2][numeric_var]
                        t_stat, pval = stats.ttest_ind(data1, data2, equal_var=False)
                        cohen_d = (data1.mean() - data2.mean()) / np.sqrt(((data1.std() ** 2) + (data2.std() ** 2)) / 2)
                        interpretation = (
                            "small" if abs(cohen_d) < 0.3 else
                            "medium" if abs(cohen_d) < 0.5 else
                            "large"
                        )
                        st.markdown(f"""
                        **T-test result:**  
                        • t = {t_stat:.3f}, p = {pval:.4f}  
                        • Mean ({g1}) = {data1.mean():.2f}, SD = {data1.std():.2f}  
                        • Mean ({g2}) = {data2.mean():.2f}, SD = {data2.std():.2f}  
                        • Effect size (Cohen’s d) = {cohen_d:.3f} → *{interpretation} effect*
                        """)
                        st.info("✅ Significant difference" if pval < 0.05 else "⚪ No significant difference")
                    else:
                        group_data = [df_clean[df_clean[group_var] == g][numeric_var] for g in selected_groups]
                        f_stat, pval = stats.f_oneway(*group_data)
                        st.markdown(f"""
                        **ANOVA result:**  
                        • F = {f_stat:.3f}, p = {pval:.4f}  
                        • Based on {n_groups} groups: {', '.join(selected_groups)}
                        """)
                        st.info("✅ Significant difference among groups" if pval < 0.05 else "⚪ No significant difference among groups")


else:
    st.warning("You are not authenticated — please log in to view this page.")
