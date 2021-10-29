import plotly.express as px
from plotly.graph_objects import Figure

main_graph_props = dict(
    x="time",
    y="value",
    color="key",
    hover_name="key",
    # category_orders={"compartment": ['S', 'E', 'I', 'V', 'R']}
)

fig_layout = dict(
    margin=dict(l=10, r=10, t=10, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.15,
        xanchor="center",
        x=0.5
    ),
    autosize=True
)


def make_main_graph(df, grouped_df):
    fig_line = px.line(grouped_df, **main_graph_props)
    fig_scat = px.scatter(df, **main_graph_props)
    fig_scat.update_traces(showlegend=False, hoverinfo='none')

    fig = Figure(data=fig_line.data + fig_scat.data)

    fig.update_layout(**fig_layout)

    return fig
