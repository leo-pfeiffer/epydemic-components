from typing import List, Callable

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
        self._long = None

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def long(self):
        if self._long is None:
            raise AttributeError(
                'LabDataFrame.to_long(keys) must be called first.'
            )
        return self._long

    @staticmethod
    def from_lab_notebook(notebook: LabNotebook):
        return LabDataFrame(notebook.dataframe())

    def to_long(self, ts_keys: List[str]):
        """
        Convert to long format data frame
        :param ts_keys: List of time series keys for the data frame,
        e.g. SIR.INFECTED
        """

        num_experiments = len(self._df)
        experiment_ids = self._df.index.tolist()

        # lists that will hold the values for the long data frame
        ls_experiment_id = []  # experiment id
        ls_time = []  # time step
        ls_keys = []  # what the value refers to, e.g. a compartment
        ls_value = []  # the value of the observation

        # time steps of the observations
        time_steps = self._get_time_steps()
        num_observations = len(time_steps)

        # for each key, fill the lists
        for key in ts_keys:
            # data frame with time series
            ts = self._get_key_df(key, time_steps)

            # put the data into the `value` column
            ls_value += reduce(lambda a, b: a + b, ts.values.tolist())

            # fill in the experiment IDs ...
            ls_experiment_id += [
                experiment_ids[i] for i in range(num_experiments)
                for _ in range(num_observations)
            ]

            # ... and the key
            ls_keys += [key] * num_experiments * len(time_steps)

            # ... and the time steps
            ls_time += time_steps * num_experiments

        self._long = pd.DataFrame({
            'experiment_id': ls_experiment_id,
            'time': ls_time,
            'key': ls_keys,
            'value': ls_value
        })

        return self._long

    def _get_time_steps(self) -> list:
        """
        Extract the time steps of the observations.
        :return: List of observation time steps
        """
        longest_obs = (self._df[Monitor.OBSERVATIONS].apply(len) ==
                       self._df[Monitor.OBSERVATIONS].apply(len).max())

        return self._df.loc[longest_obs].iloc[0][Monitor.OBSERVATIONS]

    def _get_key_df(self, ts_key, time_steps):
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
        Apply the `func` callable to the long data frame.
        :param func: A callable to be applied to the dataframe
        :return: The data frame grouped by time and key with the `func` applied.
        """
        raise NotImplementedError
        # grouped = self.long.groupby(['time', 'key']).mean()
        # grouped.reset_index(level=0, drop=True, inplace=True).reset_index(
        #     inplace=True)
        # return grouped

    def group_mean(self):
        """
        Calculate the mean value per time per key column of the long df.
        """
        # return self.group_apply(np.mean)
        grouped = self.long.groupby(['time', 'key']).mean()
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)
        return grouped

    def group_std(self):
        """
        Standard deviation per time per value in key column of the long df.
        :return:
        """
        # return self.group_apply(np.std)
        grouped = self.long.groupby(['time', 'key']).std()
        grouped.reset_index(inplace=True)
        grouped.drop(['experiment_id'], axis=1, inplace=True)
        return grouped
