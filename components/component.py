from abc import ABC, abstractmethod, abstractproperty
from plotly.graph_objects import Figure

# TODO:
#  - getters and setters, especially for layout


class Component(Figure, ABC):

    # this is the general layout
    _fig_layout = dict(
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

    _graph_props = dict()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _make_data(self, *args, **kwargs):
        """
        Abstract method to be overwritten in child class.
        """
        raise NotImplementedError

    @property
    def fig_layout(self) -> dict:
        return self._fig_layout

    @fig_layout.setter
    def fig_layout(self, layout):
        self._fig_layout = layout

