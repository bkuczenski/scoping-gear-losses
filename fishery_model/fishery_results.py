"""
This file stores fisheries and runs + stores simulation results

The approach here is:
"""
from unit_gears.query import GearModel
from random import randrange
from math import prod
from statistics import mean, stdev
from collections import defaultdict


class FisheryResultSet(object):
    """
    This stores a set of valid models, params, and sample results for a single fishery
    """
    def __init__(self, fishery, models, e_param=None, g_param=None, d_param=None):
        self._f = fishery
        assert all(isinstance(m, GearModel) for m in models)
        assert len(set(m.effort.catch_unit for m in models)) == 1, set(m.effort.catch_unit for m in models) # only one catch unit
        assert len(set(m.dissipation.op_unit for m in models)) == 1, set(m.dissipation.op_unit for m in models)  # only one dissipation op unit
        self._m = models
        self._ep = e_param
        self._gp = g_param
        self._dp = d_param
        self._samples = []
        self._m_ix = []

    @property
    def catch_unit(self):
        return self._m[0].effort.catch_unit

    @property
    def op_unit(self):
        return self._m[0].dissipation.op_unit

    @property
    def fishery(self):
        return self._f

    @property
    def name(self):
        return self._f.name

    @property
    def n(self):
        return len(self._samples)

    def __iter__(self):
        return self

    def _sample(self):
        ix = randrange(len(self._m))
        samp = self._m[ix].sample_long(e_param=self._ep, g_param=self._gp, d_param=self._dp)
        self._m_ix.append(ix)
        self._samples.append(samp)
        return prod(samp)

    def __next__(self):
        return self._sample()

    def sample(self, i=None):
        if i is not None:
            if int(i) < self.n:
                return prod(self._samples[int(i)])
            else:
                raise IndexError('Sample does not exist: %d' % i)
        i = self.n
        val = next(self)
        print('%d: %g' % (i, val))
        return val

    def scale(self, i):
        val = self.sample(i)
        return self._f.catch * val

    @property
    def samples(self):
        for k in self._samples:
            yield prod(k)

    def detail(self, i):
        """
        This could arguably be a results object
        :param i:
        :return:
        """
        samp = self._samples[int(i)]
        ix = self._m_ix[int(i)]
        catch = self._f.catch
        gear = catch * samp.effort * samp.scaling_factor * samp.gear * samp.op_factor  # should op_factor be in??
        dissipation = catch * prod(samp)
        return {
            'name': self._f.name,
            'n_vessel': self._f.n_vessels,
            'model': self._m[ix],
            'catch': catch,
            'sample': samp,
            'gear': gear,  # per dissipation unit
            'dissipation': dissipation
        }

    def summary(self):
        catch = self._f.catch
        effort = [samp.effort for samp in self._samples]
        gear = [samp.gear_kg for samp in self._samples]
        diss = [samp.diss_kg for samp in self._samples]
        r = {
            'name': self._f.name,
            'country': self._f.country,
            'year': self._f.year,
            'FAO region': self._f.fao,
            'catch': self._f.catch,
            'catch_unit': self.catch_unit,
            'op_unit': self.op_unit
        }
        if len(gear) > 0:
            r.update({
                'effort': catch * mean(effort),
                'effort_stdev': catch * stdev(effort),
                'gear_kg': catch * mean(gear),
                'gear_kg_stdev': catch * stdev(gear),
                'diss_kg_t': mean(diss),
                'diss_kg': catch * mean(diss),
                'diss_kg_stdev': catch * stdev(diss),
            })
        return r


class GearGroupResults(object):
    """
    This keeps a list of FisheryResults, runs their samples, and aggregates the results

    API:
    properties:
    N - number of fisheries
    n - number of MCS samples for each fishery
    total_catch - returns a dict of catch unit: amount
    __getitem__ - index into a sequential list of
    """
    def __init__(self):
        self._frs = []
        self._names = dict()
        self._n = 0
        self._total_catch = defaultdict(float)

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, val):
        while int(val) > self.n:
            self.sample()

    @property
    def N(self):
        return len(self._frs)

    @property
    def total_catch(self):
        return dict(self._total_catch)

    def _update_frs(self, frs):
        while frs.n < self.n:
            next(frs)

    def add_fishery(self, frs):
        assert isinstance(frs, FisheryResultSet)
        assert frs.name not in self._names
        i = self.N
        self._frs.append(frs)
        self._total_catch[frs.catch_unit.name] += frs.fishery.catch
        self._names[frs.name] = i
        self._update_frs(frs)

    def unit_scores(self, i):
        if int(i) < self.n:
            return [f.sample(i) for f in self._frs]
        else:
            raise IndexError('Not enough samples: %d' % i)

    def scores(self, i):
        if int(i) < self.n:
            return [f.scale(i) for f in self._frs]  # should be equivalent to [f.detail(i)['dissipation'] for f in _frs]

    def operation(self, i):
        if int(i) < self.n:
            return [f.detail(i)['gear'] for f in self._frs]

    def details(self, i):
        if int(i) < self.n:
            return [f.detail(i) for f in self._frs]

    def sample(self):
        self._n += 1
        for frs in self._frs:
            self._update_frs(frs)

    def total_across(self):
        """
        Returns a list of final scores
        :return:
        """
        return [sum(self.scores(j)) for j in range(self.n)]

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._frs[self._names[item]]
        return self._frs[int(item)]
