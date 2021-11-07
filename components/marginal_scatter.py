import plotly.express as px
from components.component import Component
from lab_df import LabDataFrame


class MarginalScatter(Component):

    _graph_props = dict()

    def __init__(self, lab_df: LabDataFrame, param: str, filters: dict = {},
                 size_keys=None, **kwargs):

        # todo fix this ghastly size_keys stuff
        if size_keys is None:
            size_keys = ['epydemic.SEIR.R', 'epydemic.SEIR.E']
        else:
            size_keys = []
        data = self._make_data(lab_df, filters, param, size_keys)
        super().__init__(data=data, **kwargs)

    @property
    def graph_props(self) -> dict:
        return self._graph_props

    def _make_data(self, lab_df, filters, param, size_keys):
        df = lab_df.filter(filters)
        epidemic_size = lab_df.epidemic_size_per_param(df, param, size_keys)
        fig = px.scatter(epidemic_size, x=param, y="epidemic_size")
        fig.update_layout(**self.fig_layout)
        return fig.data






