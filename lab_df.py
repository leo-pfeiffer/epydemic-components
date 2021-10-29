from typing import List, Callable, Optional, Dict, Any

import numpy as np
import pandas as pd
from epyc import LabNotebook
from epydemic import Monitor
from functools import reduce


class LabDataFrame:

    def __init__(self, df: Optional[pd.DataFrame] = None):

        if df is not None:
            assert isinstance(df, pd.DataFrame)

        self._df = df
        self._formatted = None
        self._locus_keys = None
        self._param_keys = None

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def locus_keys(self):
        return self._locus_keys

    @locus_keys.setter
    def locus_keys(self, locus_keys):
        assert isinstance(locus_keys, list)
        for key in locus_keys:
            if not Monitor.timeSeriesForLocus(key) in self.df.columns:
                raise ValueError(f'The provided locus key {key} is not in the'
                                 f'columns of LabDataFrame.df')
        self._locus_keys = locus_keys

    @property
    def param_keys(self):
        return self._param_keys

    @param_keys.setter
    def param_keys(self, param_keys):
        assert isinstance(param_keys, list)
        for key in param_keys:
            if not key in self.df.columns:
                raise ValueError(f'The provided parameter key {key} is not in'
                                 f'the columns of LabDataFrame.df')
        self._param_keys = param_keys

    @property
    def formatted(self):
        if self._formatted is None:
            raise AttributeError(
                'LabDataFrame.format(keys) must be called first.'
            )
        return self._formatted

    @staticmethod
    def from_lab_notebook(notebook: LabNotebook):
        return LabDataFrame(notebook.dataframe())

    def format(self, locus_keys: Optional[List[str]] = None,
               param_keys: Optional[List[str]] = None):
        """
        Convert to correct format data frame
        :param locus_keys: List of time series keys for the data frame,
        e.g. SIR.INFECTED
        :param param_keys: List of param keys for the data frame,
        e.g. SEIRWithQuarantine.p_quarantine
        """

        if locus_keys is None:
            if self.locus_keys is None:
                raise TypeError('Argument locus_keys must be specified if '
                                'LabDataFrame.locus_keys is not set.')
            locus_keys = self.locus_keys

        if param_keys is None:
            if self.param_keys is not None:
                param_keys = self.param_keys
            else:
                param_keys = []

        num_experiments = len(self._df)
        experiment_ids = self._df.index.tolist()

        # time steps of the observations
        time_steps = self._get_time_steps()
        num_observations = len(time_steps)

        # initialise fill values
        fill = dict(
            experiment_id=[],  # experiment id
            time=[],  # time step
            key=[],  # what the value refers to, e.g. a compartment
            value=[]  # the value of the observation
        )

        for pk in param_keys:  # parameter keys
            fill[pk] = []

        # for each key, fill the lists
        for key in locus_keys:
            # data frame with time series
            ts = self._get_key_df(key, time_steps)

            # put the data into the `value` column
            fill['value'] += reduce(lambda a, b: a + b, ts.values.tolist())

            # fill in the experiment IDs ...
            fill['experiment_id'] += [
                experiment_ids[i] for i in range(num_experiments)
                for _ in range(num_observations)
            ]

            # ... and the key
            fill['key'] += [key] * num_experiments * len(time_steps)

            # ... and the time steps
            fill['time'] += time_steps * num_experiments

            # ... and the params
            for pk in param_keys:
                vals = self._df[pk].values.tolist()
                fill[pk] += [
                    vals[i] for i in range(num_experiments)
                    for _ in range(num_observations)
                ]

        self._formatted = pd.DataFrame(fill)

        return self._formatted

    def _get_time_steps(self) -> list:
        """
        Extract the time steps of the observations.
        :return: List of observation time steps
        """
        longest_obs = (self._df[Monitor.OBSERVATIONS].apply(len) ==
                       self._df[Monitor.OBSERVATIONS].apply(len).max())

        return self._df.loc[longest_obs].iloc[0][Monitor.OBSERVATIONS]

    def _get_key_df(self, ts_key, time_steps) -> pd.DataFrame:
        """
        Extract the values for a key
        :param ts_key: Time series key, e.g. SIR.INFECTED
        :param time_steps: Time steps of the experiment
        :return:
        """
        tss = self._df[Monitor.timeSeriesForLocus(ts_key)]

        return pd.DataFrame(tss.values.tolist(), columns=time_steps)

    def group_apply(self, func: Callable):
        """
        Apply the `func` callable to the formatted data frame.
        :param func: A callable to be applied to the dataframe
        :return: The data frame grouped by time and key with the `func` applied.
        """

        grouped = self.formatted[['experiment_id', 'time', 'key', 'value']]
        grouped = grouped.groupby(['time', 'key']).agg(func)
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)
        return grouped

    def group_mean(self):
        """
        Calculate the mean value per time per key column of the formatted df.
        """
        return self.group_apply(np.mean)

    def group_std(self):
        """
        Standard deviation per time per value in key column of the formatted df.
        :return:
        """
        return self.group_apply(np.std)

    def filter(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter the data frame by the values specified in `filters`.
        :param filters: Dictionary containing columns as keys and filter values
            as values
        :return: The subset as a data frame.
        """

        return self._apply_filters(self.formatted, filters)

    @staticmethod
    def _apply_filters(df, filters: Dict[str, Any]):
        """
        Filter `df` by the conditions provided in `filters` where the keys
        correspond to columns in `df` and values are the values to filter for.
        :param df: Data frame to filter
        :param filters: Dictionary with filter conditions
        :return: filtered df
        """

        # create array with true values only
        arr = np.array([True] * len(df))

        for k, v in filters.items():
            # define filter (taking into account floating point imprecision) and
            #  combine with previous filters
            arr = arr & (lambda x: np.isclose(x, v))(df[k].values)

        return df.loc[arr]
