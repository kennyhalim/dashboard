import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from calendar import month_abbr


conn = st.connection('mysql', type='sql')

st.title('Fatigue Risk Management Dashboard')

st.markdown("April 2024 - August 2024")


st.markdown("---")

#st.subheader("Monthly Worker Assessment Count")

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
#max_assessment_month = monthly_assessment_df.loc[monthly_assessment_df['assessment_count'].idxmax()]



severe_assessment_df = conn.query('''
    SELECT 
        DATE_FORMAT(created_dt, '%Y-%m') as month,
        COUNT(*) as assessment_count
    FROM 
        t_worker_assessment
    WHERE 
        created_dt >= '2024-04-01' AND created_dt <= '2024-08-31' AND question_six_answer = '1'                           
    GROUP BY 
        DATE_FORMAT(created_dt, '%Y-%m')
    ORDER BY 
        month
''', ttl=600)


severe_assessment_df['month'] = pd.to_datetime(severe_assessment_df['month'])


modsev_assessment_df = conn.query('''
    SELECT 
        DATE_FORMAT(created_dt, '%Y-%m') as month,
        COUNT(*) as assessment_count
    FROM 
        t_worker_assessment
    WHERE 
        created_dt >= '2024-04-01' AND created_dt <= '2024-08-31' AND question_five_answer = '1'                           
    GROUP BY 
        DATE_FORMAT(created_dt, '%Y-%m')
    ORDER BY 
        month
''', ttl=600)


modsev_assessment_df['month'] = pd.to_datetime(modsev_assessment_df['month'])


mildmod_assessment_df = conn.query('''
    SELECT 
        DATE_FORMAT(created_dt, '%Y-%m') as month,
        COUNT(*) as assessment_count
    FROM 
        t_worker_assessment
    WHERE 
        created_dt >= '2024-04-01' AND created_dt <= '2024-08-31' AND question_four_answer = '1'                           
    GROUP BY 
        DATE_FORMAT(created_dt, '%Y-%m')
    ORDER BY 
        month
''', ttl=600)


mildmod_assessment_df['month'] = pd.to_datetime(mildmod_assessment_df['month'])


mild_assessment_df = conn.query('''
    SELECT 
        DATE_FORMAT(created_dt, '%Y-%m') as month,
        COUNT(*) as assessment_count
    FROM 
        t_worker_assessment
    WHERE 
        created_dt >= '2024-04-01' AND created_dt <= '2024-08-31' AND (question_one_answer = '1' OR question_two_answer = '1' OR question_three_answer = '1')                    
    GROUP BY 
        DATE_FORMAT(created_dt, '%Y-%m')
    ORDER BY 
        month
''', ttl=600)


mild_assessment_df['month'] = pd.to_datetime(mildmod_assessment_df['month'])


#with col1:
#    st.metric("Highest Number of Assessments", max_assessment_month['assessment_count'])

#with col2:
#    st.metric("Achieved In", max_assessment_month['month'].strftime('%B %Y'))



fig_monthly_assessment = go.Figure()

fig_monthly_assessment.add_trace(go.Scatter(
    x=monthly_assessment_df['month'],
    y=monthly_assessment_df['assessment_count'],
    mode='lines',
    name='Overall',
    line=dict(color='#313433')#,
    #marker=dict(size=8)
))

#fig_monthly_assessment.add_trace(go.Scatter(
#    x=[max_assessment_month['month']],
#    y=[max_assessment_month['assessment_count']],
#    mode='markers',
#    name='Highest Count',
#    marker=dict(symbol='star', size=16, color='green'),
#    showlegend=False
#))

fig_monthly_assessment.update_layout(
    title='Fatigue Assessments',
    xaxis_title='Month',
    yaxis_title='Number of Assessments',
    xaxis=dict(
        tickmode='array',
        tickvals=monthly_assessment_df['month'],
        ticktext=[month_abbr[date.month] for date in monthly_assessment_df['month']],
    ),
    hovermode='x unified'
)


fig_monthly_assessment.add_scatter(
    x=severe_assessment_df['month'], 
    y=severe_assessment_df['assessment_count'],
    mode='lines',
    line=dict(color='#ff8a8a'),
    name='Severe'
)

fig_monthly_assessment.add_scatter(
    x=modsev_assessment_df['month'], 
    y=modsev_assessment_df['assessment_count'],
    mode='lines',
    line=dict(color='#f5b779'),
    name='Moderate to Severe'
)

fig_monthly_assessment.add_scatter(
    x=mildmod_assessment_df['month'], 
    y=mildmod_assessment_df['assessment_count'],
    mode='lines',
    line=dict(color='#f5f578'),
    name='Mild to Moderate'
)

