import streamlit as st 
import sqlite3 as db 
import pandas as pd 
import altair as alt 
import plotly.express as px 
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import os 


cwd = os.getcwd()
conn = db.connect('/Users/ben/projects/streamlit_golf/db/golf.db')
cur = conn.cursor()


def distance_per_club():
    """
    Processes data and creates a graph for the gap analysis of clubs returns the altair chart object
    """
    ## Distance per club, gap analysis
    sql = """
    select club.id, clubtypeid, club_type.name as club, shot.yards, retired
    from club
    join club_type on club_type.id = clubtypeid
    join shot on shot.clubid = club.id
    where retired = 0
    """

    df1 = pd.read_sql(sql,conn)



    # Filter the DataFrame for anything erroneously long and for the putter as distance really doesn't matter
    filtered_df = df1[(df1['yards']<325 ) & (df1['club'] != 'Putter')] #[df1['retired'] == 1]
    slim_filtered_df = filtered_df[['club','yards','retired']].copy()
    # Calculate the average yards per club
    average_yards_per_club = slim_filtered_df.groupby('club')['yards'].mean().sort_values().reset_index()


    sorted = pd.merge(slim_filtered_df,average_yards_per_club,on='club').rename(columns={'yards_y':'club_avg','yards_x':'yards'})
    # sorted[['club','club_avg']].drop_duplicates()

    custom_order = sorted['club'].iloc[::-1].unique()

    chart = alt.Chart(sorted).mark_boxplot().encode(
        x=alt.X('club:N', sort=custom_order),
        y='yards:Q',
        color=alt.Color('club:N',legend=None)
        # tooltip=['club:N', 'yards:Q']
    ).properties(
        width=800,
        height=400,
        title='Yardage gap Analysis per club'
    )
    return chart


def driving_accuracy():

## Driving accuracy 

    acc_query = """
    select club_type.name as club, fairwayshotoutcome,  count(*) as count
    from club
    join club_type on club_type.id = clubtypeid
    join shot on shot.clubid = club.id
    join hole_history  on shot.scorecardid  = hole_history.scorecardid and hole_history.number = shot.holenumber  
    where startloc_lie = 'TeeBox' and fairwayshotoutcome is not null
    group by club, fairwayshotoutcome
    """

    acc_df = pd.read_sql(acc_query,conn)
    desired_order = ['LEFT', 'HIT', 'RIGHT']
    club_order = ['Driver','3 Wood','5 Wood','4 Iron','5 Iron']

    mask = acc_df['club']
    fig = px.bar(
        acc_df, 
        x='club',
        y='count',
        color='fairwayshotoutcome',
        barmode='group',
        title="Driving Accuracy by number of shots per club",
        category_orders={"fairwayshotoutcome": desired_order, "club":club_order}
    )
    pivot_df = acc_df.pivot_table(index='club', columns='fairwayshotoutcome', values='count', fill_value=0)
    total_counts = acc_df.groupby('club')['count'].sum()
    percentage_df = pivot_df.div(total_counts, axis=0) * 100


    fig1 = px.bar(
        percentage_df,
        color='fairwayshotoutcome',
        barmode='group',
        title="Driving Accuracy by percent of shots",
        category_orders={"fairwayshotoutcome": desired_order, "club":club_order}
    )
    return fig, fig1


def map():
    """
    Needs work
    """
    sql = """select scorecardid,shotorder,clubid,holenumber,startloc_lat,startloc_lon,endloc_lat,endloc_lon  
    from shot 
    join scorecard  on scorecard.id = shot.scorecardid
    join course on course.id = scorecard.coursesnapshotid 
    where coursename = 'Cog Hill Golf & Country Club ~ Red'"""
    df = pd.read_sql(sql, conn)
    print(df)
    token = 'pk.eyJ1IjoiYmVud2l0dGJyb2R0IiwiYSI6ImNscXN0ejFoOTA0cWUya3F2NThrbG43dzAifQ.BGXXmDZZD4OhROZzfU8RQ'
    px.set_mapbox_access_token(token)

    # Assuming your DataFrame is named df

    # Create a new DataFrame for start locations
    start_df = df[['scorecardid', 'startloc_lat', 'startloc_lon']].rename(columns={'startloc_lat': 'lat', 'startloc_lon': 'lon'})

    # Create a new DataFrame for end locations
    end_df = df[['scorecardid', 'endloc_lat', 'endloc_lon']].rename(columns={'endloc_lat': 'lat', 'endloc_lon': 'lon'})

    # Concatenate start and end DataFrames
    locations_df = pd.concat([start_df, end_df], ignore_index=True)

    # Create a color scale for scorecardid
    color_scale = px.colors.qualitative.Set1  # Adjust the color scale as needed

    fig = px.scatter_mapbox(locations_df, lat="lat", lon="lon", color="scorecardid",
                            hover_name="scorecardid", size_max=15, zoom=15, height=300,
                            color_discrete_sequence=color_scale)

    # Connect start and end locations with lines
    for i in range(0, len(df), 2):
        fig.add_trace(
            go.Scattermapbox(
                mode="lines",
                lon=[df['startloc_lon'][i], df['endloc_lon'][i]],
                lat=[df['startloc_lat'][i], df['endloc_lat'][i]],
                marker=dict(opacity=0),
                line=dict(width=2, color=color_scale[df['scorecardid'][i] % len(color_scale)]),
            )
        )

    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def performance_by_par(filter):
    sql = """
        select (strokes - hole_par) as score, hole_par, hole_length_yards , hole_handicap, putts, fairwayshotoutcome 
        from hole_history
        where strokes is not null 
        """
    par_perf_df = pd.read_sql(sql,conn)
    par_perf_df_slim = par_perf_df[par_perf_df["hole_par"] == filter]
    df_sorted = par_perf_df_slim.sort_values(by='score')
    
    plot = px.pie(df_sorted,names='score',labels={'score':'score'}, color_discrete_sequence=px.colors.sequential.Turbo)
    plot.update_traces(textposition='inside', textinfo='percent+label')
  

    return plot