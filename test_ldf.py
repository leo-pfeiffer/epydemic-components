from epydemic import SIR, Monitor, ProcessSequence, ERNetwork, StochasticDynamics
from epyc import Lab, JSONLabNotebook
from pandas import DataFrame
from lab_df import LabDataFrame


def test_ldf(df, keys):
    ldf = LabDataFrame(df)
    ldf.to_long(keys)
    long = ldf.long
    return long


def dataframe():
    lab = Lab()

    N = int(1e4)
    kmean = 10

    lab[ERNetwork.N] = N
    lab[ERNetwork.KMEAN] = kmean
    lab[SIR.P_INFECTED] = 0.01
    lab[SIR.P_INFECT] = 0.001
    lab[SIR.P_REMOVE] = 0.01
    lab[Monitor.DELTA] = 1
    lab['repetitions'] = range(5)

    e = StochasticDynamics(ProcessSequence([SIR(), Monitor()]), ERNetwork())
    lab.runExperiment(e)

    keys = [SIR.INFECTED]
    test_ldf(lab.dataframe(), keys)


def json():
    with JSONLabNotebook(name='seir_mobility_pre.json').open() as nb:
        nb_df = nb.dataframe()

    keys = [
        'epydemic.SEIR.S',
        'epydemic.SEIR.E',
        'epydemic.SEIR.I',
        'epydemic.SEIR.R',
        'epydemic.SEIR.SI',
        'epydemic.SEIR.SE'
    ]

    test_ldf(nb_df, keys)


if __name__ == '__main__':
    # dataframe()   # try this with a local lab
    # json()        # try this from a JSON file
    ...
