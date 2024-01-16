import plotly.express as px
import plotly.graph_objects as go

from data import (
    distance_per_club,
    driving_accuracy_data,
    performance_by_par,
    gps_traces,
)


def gap_analysis():
    """
    Creates gap analysis figure. Calls distanct per club function to create dataframe
    """
    df = distance_per_club()
    custom_order = df["club"].iloc[::-1].unique()

    fig = px.box(
        df, x="club", y="yards", category_orders={"club": custom_order}, color="club"
    )

    return fig


def driving_accuracy(**kwargs):
    """
    Creates driving accuracy bar graphs
    kwargs: club_order for custom club ordering list, accuracy_order for custom RIGHT/LEFT/HIT orders
    """
    df = driving_accuracy_data()

    if "accuracy_order" in kwargs:
        accuracy_order = kwargs["accuracy_order"]
    else:
        accuracy_order = ["LEFT", "HIT", "RIGHT"]

    if "club_order" in kwargs:
        club_order = kwargs["cub_order"]
    else:
        club_order = ["Driver", "3 Wood", "5 Wood", "4 Iron", "5 Iron"]

    fig = px.bar(
        df,
        x="club",
        y="count",
        color="fairwayshotoutcome",
        barmode="group",
        title="Driving Accuracy by number of shots per club",
        category_orders={"fairwayshotoutcome": accuracy_order, "club": club_order},
    )
    pivot_df = df.pivot_table(
        index="club", columns="fairwayshotoutcome", values="count", fill_value=0
    )
    total_counts = df.groupby("club")["count"].sum()
    percentage_df = pivot_df.div(total_counts, axis=0) * 100

    fig1 = px.bar(
        percentage_df,
        color="fairwayshotoutcome",
        barmode="group",
        title="Driving Accuracy by percent of shots",
        category_orders={"fairwayshotoutcome": accuracy_order, "club": club_order},
    )
    return fig, fig1


def score_map(row):
    score_dict = {
        -3: "Albatross",
        -2: "Eagle",
        -1: "Birdie",
        0: "Par",
        1: "Bogey",
        2: "Double Bogey",
        3: "Triple Bogey",
    }
    if row["strokes"] == 1:
        score_name = "Hole in One"
    elif row["score"] < 4:
        score_name = score_dict[row["score"]]
    else:
        score_name = f"+{row['score']}"

    return score_name


def scoring_pies(filter=None):
    df = performance_by_par()
    if filter:
        df_sorted = df[df["hole_par"] == filter].sort_values(by="score")
    else:
        df_sorted = df.sort_values(by="score")
    df_sorted["score_name"] = df_sorted.apply(lambda row: score_map(row), axis=1)

    plot = px.pie(
        df_sorted,
        names="score_name",
        color_discrete_sequence=px.colors.sequential.Turbo,
    )
    plot.update_traces(textposition="inside", textinfo="percent+label")

    return plot


def map():
    df = gps_traces()
    # Create a color scale for scorecardid
    color_scale = px.colors.qualitative.Set1  # Adjust the color scale as needed

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="scorecardid",
        hover_name="scorecardid",
        size_max=15,
        zoom=15,
        height=300,
        color_discrete_sequence=color_scale,
    )

    # Connect start and end locations with lines
    for i in range(0, len(df), 2):
        fig.add_trace(
            go.Scattermapbox(
                mode="lines",
                lon=[df["startloc_lon"][i], df["endloc_lon"][i]],
                lat=[df["startloc_lat"][i], df["endloc_lat"][i]],
                marker=dict(opacity=0),
                line=dict(
                    width=2, color=color_scale[df["scorecardid"][i] % len(color_scale)]
                ),
            )
        )

    fig.update_layout(
        mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig
