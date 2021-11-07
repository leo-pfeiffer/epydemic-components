import plotly.express as px
from components.component import Component


class CompartmentCurves(Component):

    _graph_props = dict(
        x="time",
        y="value",
        color="key",
        hover_name="key",
        # category_orders={"compartment": ['S', 'E', 'I', 'V', 'R']}
    )

    def __init__(self, df, grouped_df, **kwargs):
        data = self._make_data(df, grouped_df)
        super().__init__(data=data, **kwargs)

    @property
    def graph_props(self) -> dict:
        return self._graph_props

    def _make_data(self, df, grouped_df):
        fig_line = px.line(grouped_df, **self.graph_props)
        fig_scat = px.scatter(df, **self.graph_props)
        fig_scat.update_traces(showlegend=False, hoverinfo='none')
        return fig_line.data + fig_scat.data