fig_monthly_assessment.add_scatter(
    x=mild_assessment_df['month'], 
    y=mild_assessment_df['assessment_count'],
    mode='lines',
    line=dict(color='#9fe59f'),
    name='Mild'
)




st.plotly_chart(fig_monthly_assessment, use_container_width=True)
    #st.metric("Highest Number of Assessments", max_assessment_month['assessment_count'])


#bar chart
st.markdown("---")

st.markdown("**Fatigue Levels**")

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
        return 'Severe'
    elif row['question_five_answer'] == 1:
        return 'Moderate to Severe'
    elif row['question_four_answer'] == 1:
        return 'Mild to Moderate'
    elif row['question_one_answer'] == 1 or row['question_two_answer'] == 1 or row['question_three_answer'] == 1:
        return 'Mild'
    else:
        return 'Mild'

worker_assessment_df['severity'] = worker_assessment_df.apply(determine_severity, axis=1)

severity_counts = worker_assessment_df['severity'].value_counts()
#st.dataframe(severity_counts)

total_assessments = severity_counts.sum()
severity_percentages = (severity_counts / total_assessments * 100).round(1)

severity_order = ['Mild', 'Mild to Moderate', 'Moderate to Severe', 'Severe']
severity_colors = {'Mild': '#9fe59f', 'Mild to Moderate': '#f5f578', 'Moderate to Severe': '#f5b779', 'Severe': '#ff8a8a'}
sorted_severity_percentages = severity_percentages.reindex(severity_order).fillna(0)



#create pie chart
fig_severity = go.Figure(data=[go.Pie(
    labels=sorted_severity_percentages.index,
    values=sorted_severity_percentages.values,
    hole=.3,
    hoverinfo='label+percent',
    textinfo='percent',
    textposition='inside',
    insidetextorientation='radial',
    marker=dict(colors=[severity_colors[severity] for severity in sorted_severity_percentages.index])
)])


fig_severity.update_traces(textfont_size=12)

fig_severity.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)


#fig_severity.update_layout(
#    title='Fatigue Severity'
#)

#st.subheader("Severity Distribution")

severity_order = ['Mild', 'Mild to Moderate', 'Moderate to Severe', 'Severe']
severity_colors = {'Mild': '#9fe59f', 'Mild to Moderate': '#f5f578', 'Moderate to Severe': '#f5b779', 'Severe': '#ff8a8a'}

sorted_severity_counts = severity_counts.reindex(severity_order).fillna(0)

