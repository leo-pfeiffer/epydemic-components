# todo find a better name

import plotly.express as px
import numpy as np
from plotly.graph_objs import Figure

from components.component import Component
from lab_df import LabDataFrame


class CompartmentLines(Component):
    _graph_props = dict(
        x="time",
        y="value"
    )

    def __init__(self, lab_df: LabDataFrame, key: str, param: str, **kwargs):
        data = self._make_data(lab_df, key, param)
        super().__init__(data=data, **kwargs)

    @property
    def graph_props(self) -> dict:
        return self._graph_props

    def _make_data(self, lab_df, key, param):
        df = lab_df.formatted[lab_df.formatted['key'] == key].copy()

        cat = [str(x) for x in sorted(df[param].unique(), reverse=True)]

        df[param] = df[param].astype(str)

        grouped = df.groupby(['time', param]).mean()
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)

        self._graph_props['color'] = param
        self._graph_props['hover_name'] = param
        self._graph_props['category_orders'] = {param: cat}

        fig_line = px.line(grouped, **self.graph_props)
        fig_scat = px.scatter(df, **self.graph_props)
        fig_line.update_traces(showlegend=False, hoverinfo='none')

        fig = Figure(data=fig_line.data + fig_scat.data)
        fig.update_layout(**self.fig_layout)

        return fig.data



