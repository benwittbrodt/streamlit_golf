import pandas as pd
import toml
from pathlib import Path
import sqlite3
import os

if __name__ == "__main__":
    project_base = Path(__file__).resolve().parent.parent

else:
    project_base = Path.cwd().parent


config = toml.load(project_base / "config.toml")

# Connect to database file and initiate a cursor for querying
DB_LOC = project_base / config["db_src"]
conn = sqlite3.connect(DB_LOC)


def distance_per_club(connection=conn):
    """
    Processes data for the gap analysis of clubs
    Returns: Dataframe that is cleaned and sorted
    """

    ## Distance per club, gap analysis
    sql = """
    select club.id, clubtypeid, club_type.name as club, shot.yards, retired
    from club
    join club_type on club_type.id = clubtypeid
    join shot on shot.clubid = club.id
    where retired = 0
    """

    df1 = pd.read_sql(sql, connection)

    # Filter the DataFrame for anything erroneously long and for the putter as distance really doesn't matter
    filtered_df = df1[(df1["yards"] < 325) & (df1["club"] != "Putter")]

    slim_filtered_df = filtered_df[["club", "yards", "retired"]].copy()
    # Calculate the average yards per club
    average_yards_per_club = (
        slim_filtered_df.groupby("club")["yards"].mean().sort_values().reset_index()
    )

    # Sort DF to put it in order of average yardage
    sorted = pd.merge(slim_filtered_df, average_yards_per_club, on="club").rename(
        columns={"yards_y": "club_avg", "yards_x": "yards"}
    )
    # Cleans up dataframe with an easy 1/2 average exclusion to remove any clearly duffed shots or half swings that were tracked
    sorted_clean = sorted[(sorted["yards"] > (sorted["club_avg"] / 2))]

    return sorted_clean


def driving_accuracy_data(connection=conn):
    """
    Queries dataset for driving accuracy
    """

    sql = """
    select club_type.name as club, fairwayshotoutcome,  count(*) as count
    from club
    join club_type on club_type.id = clubtypeid
    join shot on shot.clubid = club.id
    join hole_history  on shot.scorecardid  = hole_history.scorecardid and hole_history.number = shot.holenumber  
    where startloc_lie = 'TeeBox' and fairwayshotoutcome is not null
    group by club, fairwayshotoutcome
    """

    return pd.read_sql(sql, connection)


def performance_by_par(connection=conn):
    sql = """
        select (strokes - hole_par) as score, hole_par, strokes, hole_length_yards , hole_handicap, putts, fairwayshotoutcome 
        from hole_history
        where strokes is not null 
        """
    return pd.read_sql(sql, connection)


def gps_traces(connection=conn):
    """
    Needs work - doesn't show the full source of data and not all shots are combined
    """
    sql = """select scorecardid,shotorder,clubid,holenumber,startloc_lat,startloc_lon,endloc_lat,endloc_lon  
    from shot 
    join scorecard  on scorecard.id = shot.scorecardid
    join course on course.id = scorecard.coursesnapshotid 
    where coursename = 'Cog Hill Golf & Country Club ~ Red'"""
    df = pd.read_sql(sql, connection)

    # Create a new DataFrame for start locations
    start_df = df[["scorecardid", "startloc_lat", "startloc_lon"]].rename(
        columns={"startloc_lat": "lat", "startloc_lon": "lon"}
    )

    # Create a new DataFrame for end locations
    end_df = df[["scorecardid", "endloc_lat", "endloc_lon"]].rename(
        columns={"endloc_lat": "lat", "endloc_lon": "lon"}
    )

    # Concatenate start and end DataFrames
    return pd.concat([start_df, end_df], ignore_index=True)
