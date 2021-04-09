# import re
import csv
import os

from collections import defaultdict
from unit_gears.stages import CatchEffort
from unit_gears.base_models import PolynomialModel

from .fishery import op_equiv_by_gear, EFF_MAP


QUANTILE_REGRESSION = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '..', 'output', 'quantile_reg_results.csv'))


def _quantile_reg_model(library, tau, qr, op_equiv=None, overwrite=False):
    """

    :param library:
    :param qr: A list of quantile regression dicts, in order of increasing polynomial coefficients
    Note: intercept param is modeled as having normal uncertainty; higher-order params are static bc 10**x instability
    :return:
    """
    eff = qr[0]['effort_type']
    gear = qr[0]['gear']
    # model = PolynomialModel(('normal', float(qr[0]['estimate']), float(qr[0]['std_error'])),
    #                         *(('static', float(k['estimate'])) for k in qr[1:]), scale='log10')
    model = PolynomialModel(*(('normal', float(k['estimate']), float(k['std_error'])) for k in qr), scale='log10')
    doc_string = 'GFW Catch-effort regression'
    for k in ('gear', 'effort_type'):
        doc_string = '\n'.join([doc_string, '%s: %s' % (k, qr[0][k])])
    for i, k in enumerate(qr):
        doc_string = '\n'.join([doc_string,
                                '; '.join(['%s: %g' % (key, float(k[key]))
                                           for key in ('estimate', 'std_error', 'statistic', 'p_value')])])  # value, t-value, pr_t

    ce = CatchEffort('GFW-%s-%s-%s' % (gear, eff, tau), 'GFW Regression, %s, %s, %s' % (gear, eff, tau),
                     {'GFWCategory': gear},
                     library.get_quantity('One tonne capture', measure='catch'),
                     library.get_quantity(EFF_MAP[eff], measure='scaling'),
                     library.get_quantity('Fishing hour', measure='operation'),
                     param_unit=library.get_quantity(EFF_MAP[eff], measure='scaling'),
                     effort_model=model, op_equiv=op_equiv, documentation=doc_string)

    library.add_effort_model(ce, overwrite=overwrite)


proxy_quantities = (
    ("Kilowatt-hour proxy catch", "Kilowatt of engine capacity"),
    ("Vessel meter LOA-hour proxy catch", "Vessel length in meters"),
    ("Vessel gross tonnage-hour proxy catch", "Gross Tonnage of vessel")
)


def proxy_effort_model(library, gear, op_equiv):
    op = library.get_quantity('Fishing hour', measure='operation')
    for qty, scl in proxy_quantities:
        q = library.get_quantity(qty, measure='catch')
        family = 'GFW-proxy-%s-%s' % (gear, q.unit)
        try:
            next(library.effort_models(family=family))
        except StopIteration:
            s = library.get_quantity(scl, measure='scaling')
            ce = CatchEffort(family, 'GFW Proxy effort, %s, %s' % (gear, q.unit),
                             {'GFWCategory': gear},
                             q,
                             s,
                             op,
                             effort_model=1.0, op_equiv=op_equiv, documentation="Pass-through model for observed effort")
            library.add_effort_model(ce)


def quantile_reg_models(library, qrr=None, tau='0.8', **kwargs):
    if qrr is None:
        qrr = read_quantile_reg_results()
    for gear in qrr.keys():
        op_equiv = op_equiv_by_gear(gear, statistics=True)
        for effort in qrr[gear].keys():
            _quantile_reg_model(library, tau, qrr[gear][effort][tau], op_equiv=op_equiv, **kwargs)
        proxy_effort_model(library, gear, op_equiv)
    pass


def read_quantile_reg_results(file=QUANTILE_REGRESSION):
    with open(file) as fp:
        dr = csv.DictReader(fp)
        qrr_list = list(dr)

    efforts = set(k['effort_type'] for k in qrr_list)
    gears = set(k['gear'] for k in qrr_list)
    qrr = defaultdict(dict)
    for effort in efforts:
        for gear in gears:
            qrr[gear][effort] = defaultdict(list)

    for qr in sorted(qrr_list, key=lambda x: x['term'] != 'intercept'):
        qrr[qr['gear']][qr['effort_type']][qr['tau']].append(qr)

    return qrr

def best_regressions(qrr):
    print('Best regressions by gear:')
    for gear in qrr.keys():
        best_effort(qrr, gear)

def best_effort(qrr, gear, tau='0.8'):
    try:
        p_values = {k: [float(c['pr_t']) for c in v[tau]] for k, v in qrr[gear].items()}
    except KeyError:
        p_values = {k: [float(c['p_value']) for c in v[tau]] for k, v in qrr[gear].items()}
    best = sorted(p_values.keys(), key=lambda x: sum(p_values[x]))[0]
    print('%s: %s: %s' % (gear, best, p_values[best]))
    return best
