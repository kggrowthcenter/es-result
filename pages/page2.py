from navigation import make_sidebar, make_filter
import streamlit as st
from data_processing import finalize_data
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Set up page configuration
st.set_page_config(
    page_title='Mood Meter',
    page_icon=':😊:', 
)

make_sidebar()

# Load data
df_survey25, df_survey24, df_survey23, df_creds = finalize_data()

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
    df_survey25 = df_survey25[df_survey25['subunit'].isin(user_units)]
    df_survey24 = df_survey24[df_survey24['subunit'].isin(user_units)]
    df_survey23 = df_survey23[df_survey23['subunit'].isin(user_units)]

    # Subheader for the Mood Meter
    st.header('Mood Meter Overview', divider='rainbow')

    # Apply the filter from make_filter (use the filter returned by make_filter)
    filtered_data, selected_filters = make_filter(columns_list, df_survey)
    total_participants = filtered_data['nik'].nunique()

    # Calculate the count of unique 'nik' for each mood level (1-8)
    mood_counts = filtered_data.groupby('EMO')['nik'].nunique().reindex(range(1, 9), fill_value=0)

    # Create a DataFrame for the mood counts
    mood_table = pd.DataFrame({
        'Mood Level': mood_counts.index,
        'User': mood_counts.values,
    })

    # Define emoticons and descriptions for each mood level
    emoticons = ['😭', '😞', '😐', '😠', '😄', '😁', '🤩', '😍']
    keterangan = ['Sedih', 'Kesepian', 'Tertekan', 'Marah', 'Senang', 'Bermakna', 'Tenteram', 'Tenang']

    # Add emoticons and descriptions to the mood_table DataFrame
    mood_table['Emoticon'] = [emoticons[mood - 1] for mood in mood_table['Mood Level']]
    mood_table['Description'] = [keterangan[mood - 1] for mood in mood_table['Mood Level']]

    # Create the bar chart using Plotly
    fig = go.Figure()

    mood_colors = ['#8B0000', '#CD5C5C', '#FFA07A', '#FFE4B5', '#FFD700', '#ADFF2F', '#00BFFF', '#00008B']

    fig.add_trace(go.Bar(
        x=mood_table['Description'],
        y=mood_table['User'],
        text=[
            f"{emo} {user} ({user / total_participants * 100:.1f}%)" 
            for emo, user in zip(mood_table['Emoticon'], mood_table['User'])
        ],
        textposition="outside",
        marker=dict(color=mood_colors),
        hovertemplate="<b>%{x}</b><br>Emoticon: %{text}<br>User Count: %{y}<extra></extra>"  # Tooltip
    ))

    # Update layout for title, axis labels, and colors
    fig.update_layout(
        title="Mood Level Overview",
        xaxis_title="Mood Description",
        yaxis_title="User Count",
        yaxis=dict(tickformat=".0f"),
        template="presentation"
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    # Filter selection for the additional chart
    unit_column = st.selectbox(
        'Select the column to compare mood meter by:',
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    # Filter and prepare the data
    filtered_df = filtered_data.dropna(subset=['EMO', unit_column])

    # Count occurrences of each mood level per category and calculate the percentage
    mood_counts = filtered_df.groupby([unit_column, 'EMO']).size().unstack(fill_value=0)

    # Confidentiality check: Store original size before filtering
    original_size = mood_counts.shape[0]

    # Confidentiality check: Remove rows where N=1
    mood_counts = mood_counts[mood_counts.sum(axis=1) > 1]

    # Calculate the number of rows removed
    rows_removed = original_size - mood_counts.shape[0]

    # If any rows were removed, show the disclaimer
    if rows_removed > 0:
        st.write(f"Disclaimer: {rows_removed} entry/entries in the '{unit_column.capitalize()}' column were removed to protect confidentiality (N=1).")

    # Ensure all score columns exist
    if 1 not in mood_counts:
        mood_counts[1] = 0
    if 2 not in mood_counts:
        mood_counts[2] = 0
    if 3 not in mood_counts:
        mood_counts[3] = 0
    if 4 not in mood_counts:
        mood_counts[4] = 0
    if 5 not in mood_counts:
        mood_counts[5] = 0
    if 6 not in mood_counts:
        mood_counts[6] = 0
    if 7 not in mood_counts:
        mood_counts[7] = 0
    if 8 not in mood_counts:
        mood_counts[8] = 0

    # Convert the index back to a column so it can be used as `id_vars` in the melt operation
    mood_counts = mood_counts.reset_index()

    # Ensure the correct order of columns before renaming
    mood_counts = mood_counts[[unit_column, 1, 2, 3, 4, 5, 6, 7, 8]]

    # Transform data for Altair: Melt the DataFrame into long format
    mood_counts = mood_counts.melt(
        id_vars=unit_column,          # The unit column now reset as a regular column
        value_vars=[1, 2, 3, 4, 5, 6, 7, 8],  # The EMO columns to melt
        var_name='EMO',               # New column name for the EMO values
        value_name='count'            # New column name for the counts
    )

    mood_total = mood_counts.groupby(unit_column)['count'].transform('sum')
    mood_counts['percentage'] = (mood_counts['count'] / mood_total) * 100

    mood_colors = ['#8B0000', '#CD5C5C', '#FFA07A', '#FFE4B5', '#FFD700', '#ADFF2F', '#00BFFF', '#00008B']

    # Create a figure with each mood level as a trace to enable custom text labels
    fig = go.Figure()

    for mood_level in sorted(mood_counts['EMO'].unique()):
        mood_data = mood_counts[mood_counts['EMO'] == mood_level]
        fig.add_trace(
            go.Bar(
                x=mood_data['percentage'],
                y=mood_data[unit_column],
                name=keterangan[mood_level - 1],
                orientation='h',
                text = mood_data.apply(lambda row: f"{row['percentage']:.1f}%\n({row['count']})", axis=1),
                textposition='inside',
                marker=dict(color=mood_colors[mood_level - 1]),
                hoverinfo='name+x+y'
            )
        )

    # Update layout for the stacked bar chart
    fig.update_layout(
        title_text=f'Mood Level Distribution by {unit_column.capitalize()}',
        xaxis_title='Percentage (%)',
        yaxis_title=unit_column.capitalize(),
        barmode='stack',
        template='presentation',
        width=1000,
        height=1000 
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
