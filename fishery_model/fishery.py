import os
import csv
from collections import namedtuple

# from unit_gears.stages import CatchEffort
# from unit_gears.base_models import PolynomialModel
from unit_gears.gear_mapping import validate_gear_types

# from .gear_library import gml


Operation = namedtuple('Operation', ('fishing_hours', 'hours', 'days'))


CATCH_EFFORT_IND = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', 'output', 'catch_effort_ind.csv'))


EFF_MAP = {
    'total_f_hours_kw': 'Kilowatt of engine capacity',
    'total_f_hours_length': 'Vessel length in meters',
    'total_f_hours_tonnage': 'Gross Tonnage of vessel'
}


EFF_MAP_r = {v: k for k, v in EFF_MAP.items()}


def generate_fisheries(gear, statistics=True, gfw=True, catch=True, **kwargs):
    """
    We also want to generate some scoping statistics.  Records in CATCH_EFFORT_IND are of 3 types:
    1 - nonzero catch, nonzero effort: an affirmative match was found between fishery library and GFW observations
    2 - nonzero catch, zero effort: no GFW match was found
    3 - zero catch, nonzero effort: no fishery model was found
    :param gear:
    :param statistics: [True] whether to print coverage statistics after the generator completes
    :param gfw: [True] only return results with GFW match (default)
                [False] only return results without GFW match
                [None] return both
    :param catch: [True] only return results with catch allocation (default)
                  [False] only return results without catch allocation
                  [None] return both
    :param kwargs:
    :return:
    """
    yielded_n = 0
    yielded_hours = 0
    yielded_catch = 0
    total_n = 0
    total_hours = 0
    total_catch = 0
    with open(CATCH_EFFORT_IND) as fp:
        dr = csv.DictReader(fp)
        for d in dr:
            _th = 0.0
            _tc = 0.0
            if d['GFWCategory'] != gear:
                continue
            total_n += 1
            if d['total_catch_gfw_cat'] == 'NA':
                # class 3
                _th = float(d['total_hours']) # no entries with NA catch AND NA hours
                total_hours += _th
                if catch is True:
                    continue  # we always skip entries with no catch
            else:
                _tc = float(d['total_catch_gfw_cat'])
                total_catch += _tc
                if d['total_f_hours'] == 'NA':
                    # class 2
                    if gfw is True:
                        continue
                else:
                    # class 1
                    _th = float(d['total_hours'])
                    total_hours += _th
                    if gfw is False:
                        continue
                if catch is False:
                    continue

            _mini_check = True
            for key, val in kwargs.items():
                if key in d and d[key] != val:
                    _mini_check = False
            if _mini_check:
                yielded_n += 1
                yielded_hours += _th
                yielded_catch += _tc
                yield d
    if statistics:
        print('Gear type: %s' % gear)
        if len(kwargs) > 0:
            print('\n'.join(['%s: %s' % (k, v) for k, v in kwargs.items()]))
        print('  Total: N %4d catch %g hours %g' % (total_n, total_catch, total_hours))
        print('Yielded: N %4d catch %g hours %g' % (yielded_n, yielded_catch, yielded_hours))
        print('\n')


OP_EQUIV_DICT = dict()


def op_equiv_by_gear(gear, statistics=False, **kwargs):
    """
    Constructs an operation unit equivalence dictionary based on real statistics reported in catch_effort_ind
    Assumes a unit of 1 fishing hour; reports equivalencies for operating hours, day of operation, year of operation.
    Performs a flat average-- adds together total hours, total fishing hours, total days, and divides each by
    total number of vessels
    :param gear:
    :param statistics: whether to display coverage statistics
    :return:
    """
    if gear not in OP_EQUIV_DICT or len(kwargs) > 0:
        print('Generating operation-equivalency data for %s' % gear)
        f_recs = list(generate_fisheries(gear, statistics=statistics, **kwargs))
        n_vessels = sum(float(k['n_vessel']) for k in f_recs)
        f_hour = sum(float(k['total_f_hours']) for k in f_recs)
        hour = sum(float(k['total_hours']) for k in f_recs)
        day = sum(float(k['total_days']) for k in f_recs)
        gd = {
            'Fishing hour': 1.0,
            'Hour of operation': hour / f_hour,
            'Day of operation': day / f_hour,
            'Year of operation': n_vessels / f_hour
        }
        if len(kwargs) == 0:  # store it if created with no args
            OP_EQUIV_DICT[gear] = gd
        return gd
    return OP_EQUIV_DICT[gear]


