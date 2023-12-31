import streamlit as st
from datasets import distance_per_club, driving_accuracy, map

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
