import os
from unit_gears.model_library import GearModelLibrary, MODELS_DIR

from .quantile_catch_effort_intensity import quantile_reg_models

CUSTOM_GEARS = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gear_data'))


LOAD_FAMILIES = (
    'Sala 2019',  # trawl meta-model
    'Deshpande 2020'
)

SAMPLE_FAMILIES = {
    'seiners': ['Avadi 2014.json', 'Laissane 2011.json', 'Laso 2017.json', 'Pravin 2016.json', 'Soldo 2019.json'],
    'trawlers': ['Hoffman 2009.json', 'Thrane 2006.json', 'Watanabe 2016.json'],
    'driftnets': ['Akyol 2012.json'],
    'drifting-longlines': ['Gabr 2012.json'],
    'set-nets': ['Grimaldo 2019.json'],
}


TAU = ('0.5', '0.6', '0.7', '0.8', '0.9')


def gml_init(tau=TAU):
    _gml = GearModelLibrary(verbose=False)
    for family in LOAD_FAMILIES:
        _gml.load_family(MODELS_DIR, family)
    _gml.load_path(CUSTOM_GEARS, verbose=True)

    for t in tau:
        print('Building regression models for tau=%s' % t)
        quantile_reg_models(_gml, tau=t)

    return _gml
