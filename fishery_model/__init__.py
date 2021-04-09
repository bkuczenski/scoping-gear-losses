from .gear_library import gml_init
from .gear_loss_estimators import GearLossEstimators


def tnc_gear_loss_params(**filters):
    gml = gml_init()
    study = GearLossEstimators(gml, **filters)
    study.init_proxy_set('set_gillnets')
    study.init_dfad_set('seiners')

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
