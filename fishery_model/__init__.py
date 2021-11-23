from .gear_library import gml_init
from .gear_loss_estimators import GearLossEstimators, unit_samples, total_across, total_operation

from math import floor, ceil
from statistics import median
import pandas as pd


class InputDataNotFound(Exception):
    pass


def tnc_gear_loss_params(**filters):
    try:
        gml = gml_init()
    except FileNotFoundError:
        raise InputDataNotFound('quantile_reg_results.csv missing: Run R script "3-quantile_reg.Rmd"')
    except ImportError:
        print('Try "pip install -r requirements.txt"')
        raise

    study = GearLossEstimators(gml, **filters)
    try:
        study.init_proxy_set('set_gillnets')
    except FileNotFoundError:
        raise InputDataNotFound('catch_effort_ind.csv missing: Run R script "2-match_catch_effort.Rmd"')

    try:
        study.init_dfad_set('seiners')
    except FileNotFoundError:
        raise InputDataNotFound('catch_effort_ind.csv missing: Run R script "2-match_catch_effort.Rmd"')

    study.init_gfw_set('drifting_longlines', 'total_f_hours_length', tau='0.5')
    study.init_gfw_set('drifting_longlines', 'total_f_hours_length', tau='0.7')
    study.init_gfw_set('drifting_longlines', 'total_f_hours_length', tau='0.9')

    study.init_gfw_set('seiners', 'total_f_hours_tonnage', tau='0.5')
    study.init_gfw_set('seiners', 'total_f_hours_tonnage', tau='0.7')
    study.init_gfw_set('seiners', 'total_f_hours_tonnage', tau='0.9')

    study.init_gfw_set('trawlers', 'total_f_hours_length', tau='0.5')
    study.init_gfw_set('trawlers', 'total_f_hours_length', tau='0.7')
    study.init_gfw_set('trawlers', 'total_f_hours_length', tau='0.9')

    return study



def conf_95(_data):
    _ss = sorted(_data)
    _ln = len(_ss)
    return _ss[int(floor(0.05*_ln))], _ss[int(ceil(0.95*_ln)) - 1]


def _ddd(arg, nam):
    _c5, _c95 = conf_95(arg)
    return {
        '%s_median' % nam : '%.3g' % median(arg),
        '%s_05' % nam: '%.3g' % _c5,
        '%s_95' % nam: '%.3g' % _c95
    }


def _make_pd_row(nam, tau, **kwargs):
    d = {'Gear': nam,
         'tau': tau
        }
    for k, v in kwargs.items():
        d.update(_ddd(v, k))
    return d


def run_study(n=1000, **filters):
    st = tnc_gear_loss_params(**filters)

    print('Executing gear loss study with n=%d iterations' % n)
    st.n_gfw = n
    st.n_prox = n
    return st


def simulation_table(study):
    stats = [('Trawlers', float(k.tau), k) for k in sorted(study.result_sets(gear='trawlers'), key=lambda x: x.tau)]
    stats.extend([('Seiners', float(k.tau), k) for k in sorted(study.result_sets(gear='seiners'), key=lambda x: x.tau)])
    stats.extend([('Longlines', float(k.tau), k)
                  for k in sorted(study.result_sets(gear='drifting_longlines'), key=lambda x: x.tau)])
    stats.append(('Set Gillnets', pd.NA, next(study.proxy_sets(gear='set_gillnets'))))
    stats.append(('Drifting FADs', pd.NA, next(study.proxy_sets(gear='FADs'))))
    return pd.DataFrame((_make_pd_row(k, l, unit=list(unit_samples(m)), oper=total_operation(m), diss=total_across(m)) for k, l, m in stats))


def _make_fishery_row(gear, tau, f_res):
    d = {'Country': f_res.fishery.country,
         'FAO': f_res.fishery.fao,
         'Year': f_res.fishery.year,
         'Gear': gear,
         'tau': tau}
    oper = [f_res.detail(k)['gear'] for k in range(f_res.n)]
    diss = [f_res.detail(k)['dissipation'] for k in range(f_res.n)]
    unit = [f_res.detail(k)['sample'].gear_kg for k in range(f_res.n)]

    d.update(_ddd(unit, 'unit'))
    d.update(_ddd(oper, 'oper'))
    d.update(_ddd(diss, 'diss'))
    return d


def per_fishery_table(study, gear, tau):
    result_set = next(study.result_sets(gear=gear, tau=tau))

    return pd.DataFrame((_make_fishery_row(gear, tau, result_set[k]) for k in range(result_set.N)))
