import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from calendar import month_abbr

conn = st.connection('mysql', type='sql')

st.title('Worker Assessment and Countermeasures Dashboard')

st.subheader("Monthly Worker Assessment Count")

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

monthly_assessment_df['month'] = pd.to_datetime(monthly_assessment_df['month'])

max_assessment_month = monthly_assessment_df.loc[monthly_assessment_df['assessment_count'].idxmax()]

col1, col2 = st.columns(2)

with col1:
    st.metric("Highest Number of Assessments", max_assessment_month['assessment_count'])

with col2:
    st.metric("Achieved In", max_assessment_month['month'].strftime('%B %Y'))

fig_monthly_assessment = go.Figure()

fig_monthly_assessment.add_trace(go.Scatter(
    x=monthly_assessment_df['month'],
    y=monthly_assessment_df['assessment_count'],
    mode='lines+markers',
    name='Monthly Assessments',
    line=dict(color='black'),
    marker=dict(size=8)
))

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

st.plotly_chart(fig_monthly_assessment, use_container_width=True)

st.markdown("---")

st.subheader("Popular Countermeasures")

countermeasures_df = conn.query('CALL getCountermeasuresData()', ttl=600)

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

st.plotly_chart(fig_countermeasures, use_container_width=True)

# st.write("Countermeasures Data")
# display_df = countermeasures_df[['countermeasure_text', 'count', 'percentage']]
# st.dataframe(display_df.style.format({
#     'count': '{:,.0f}',
#     'percentage': '{:.2f}%'
# }), height=300)

st.markdown("---")

st.subheader("Causes of Fatigue")

fatigue_causes_df = conn.query('CALL getCausesOfFatigueCount()', ttl=600)

fig_fatigue_causes = go.Figure(data=[go.Bar(
    x=fatigue_causes_df['fatigue_cause'],
    y=fatigue_causes_df['count'],
    text=fatigue_causes_df['count'],
    textposition='auto',
    marker_color='darkgreen'
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
    height=500,
    margin=dict(l=50, r=50, t=80, b=50)
)

fig_fatigue_causes.update_xaxes(tickangle=-45, tickfont=dict(size=10))

st.plotly_chart(fig_fatigue_causes, use_container_width=True)

# st.write("Fatigue Causes Data")
# st.dataframe(fatigue_causes_df.style.format({
#     'count': '{:,.0f}'
# }), height=200)

#one pie chart for severity

#bar chart
st.markdown("---")

st.subheader("Assessment Severity")

#fetch sql data
worker_assessment_df = conn.query('''
    SELECT 
        question_one_answer, question_two_answer, question_three_answer,
        question_four_answer, question_five_answer, question_six_answer
    FROM 
        t_worker_assessment
''', ttl=600)

def determine_severity(row):
    if row['question_six_answer'] == 1:
        return 'Red'
    elif row['question_five_answer'] == 1:
        return 'Orange'
    elif row['question_four_answer'] == 1:
        return 'Yellow'
    elif row['question_one_answer'] == 1 or row['question_two_answer'] == 1 or row['question_three_answer'] == 1:
        return 'Green'
    else:
        return 'Green'

worker_assessment_df['severity'] = worker_assessment_df.apply(determine_severity, axis=1)

#count occurrences of each severity
severity_counts = worker_assessment_df['severity'].value_counts()

#create pie chart for severity
fig_severity = go.Figure(data=[go.Pie(
    labels=severity_counts.index,
    values=severity_counts.values,
    hole=.3,
    hoverinfo='label+percent',
    textinfo='value',
    marker=dict(colors=['red', 'orange', 'yellow', 'green', 'gray'])
)])

# fig_severity.update_layout(
#     title='Assessment Severity Distribution',
# )

st.plotly_chart(fig_severity, use_container_width=True)

st.markdown("---")

st.subheader("Severity Distribution")

severity_order = ['Green', 'Yellow', 'Orange', 'Red']
severity_colors = {'Green': 'green', 'Yellow': 'yellow', 'Orange': 'orange', 'Red': 'red'}

sorted_severity_counts = severity_counts.reindex(severity_order).fillna(0)

#create horizontal bar chart
fig_severity_bar = go.Figure(data=[go.Bar(
    y=sorted_severity_counts.index,
    x=sorted_severity_counts.values,
    orientation='h',
    text=sorted_severity_counts.values,
    textposition='auto',
    marker_color=[severity_colors[severity] for severity in sorted_severity_counts.index]
)])

fig_severity_bar.update_layout(
    xaxis_title='Count',
    yaxis_title='Severity Level',
    height=400,
    margin=dict(l=50, r=50, t=80, b=50)
)

st.plotly_chart(fig_severity_bar, use_container_width=True)
