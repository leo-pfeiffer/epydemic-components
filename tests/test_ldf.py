from epydemic import SIR, Monitor, ProcessSequence, ERNetwork, StochasticDynamics
from epyc import Lab, JSONLabNotebook
from pandas import DataFrame
from lab_df import LabDataFrame
from components.compartment_curves import CompartmentCurves


def test_ldf(df, ts_keys, param_keys):
    ldf = LabDataFrame(df)

    ldf.locus_keys = ts_keys
    ldf.param_keys = param_keys

    ldf.format()
    formatted = ldf.formatted
    mean = ldf.group_mean()
    std = ldf.group_std()
    f_key = 'epydemic.SEIRWithQuarantine.p_quarantine'
    f_value = 0.5
    filtered = ldf.filter({f_key: f_value})

    fig = CompartmentCurves(formatted, mean)

    return formatted


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
    test_ldf(lab.dataframe(), keys, [])


def json():
    # file_name = 'tests/test_data/seir_mobility_pre.json'
    file_name = 'tests/test_data/seirq_plc_pre.json'
    with JSONLabNotebook(name=file_name).open() as nb:
        nb_df = nb.dataframe()

    ts_keys = [
        'epydemic.SEIR.S',
        'epydemic.SEIR.E',
        'epydemic.SEIR.I',
        'epydemic.SEIR.R',
        'epydemic.SEIR.SI',
        'epydemic.SEIR.SE'
    ]

    param_keys = [
        'epydemic.SEIRWithQuarantine.p_quarantine'
    ]

    test_ldf(nb_df, ts_keys, param_keys)


if __name__ == '__main__':
    # dataframe()   # try this with a local lab
    json()        # try this from a JSON file
    ...
