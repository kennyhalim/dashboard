# import streamlit as st
# import pandas as pd
# import math
# import numpy as np
# from pathlib import Path
# from datetime import datetime

# # Set the title and favicon that appear in the Browser's tab bar.
# st.set_page_config(
#     page_title='Tenvos-Novachem Dashboard',
#     page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
# )

# # -----------------------------------------------------------------------------


# # -----------------------------------------------------------------------------
# # Draw the actual page

# # Set the title that appears at the top of the page.
# '''
# # :earth_americas: Tenvos-Novachem Dashboard
# '''

# conn = st.connection('mysql', type='sql')
# df = conn.query('CALL getDailyReport()', ttl=600)

# date_obj = df['Checkin_DateTime'].iloc[0]
# formatted_date = date_obj.strftime("%m/%d/%Y")

# st.header(f"Data for {formatted_date}")
# '''
# '''
# '''
# '''


# # Count the number of recordings for each employee
# recording_counts = df.groupby(['employee_id', 'first_name', 'last_name'])['recording_id'].count().reset_index()
# recording_counts.columns = ['employee_id', 'first_name', 'last_name', 'recording_count']

# # Create a full name column
# recording_counts['full_name'] = recording_counts['first_name'] + ' ' + recording_counts['last_name']

# # Set the full name as the index
# recording_counts.set_index('full_name', inplace=True)

# # Sort the DataFrame by recording count in descending order
# recording_counts = recording_counts.sort_values('recording_count', ascending=False)

# # Create and display the line chart
# st.line_chart(
#     data=recording_counts,
#     y='recording_count',
#     x_label='Employee Name',
#     y_label='Number of Recordings',
#     color='#FF0000',
#     use_container_width=True
# )

# total_checkins = len(df)
# preshift_checkins = df['PRESHIFT'].sum()
# postshift_checkins = df['POSTSHIFT'].sum()

# order = ['Total', 'Pre-shift', 'Post-shift']

# chart_data = pd.DataFrame({
#     'Check-in Type': pd.Categorical(order, categories=order, ordered=True),
#     'Count': [total_checkins, preshift_checkins, postshift_checkins]
# })

# # Set 'Check-in Type' as the index
# chart_data.set_index('Check-in Type', inplace=True)

# # Create and display the line chart
# st.bar_chart(
#     data=chart_data,
#     y='Count',
#     x_label='Check-in Type',
#     y_label='Number of Check-ins',
#     use_container_width=True
# )

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Assuming your connection is already set up
conn = st.connection('mysql', type='sql')

# Fetch data for a longer period
df = conn.query('CALL dashboardReport()', ttl=600)

# Convert Checkin_DateTime to datetime if it's not already
df['Checkin_DateTime'] = pd.to_datetime(df['Checkin_DateTime'])

# Function to determine the shift date
def get_shift_date(row):
    # Assuming shifts starting before 4 AM belong to the previous day
    if row['Checkin_DateTime'].hour < 4:
        return row['Checkin_DateTime'].date() - timedelta(days=1)
    return row['Checkin_DateTime'].date()

# Apply the function to create a new 'Shift_Date' column
df['Shift_Date'] = df.apply(get_shift_date, axis=1)

# Group by Shift_Date and calculate daily totals
daily_totals = df.groupby('Shift_Date').agg({
    'recording_id': 'count',
    'PRESHIFT': 'sum',
    'POSTSHIFT': 'sum'
}).reset_index()

daily_totals.columns = ['Shift_Date', 'Total_Checkins', 'Pre_Shift_Checkins', 'Post_Shift_Checkins']

# Sort by date
daily_totals = daily_totals.sort_values('Shift_Date')

# Create shift labels
shift_labels = [f"Shift {i+1}<br>{date.strftime('%m-%d-%y')}" for i, date in enumerate(daily_totals['Shift_Date'])]

# Create the line chart using Plotly
fig = go.Figure()

fig.add_trace(go.Scatter(x=shift_labels, y=daily_totals['Total_Checkins'],
                         mode='lines+markers', name='Total Check-ins'))
fig.add_trace(go.Scatter(x=shift_labels, y=daily_totals['Pre_Shift_Checkins'],
                         mode='lines+markers', name='Pre-Shift Check-ins'))
fig.add_trace(go.Scatter(x=shift_labels, y=daily_totals['Post_Shift_Checkins'],
                         mode='lines+markers', name='Post-Shift Check-ins'))

fig.update_layout(
    title='Daily Check-ins by Shift',
    xaxis_title='Shift',
    yaxis_title='Number of Check-ins',
    legend_title='Check-in Type',
    hovermode='x unified',
    xaxis=dict(tickangle=-45)
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

# Display the data table
st.write(daily_totals)