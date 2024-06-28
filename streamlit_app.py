import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path
from datetime import datetime

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Tenvos-Novachem Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: Tenvos-Novachem Dashboard
'''

conn = st.connection('mysql', type='sql')
df = conn.query('CALL getDailyReport()', ttl=600)

date_obj = df['Checkin_DateTime'].iloc[0]
formatted_date = date_obj.strftime("%m/%d/%Y")

st.header(f"Data for {formatted_date}")
'''
'''
'''
'''


# Count the number of recordings for each employee
recording_counts = df.groupby(['employee_id', 'first_name', 'last_name'])['recording_id'].count().reset_index()
recording_counts.columns = ['employee_id', 'first_name', 'last_name', 'recording_count']

# Create a full name column
recording_counts['full_name'] = recording_counts['first_name'] + ' ' + recording_counts['last_name']

# Set the full name as the index
recording_counts.set_index('full_name', inplace=True)

# Sort the DataFrame by recording count in descending order
recording_counts = recording_counts.sort_values('recording_count', ascending=False)

# Create and display the line chart
st.line_chart(
    data=recording_counts,
    y='recording_count',
    x_label='Employee Name',
    y_label='Number of Recordings',
    color='#FF0000',
    use_container_width=True
)

total_checkins = len(df)
preshift_checkins = df['PRESHIFT'].sum()
postshift_checkins = df['POSTSHIFT'].sum()

order = ['Total', 'Pre-shift', 'Post-shift']

chart_data = pd.DataFrame({
    'Check-in Type': pd.Categorical(order, categories=order, ordered=True),
    'Count': [total_checkins, preshift_checkins, postshift_checkins]
})

# Set 'Check-in Type' as the index
chart_data.set_index('Check-in Type', inplace=True)

# Create and display the line chart
st.bar_chart(
    data=chart_data,
    y='Count',
    x_label='Check-in Type',
    y_label='Number of Check-ins',
    use_container_width=True
)
