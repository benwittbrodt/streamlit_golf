import streamlit as st
from datasets import distance_per_club, driving_accuracy, map, performance_by_par

# Initialize session state variable
if 'driving_acc_toggle' not in st.session_state:
    st.session_state['driving_acc_toggle'] = 0

# Display gap analysis 
gap_analysis = distance_per_club()
st.altair_chart(gap_analysis)

fig, fig1 = driving_accuracy()

# Render the graph above the toggle
if st.session_state['driving_acc_toggle'] == 1:
    st.plotly_chart(fig1)
else: 
    st.plotly_chart(fig)

# Toggle for switching between percentage view and normal view
togg = st.toggle('View by percentage', key='driving_acc_toggle')


# st.plotly_chart(map())

tab1, tab2, tab3 = st.tabs(["Par 3", "Par 4", "Par 5"])

tab_write = [tab1, tab2, tab3]

z = 0
for i in [3,4,5]:
    plot = performance_by_par(i)

    tab_write[z].plotly_chart(plot)
    z+=1