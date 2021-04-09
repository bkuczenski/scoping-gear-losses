from fishery_model.fishery import FisheryModel
from  fishery_model.gfw_results import ProtoResultSet, FisheryResultSet

import csv


TUNA_CATCH_PS_IND = '/data/GitHub/2021/tnc-gear-data/output/tuna_purse_seine_ind.csv'


def generate_tuna_ps_ind(statistics=True, **kwargs):
    gear = 'seiners'
    yielded_n = 0
    yielded_catch = 0
    total_n = 0
    total_catch = 0
    with open(TUNA_CATCH_PS_IND) as fp:
        dr = csv.DictReader(fp)
        for d in dr:
            _tc = 0.0
            if d['GFWCategory'] != gear:
                continue
            total_n += 1
            _tc = float(d['tuna_catch'])

            total_catch += _tc

            _mini_check = True
            for key, val in kwargs.items():
                if key in d and d[key] != val:
                    _mini_check = False
            if _mini_check:
                yielded_n += 1
                yielded_catch += _tc
                yield d
    if statistics:
        print('Gear type: %s' % gear)
        if len(kwargs) > 0:
            print('\n'.join(['%s: %s' % (k, v) for k, v in kwargs.items()]))
        print('  Total: N %4d catch %g' % (total_n, total_catch))
        print('Yielded: N %4d catch %g' % (yielded_n, yielded_catch))
        print('\n')


class TunaFisheryModel(FisheryModel):

    @classmethod
    def from_tuna_ps(cls, cel):
        if 'GFWCategory' in cel:
            gear = {'GFWCategory': cel.pop('GFWCategory')}
        else:
            raise ValueError('Unknown gear mapping for this fishery spec')
        return cls(cel.pop('year'), cel.pop('iso3_code'), cel.pop('fao_area_code'), gear, cel.pop('tuna_catch'), **cel)


class TunaDFADResultSet(ProtoResultSet):
    _gfw = None
    _catch = True
    _valid_gears = ('seiners',)

    @property
    def gear_types(self):
        return {
            'FADs': ['Purse Seine Drifting FADs', 'Purse Seine Anchored FADs']
        }

    def _generate_fisheries(self, **kwargs):
        return list(generate_tuna_ps_ind(**kwargs))

    def next_fishery(self, **kwargs):
        cei = self._cei.pop(0)
        fm = TunaFisheryModel.from_tuna_ps(cei)
        frs = FisheryResultSet(fm, self.models(**kwargs))
        self.add_fishery(frs)
        self._matched.append(fm.name)
        return frs


