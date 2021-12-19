from plotly.graph_objs import Figure, Heatmap
from components.component import Component
from lab_df import LabDataFrame


class MarginalHeatmap(Component):

    _graph_props = dict()

    def __init__(self, lab_df: LabDataFrame, param: str, size_keys=None,
                 filters: dict = {}, **kwargs):
        # todo fix this ghastly size_keys stuff
        data = self._make_data(lab_df, filters, param, size_keys)
        super().__init__(data=data, **kwargs)

    @property
    def graph_props(self) -> dict:
        return self._graph_props

    def _make_data(self, lab_df: LabDataFrame, filters, param, size_keys):

        # todo this is only for the epidemic size right now
        #  -> provide some more options

        # x values
        x = lab_df.formatted[param].unique()

        # name of the parameter
        y = [param]  # todo maybe something more useful

        df = lab_df.filter(filters)
        epi = lab_df.epidemic_size_per_param(df, param, size_keys)
        epi = epi.groupby(param).mean()
        epi.sort_index(inplace=True)
        z = [list(epi.epidemic_size.values)]

        fig = Figure(
            data=Heatmap(
                z=z, x=x, y=y,
                # colorscale=[[0, 'rgb(237, 198, 48)'], [1, 'rgb(5, 38, 150)']],
                colorbar=dict(title={'text': 'epidemic_size', 'side': 'right'}),
                hovertemplate=param + ': %{x}<br>epidemic_size: %{z}<extra></extra>'
            ),
        )

        fig.update_layout(**self.fig_layout)
        return fig.data
