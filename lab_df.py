from typing import List, Callable, Optional, Dict, Any

import numpy as np
import pandas as pd
from epyc import LabNotebook
from epydemic import Monitor
from functools import reduce


class LabDataFrame:

    def __init__(self, df=None):
        if df is not None:
            assert isinstance(df, pd.DataFrame)
        self._df = df
        self._formatted = None

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

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

    def format(self, ts_keys: List[str],
               param_keys: Optional[List[str]] = None):
        """
        Convert to correct format data frame
        :param ts_keys: List of time series keys for the data frame,
        e.g. SIR.INFECTED
        :param param_keys: List of param keys for the data frame,
        e.g. SEIRWithQuarantine.p_quarantine
        """

        if param_keys is None:
            param_keys = []

        num_experiments = len(self._df)
        experiment_ids = self._df.index.tolist()

        # time steps of the observations
        time_steps = self._get_time_steps()
        num_observations = len(time_steps)

        # initialise fill values
        fill = dict(
            experiment_id=[],   # experiment id
            time=[],            # time step
            key=[],             # what the value refers to, e.g. a compartment
            value=[]            # the value of the observation
        )

        for pk in param_keys:   # parameter keys
            fill[pk] = []

        # for each key, fill the lists
        for key in ts_keys:
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
        raise NotImplementedError
        # grouped = self.formatted.groupby(['time', 'key']).mean()
        # grouped.reset_index(level=0, drop=True, inplace=True).reset_index(
        #     inplace=True)
        # return grouped

    def group_mean(self):
        """
        Calculate the mean value per time per key column of the formatted df.
        """
        # return self.group_apply(np.mean)
        grouped = self.formatted.groupby(['time', 'key']).mean()
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)
        return grouped

    def group_std(self):
        """
        Standard deviation per time per value in key column of the formatted df.
        :return:
        """
        # return self.group_apply(np.std)
        grouped = self.formatted.groupby(['time', 'key']).std()
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)
        return grouped

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

        # todo
        raise NotImplementedError

        # # create array with true values only
        # arr = np.array([True] * len(df))
        #
        # for k, v in filters.items():
        #     # define filter (taking into account floating point imprecision) and
        #     #  combine with previous filters
        #     arr = arr & (lambda x: np.isclose(x, v))(df[k].values)
        #
        # return df.loc[arr]