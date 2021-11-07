import plotly.express as px
from components.component import Component
from lab_df import LabDataFrame


class CompartmentCurves(Component):

    _graph_props = dict(
        x="time",
        y="value",
        color="key",
        hover_name="key",
        # category_orders={"compartment": ['S', 'E', 'I', 'V', 'R']}
    )

    def __init__(self, lab_df: LabDataFrame, **kwargs):
        data = self._make_data(lab_df)
        super().__init__(data=data, **kwargs)

    @property
    def graph_props(self) -> dict:
        return self._graph_props

    def _make_data(self, lab_df):
        fig_line = px.line(lab_df.group_mean(), **self.graph_props)
        fig_scat = px.scatter(lab_df.formatted, **self.graph_props)
        fig_scat.update_traces(showlegend=False, hoverinfo='none')
        return fig_line.data + fig_scat.data