#create horizontal bar chart
fig_severity_bar = go.Figure(data=[go.Bar(
    #y=sorted_severity_counts.index,
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
    margin=dict(l=50, r=50, t=80, b=50),
    hovermode='y unified'
)

#fig_severity_bar.update_layout(
#    title='Severity by Numbers',   
#)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_severity, use_container_width=True)
    #st.metric("Highest Number of Assessments", max_assessment_month['assessment_count'])

with col2:
    st.plotly_chart(fig_severity_bar, use_container_width=True)
    #st.metric("Achieved In", max_assessment_month['month'].strftime('%B %Y'))

st.markdown("---")

st.markdown("**Countermeasures**")

#st.subheader("Countermeasures")

countermeasures_df = conn.query('CALL getCountermeasuresData()', ttl=600)

countermeasures_df = countermeasures_df[:5]

countermeasures_df = countermeasures_df.set_index('countermeasure_short')
#st.dataframe(countermeasures_df)

countermeasures_sr = countermeasures_df['percentage']
#st.dataframe(countermeasures_sr)


countermeasure_order = ['Nap', 'High Protein Foods', 'Hydration', 'Avoid Sugar','Caffeine']
countermeasure_colors = {'Nap': '#a4d164', 'High Protein Foods': '#8fbc98', 'Hydration': '#689d87', 'Avoid Sugar': '#4e7464', 'Caffeine':'#2d6065'}
sorted_countermeasures_sr = countermeasures_sr.reindex(countermeasure_order).fillna(0)

fig_countermeasures = go.Figure(data=[go.Pie(
    labels=sorted_countermeasures_sr.index,
    values=sorted_countermeasures_sr.values,
    hole=.3,
    hoverinfo='label+percent',
    textinfo='percent',
    textposition='inside',
    insidetextorientation='radial',
    marker=dict(colors=[countermeasure_colors[countermeasure] for countermeasure in sorted_countermeasures_sr.index])

    #showlegend=False
    
)])

fig_countermeasures.update_traces(textfont_size=12)

fig_countermeasures.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)


#fig_countermeasures.update_traces(
#            hoverinfo="label+value",
#            textinfo="percent",
#            marker=dict(
#                colors=[
#                    "#a4d164",
#                    "#8fbc98",
#                    "#689d87",
#                    "#4e7464",
#                    "#2d6065",
#                    "#125972"                                       
#                ]
#            )
#        )


#fig_countermeasures.update_layout(
#    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#)

#fig_countermeasures.update_layout(legend=dict(
#    orientation="h",
#    #entrywidth=70,
#    yanchor="bottom",
#    y=1.02,
#    xanchor="right",
#    x=-70
#))

#fig_severity.update_layout(
#    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=-10)
#)


#st.plotly_chart(fig_countermeasures, use_container_width=True)



diction = {'measure':["Nap", "High Protein Foods", "Hydration", "Avoid Sugar", "Caffeine"],
        'effect': [1.8,0.7, 0.5, 0.1 ,0.3]}

countermeasure_eff_df = pd.DataFrame(diction, index=["0", "1", "2", "3", "4"])

countermeasure_eff_df = countermeasure_eff_df.set_index('measure')

countermeasure_eff_order = ["Nap", "High Protein Foods", "Hydration", "Avoid Sugar", "Caffeine"]
countermeasure_colors = {'Nap': '#a4d164', 'High Protein Foods': '#8fbc98', 'Hydration': '#689d87', 'Avoid Sugar': '#4e7464', 'Caffeine':'#2d6065'}

sorted_countermeasures_eff_df = countermeasure_eff_df.reindex(countermeasure_eff_order).fillna(0)

#st.dataframe(countermeasure_eff_df['effect'])

countermeasure_eff =  go.Figure(data=[go.Bar(
    x=countermeasure_eff_order, #countermeasure_eff_df['measure'],
    y=countermeasure_eff_df['effect'],
    text=countermeasure_eff_df['effect'],
    textposition='auto',
    marker_color=[countermeasure_colors[cm] for cm in sorted_countermeasures_eff_df.index]
)])

countermeasure_eff.update_layout(
    xaxis_title='Countermeasure',
    yaxis_title='Average Effect on Fatigue',
    height=400,
    margin=dict(l=50, r=50, t=80, b=50),
    hovermode='x unified'
)


#countermeasure_eff.update_layout(
#    title={
#        #'text': 'Countermeasure Effectiveness',
#        'y':0.9,
#        'x':0.5,
#        'xanchor': 'center',
#        'yanchor': 'top'
#    },
#    xaxis_title='Countermeasure',
#    yaxis_title='Average Effect on Fatigue',
#    #hovermode='label+percent',
#    hovermode='x unified',
#    height=400
#)

#countermeasure_eff.update_xaxes(tickangle=-45, tickfont=dict(size=10))

#countermeasure_eff.update_layout(
#    title=' ', #Countermeasure Effectiveness',
#    margin=dict(l=50, r=50, t=80, b=50)
    
#)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_countermeasures, use_container_width=True)

with col2:
    st.plotly_chart(countermeasure_eff, use_container_width=True)
    #st.metric("Achieved In", max_assessment_month['month'].strftime('%B %Y'))

st.markdown("---")

#fig_countermeasures.add_trace(marker=dict(colors=['green', 'red', 'green', 'red','red']))

# st.write("Countermeasures Data")
# display_df = countermeasures_df[['countermeasure_text', 'count', 'percentage']]
# st.dataframe(display_df.style.format({
#     'count': '{:,.0f}',
#     'percentage': '{:.2f}%'
# }), height=300)


#st.subheader("Causes of Fatigue")

fatigue_causes_df = conn.query('CALL getCausesOfFatigueCount()', ttl=600)

fig_fatigue_causes = go.Figure(data=[go.Bar(
    x=fatigue_causes_df['fatigue_cause'],
    y=fatigue_causes_df['count'],
    text=fatigue_causes_df['count'],
    textposition='auto',
    marker_color= '#4e7464' #'#a4d164'

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
    #hovermode='label+percent',
    hovermode='x unified',
    height=400
)

fig_fatigue_causes.update_xaxes(tickangle=-45, tickfont=dict(size=10))

fig_fatigue_causes.update_layout(
    title='Causes of Fatigue',
    margin=dict(l=50, r=250, t=80, b=50)
    
)

st.plotly_chart(fig_fatigue_causes, use_container_width=True)

# st.write("Fatigue Causes Data")
# st.dataframe(fatigue_causes_df.style.format({
#     'count': '{:,.0f}'
# }), height=200)

#one pie chart for severity

