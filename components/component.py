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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def _make_data(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def graph_props(self) -> dict:
        pass

    @property
    def fig_layout(self) -> dict:
        return self._fig_layout
