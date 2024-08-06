import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from calendar import month_abbr

# Set up your database connection
conn = st.connection('mysql', type='sql')

# Set the title that appears at the top of the page
st.title('Worker Assessment and Countermeasures Dashboard')

# Monthly Worker Assessment Count
st.subheader("Monthly Worker Assessment Count")

# Call the stored procedure for monthly assessment count
monthly_assessment_df = conn.query('''
    SELECT 
        DATE_FORMAT(created_dt, '%Y-%m') as month,
        COUNT(*) as assessment_count
    FROM 
        t_worker_assessment
    WHERE 
        created_dt >= '2024-04-01' AND created_dt <= '2024-08-31'
    GROUP BY 
        DATE_FORMAT(created_dt, '%Y-%m')
    ORDER BY 
        month
''', ttl=600)

# Convert month to datetime for proper ordering
monthly_assessment_df['month'] = pd.to_datetime(monthly_assessment_df['month'])

# Find the month with the highest number of assessments
max_assessment_month = monthly_assessment_df.loc[monthly_assessment_df['assessment_count'].idxmax()]

# Create two columns for metrics
col1, col2 = st.columns(2)

# Display the highest number of assessments
with col1:
    st.metric("Highest Number of Assessments", max_assessment_month['assessment_count'])

# Display the month it was achieved
with col2:
    st.metric("Achieved In", max_assessment_month['month'].strftime('%B %Y'))

# Create the line chart for monthly assessment count
fig_monthly_assessment = go.Figure()

# Add the line trace
fig_monthly_assessment.add_trace(go.Scatter(
    x=monthly_assessment_df['month'],
    y=monthly_assessment_df['assessment_count'],
    mode='lines+markers',
    name='Monthly Assessments',
    line=dict(color='black'),
    marker=dict(size=8)
))

# Add the star marker for the highest count
fig_monthly_assessment.add_trace(go.Scatter(
    x=[max_assessment_month['month']],
    y=[max_assessment_month['assessment_count']],
    mode='markers',
    name='Highest Count',
    marker=dict(symbol='star', size=16, color='green'),
    showlegend=False
))

fig_monthly_assessment.update_layout(
    title='Monthly Worker Assessment Count',
    xaxis_title='Month',
    yaxis_title='Number of Assessments',
    xaxis=dict(
        tickmode='array',
        tickvals=monthly_assessment_df['month'],
        ticktext=[month_abbr[date.month] for date in monthly_assessment_df['month']],
    ),
    hovermode='x unified'
)

# Display the monthly assessment chart
st.plotly_chart(fig_monthly_assessment, use_container_width=True)

# Add a horizontal line for visual separation
st.markdown("---")

# Popular Countermeasures (keep this part as it was)
st.subheader("Popular Countermeasures")

# Call the stored procedure for popular countermeasures
countermeasures_df = conn.query('CALL getCountermeasuresData()', ttl=600)

# Create the pie chart for popular countermeasures
fig_countermeasures = go.Figure(data=[go.Pie(
    labels=countermeasures_df['countermeasure_text'],
    values=countermeasures_df['percentage'],
    hole=.3,
    hoverinfo='label+percent',
    textinfo='value'
)])

fig_countermeasures.update_layout(
    title='Popular Countermeasures',
)

# Display the countermeasures pie chart
st.plotly_chart(fig_countermeasures, use_container_width=True)

# Display the countermeasures data table
st.write("Countermeasures Data")
display_df = countermeasures_df[['countermeasure_text', 'count', 'percentage']]
st.dataframe(display_df.style.format({
    'count': '{:,.0f}',
    'percentage': '{:.2f}%'
}), height=300)

# Add a horizontal line for visual separation
st.markdown("---")

st.subheader("Causes of Fatigue")

# Call the stored procedure for fatigue causes count
fatigue_causes_df = conn.query('CALL getCausesOfFatigueCount()', ttl=600)

# Create the bar chart for fatigue causes
fig_fatigue_causes = go.Figure(data=[go.Bar(
    x=fatigue_causes_df['fatigue_cause'],
    y=fatigue_causes_df['count'],
    text=fatigue_causes_df['count'],
    textposition='auto',
    marker_color='darkgreen'  # You can change this color as needed
)])

fig_fatigue_causes.update_layout(
    title={
        'text': 'Causes of Fatigue',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='Cause of Fatigue',
    yaxis_title='Count',
    hovermode='x unified',
    height=500,  # Adjust the height as needed
    margin=dict(l=50, r=50, t=80, b=50)
)

# Improve readability of x-axis labels
fig_fatigue_causes.update_xaxes(tickangle=-45, tickfont=dict(size=10))

# Display the fatigue causes chart
st.plotly_chart(fig_fatigue_causes, use_container_width=True)

# Optionally, display the fatigue causes data table
st.write("Fatigue Causes Data")
st.dataframe(fatigue_causes_df.style.format({
    'count': '{:,.0f}'
}), height=200)