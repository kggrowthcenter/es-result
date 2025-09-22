import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import pandas as pd


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    with st.sidebar:
        st.title(":blue_heart: KG Survey Result 2024")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/page1.py", label="Demography", icon="🌎")
            st.page_link("pages/page2.py", label="Mood Meter", icon="😊")
            st.page_link("pages/page3.py", label="Satisfaction", icon="👍")
            st.page_link("pages/page4.py", label="NPS", icon="🗣️")
            st.page_link("pages/page5.py", label="Categorization", icon="🤝")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "streamlit_app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("streamlit_app.py")


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("streamlit_app.py")

def make_filter(columns_list, df_survey):
    # Allow the user to select multiple filter columns (unit, subunit, etc.)
    filter_columns = st.multiselect(
        'Filter the data (optional):',
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    # Check if 'layer' is selected
    if 'layer' in filter_columns:
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

    # Initialize the filtered data as the original DataFrame
    filtered_data = df_survey.copy()

    # List to store selected filter values for display in the subheader
    selected_filters = []

    # Display filter options for each selected filter column
    for filter_col in filter_columns:
        selected_filter_value = st.multiselect(
            f'Select {filter_col.capitalize()} to filter the data:',
            options=filtered_data[filter_col].unique(),
            key=f'filter_{filter_col}'  # Unique key for each filter selectbox
        )
        
        # Check if any values are selected for this filter
        if selected_filter_value:
            # Filter the data to include only rows where the column value is in the selected values
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_filter_value)]
            
            # Add the selected filter values to the list for subheader display
            selected_filters.append(f"{filter_col.capitalize()}: {', '.join(selected_filter_value)}")

    # Confidentiality check: return empty DataFrame if filtered data has only 1 record
    if filtered_data.shape[0] <= 1:
        st.write("Data is unavailable to protect confidentiality.")
        return pd.DataFrame(), selected_filters  # Return an empty DataFrame and the selected filters
    
    return filtered_data, selected_filters
