import pandas as pd
from epyc import LabNotebook
from epydemic import Monitor


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

    def to_long(self, ts_keys: list[str]):
        """
        Convert to long format data frame
        :param ts_keys: List of time series keys for the data frame,
        e.g. SIR.INFECTED
        """

        num_experiments = len(self._df)
        experiment_ids = self._df.index.tolist()

        # lists that will hold the values that we need to fill in
        ls_experiment_id = []  # experiment id
        ls_time = []  # time step
        ls_keys = []  # what the value refers to, e.g. a compartment
        ls_value = []  # the value of the observation

        time_steps = self._get_time_steps()

        num_observations = len(time_steps)

        for key in ts_keys:
            ts = self._get_key_df(key, time_steps)
            ls_experiment_id += [
                experiment_ids[i] for i in range(num_experiments)
                for _ in range(num_observations)
            ]
            ls_keys += [key] * num_experiments * len(time_steps)
            ls_time += time_steps * num_experiments
            ls_value += sum(ts.values.tolist(), [])

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
        return pd.DataFrame(tss.values.tolist()).rename(
            columns=lambda i: time_steps[i])
