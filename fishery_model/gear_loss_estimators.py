from .gfw_results import GFWResultSet, ProxyResultSet
from .tuna_ps_results import TunaDFADResultSet

from pandas import DataFrame
from itertools import chain

COLUMN_ORDER = ('Family', 'GearTypes', 'InputUnit', 'Param', 'OutputUnit', 'Scale', 'Order', 'DistType', 'DistValue')

class GearLossEstimators(object):
    """
    Container class for result objects
    """
    def __init__(self, gml, n_gfw=0, n_prox=0, **kwargs):
        self._gml = gml
        self.filters = kwargs
        self._n_gfw = n_gfw
        self._n_prox = n_prox

        self._gfw = []
        self._prox = []

        self._e = set()
        self._g = set()
        self._d = set()

    def _append_model(self, m):
        self._e.add(m.effort)
        self._g.add(m.gear)
        self._d.add(m.dissipation)

    def init_gfw_set(self, gear, effort, tau, **kwargs):
        _res = GFWResultSet(self._gml, gear, effort, tau=tau, **self.filters, **kwargs)
        _res.n = self._n_gfw
        self._gfw.append(_res)
        list(_res)
        for m in _res.models():
            self._append_model(m)
        return _res

    def init_mod_fisheries_gfw_set(self, gear, effort, tau, **kwargs):
        _res = GFWResultSet(self._gml, gear, effort, tau=tau, **self.filters)
        while 1:
            try:
                _res.next_fishery(**kwargs)
            except IndexError:
                break
        _res.n = self._n_gfw
        self._gfw.append(_res)
        list(_res)
        for m in _res.models():
            self._append_model(m)
        return _res

    def init_proxy_set(self, gear, **kwargs):
        _res = ProxyResultSet(self._gml, gear, **self.filters, **kwargs)
        _res.n = self._n_prox
        self._prox.append(_res)
        list(_res)
        for m in _res.models():
            self._append_model(m)
        return _res

    def init_dfad_set(self, gear, **kwargs):
        _res = TunaDFADResultSet(self._gml, gear, **self.filters, **kwargs)
        _res.n = self._n_prox
        self._prox.append(_res)
        list(_res)
        for m in _res.models():
            self._append_model(m)
        return _res

    @property
    def n_gfw(self):
        return self._n_gfw

    @n_gfw.setter
    def n_gfw(self, value):
        self._n_gfw = max([self._n_gfw, int(value)])
        for res in self._gfw:
            print('.')
            res.n = self._n_gfw

    @property
    def n_prox(self):
        return self._n_prox

    @n_prox.setter
    def n_prox(self, value):
        self._n_prox = max([self._n_prox, int(value)])
        for res in self._prox:
            print('.')
            res.n = self._n_prox

    @property
    def rs(self):
        return list(self._gfw + self._prox)

    @property
    def effort_models(self):
        return sorted(self._e, key=lambda x: x.family)

    @property
    def gear_models(self):
        return sorted(self._g, key=lambda x: x.family)

    @property
    def dissipation_models(self):
        return sorted(self._d, key=lambda x: x.family)

    def effort_table(self):
        return DataFrame(chain(*(_g.table() for _g in self.effort_models)), columns=COLUMN_ORDER)

    def gear_table(self):
        return DataFrame(chain(*(_g.table() for _g in self.gear_models)), columns=COLUMN_ORDER)

    def dissipation_table(self):
        return DataFrame(chain(*(_g.table() for _g in self.dissipation_models)), columns=COLUMN_ORDER)

    def result_sets(self, gear=None, effort=None, tau=None):
        for res in self._gfw:
            if gear is not None:
                if res.gear != gear:
                    continue
            if effort is not None:
                if res.effort != effort:
                    continue
            if tau is not None:
                if res.tau != tau:
                    continue
            yield res

    def proxy_sets(self, gear=None):
        for res in self._prox:
            if gear is not None:
                if res.gear != gear:
                    continue
            yield res


# Analysis Methods
# These take a result-set as input and generate lists of numeric results from the simulation samples
# n = number of samples / iterations
# N = number of fisheries


def total_across(_res):
    # total across all fisheries, for each iteration - this is total dissipated mass for the iteration
    return [sum(_res.scores(j)) for j in range(_res.n)]


def unit_samples(_res):
    # chain together all samples indicating gear intensity (will have length n * N)
    for det in chain(*(_res.details(t) for t in range(_res.n))):
        yield det['sample'].gear_kg


def unit_diss(_res):
    # chain together all samples indicating dissipation intensity (will have length n * N)
    for det in chain(*(_res.details(t) for t in range(_res.n))):
        yield det['sample'].diss_kg


# disused-- vessel number is too undercounted to use for this purpose
def vessel_samples(_res):
    # chain together gear intensity per vessel
    for det in chain(*(_res.details(t) for t in range(_res.n))):
        yield det['gear'] / det['n_vessel']