def _float_or_na(val):
    if val is None or val == 'NA':
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


class FisheryModel(object):
    """
    A fishery model has an effort intensity model embedded in it and is used to accumulate simulation results

    def _format_effort_intensity_dict(qrr, gear, effort):
    effort_short = re.sub('^total_f_hours_', '', effort, flags=re.I)
    d = {
        "name": "GFW effort intensity | %s, %s*hours" % (gear, effort_short),
        "gear_types": {'GFWCategory': gear},
        "catch_unit": "One tonne landed catch",
        "scaling_unit": EFF_MAP[effort_short],
        "op_unit": "Fishing hour",
        "op_equiv":
    }

    """
    @classmethod
    def from_catch(cls, cel, name=None):
        """
        Use catch (without discard scale-up) instead of total capture
        :param cel:
        :param name:
        :return:
        """
        if 'GFWCategory' in cel:
            gear = {'GFWCategory': cel.pop('GFWCategory')}
        else:
            raise ValueError('Unknown gear mapping for this fishery spec')
        fm = cls(cel.pop('year'), cel.pop('iso3_code'), cel.pop('fao_area_code'), gear, cel.pop('total_catch_fishery'),
                 fishing_hours=cel.pop('total_f_hours'), hours=cel.pop('total_hours'), days=cel.pop('total_days'),
                 name=name, n_vessels=cel.pop('n_vessel'), **cel)
        return fm

    @classmethod
    def from_observed_effort(cls, cel, effort_proxy, name=None):
        if 'GFWCategory' in cel:
            gear = {'GFWCategory': cel.pop('GFWCategory')}
        else:
            raise ValueError('Unknown gear mapping for this fishery spec')
        fm = cls(cel.pop('year'), cel.pop('iso3_code'), cel.pop('fao_area_code'), gear, cel[effort_proxy],
                 fishing_hours=cel.pop('total_f_hours'), hours=cel.pop('total_hours'), days=cel.pop('total_days'),
                 name=name, n_vessels=cel.pop('n_vessel'), **cel)
        return fm

    @classmethod
    def from_catch_effort(cls, cel, name=None):
        if 'GFWCategory' in cel:
            gear = {'GFWCategory': cel.pop('GFWCategory')}
        else:
            raise ValueError('Unknown gear mapping for this fishery spec')
        fm = cls(cel.pop('year'), cel.pop('iso3_code'), cel.pop('fao_area_code'), gear, cel.pop('total_catch_gfw_cat'),
                 fishing_hours=cel.pop('total_f_hours'), hours=cel.pop('total_hours'), days=cel.pop('total_days'),
                 name=name, n_vessels=cel.pop('n_vessel'), **cel)
        return fm

    '''
    @classmethod
    def from_gfw_regression(cls, cel, qr, name=None):  # outmoded
        """
        Main objective here is to construct an effort intensity model from the data
        :param cel:
        :param qr: the quantile regression model as a list of coefficients
        :param name: optional
        :return:
        """
        """
        for CatchEffort we need:
        family, name, gear_types, catch_unit, scaling_unit, op_unit, effort_model, op_equiv, documentation
        
        we take our regression, which provides a relationship between scaling parameter and log(effort/catch) [base 10]
        Both the intercept and slope have variability bounds.  What that means is that we should actually code them
        up and simulate them for the fishery INSTANCE.
        """
        fm = cls.from_catch_effort(cel, name=name)

        eff = cel['effort_type']
        param = float(cel['effort_moment'])

        assert all(eff == k['effort_type'] for k in qr)
        model = PolynomialModel(*(('normal', float(k['value']), float(k['std_error'])) for k in qr), scale='log10')

        doc_string = 'GFW Catch-effort regression'
        for k in ('effort_type', 'effort_moment', 'slope', 'slope_log'):
            doc_string = '\n'.join([doc_string, '%s: %s' % (k, cel[k])])
        for i, k in enumerate(qr):
            doc_string = '\n'.join([doc_string,
                                    '; '.join(['%s: %g' %(key, float(k[key]))
                                               for key in ('value', 'std_error', 't_value', 'pr_t')])])

        # doc_string = '\n'.join([doc_string, 'Computed slope_log: %g' % slope_log, 'Computed slope: %g' % slope])


        ce = CatchEffort('GFW-%s' % eff, fm.name, fm.gear_types,
                         gml.get_quantity('One tonne landed catch', measure='catch'),
                         gml.get_quantity(EFF_MAP[eff], measure='scaling'),
                         gml.get_quantity('Fishing hour', measure='operation'),
                         param_unit=gml.get_quantity(EFF_MAP[eff], measure='scaling'),
                         effort_model=model, effort_param=param, op_equiv=fm.op_equiv, documentation=doc_string)
        fm.effort = ce
        return fm
    '''

    def __init__(self, year, country, fao_area, gear, total_catch,
                 name=None,
                 fishing_hours=None,
                 hours=None,
                 days=None,
                 n_vessels=None,
                 **kwargs):
        """

        :param year:
        :param country:
        :param fao_area:
        :param gear:
        :param total_catch:
        :param name:
        :param fishing_hours:
        :param hours:
        :param days:
        :param n_vessels:
        :param effort_model:
        :param effort_param:
        :param kwargs:
        """
        self.year = int(year)
        self.country = country
        self.fao = fao_area
        self._gear_ec = set(validate_gear_types(gear))
        self._gear = gear
        self._catch = float(total_catch)

        self._name = name
        self._op = Operation(*(_float_or_na(k) for k in (fishing_hours, hours, days)))  # for convenience
        self._nv = int(_float_or_na(n_vessels))

        self.args = kwargs

    @property
    def name(self):
        if self._name is None:
            return '%d-%s-%s-FAO %s' % (self.year, self.country, self.gear_names, self.fao)
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            self._name = None
        else:
            self._name = str(value)

    @property
    def gear_types(self):
        return self._gear

    @property
    def gear_names(self):
        return '_'.join(set(v for v in self._gear.values()))

    @property
    def gear_ec(self):
        return self._gear_ec

    @property
    def catch(self):
        return float(self._catch or 1.0)

    @property
    def avg_fishing_hours(self):
        return self._op.fishing_hours / self.n_vessels

    @property
    def avg_total_hours(self):
        return self._op.hours / self.n_vessels

    @property
    def avg_days(self):
        return self._op.days / self.n_vessels

    @property
    def op_equiv(self):
        d ={'Fishing hour': 1.0}
        if self.avg_fishing_hours != 0:
            d["Year of operation"] = 1.0 / self.avg_fishing_hours
            if self.avg_total_hours != 0:
                d['Hour of operation'] = self.avg_total_hours / self.avg_fishing_hours
            if self.avg_days != 0:
                d['Day of operation'] = self.avg_days / self.avg_fishing_hours
        return d

    def effort_moment(self, effort_type):
        if self._op.fishing_hours == 0.0:
            return 0.0
        if effort_type in self.args:
            return float(self.args[effort_type]) / self._op.fishing_hours
        elif effort_type in EFF_MAP_r:
            return float(self.args[EFF_MAP_r[effort_type]]) / self._op.fishing_hours
        return 0.0

    @property
    def n_vessels(self):
        return self._nv or 1
