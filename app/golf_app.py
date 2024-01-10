import streamlit as st
from datasets import distance_per_club, driving_accuracy, performance_by_par

# Initialize session state variable
if 'driving_acc_toggle' not in st.session_state:
    st.session_state['driving_acc_toggle'] = 0

st.title("Garmin Golf Data Analysis")

# Display gap analysis 
gap_analysis = distance_per_club()
st.plotly_chart(gap_analysis)
st.caption("Analysis of the gapping via box plot for golf shots. Ideally each club should occupy its' own range of distance")

st.header("Driving Accuray from the Tee")
st.text("Did I hit the fairway?")
fig, fig1 = driving_accuracy()

# Render the graph above the toggle
if st.session_state['driving_acc_toggle'] == 1:
    st.plotly_chart(fig1)
else: 
    st.plotly_chart(fig)

# Toggle for switching between percentage view and normal view
togg = st.toggle('View by percentage', key='driving_acc_toggle')

st.divider()

st.header("Scoring Performance by Hole Par Rating")
tab1, tab2, tab3, tab4 = st.tabs(["Overall","Par 3", "Par 4", "Par 5"])
tab_write = [tab1, tab2, tab3, tab4]
z = 0
for i in [None,3,4,5]:
    plot = performance_by_par(i)

    tab_write[z].plotly_chart(plot)
    z+=1