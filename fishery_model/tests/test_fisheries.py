import unittest
from ..fishery import CATCH_EFFORT_IND

import csv

with open(CATCH_EFFORT_IND) as fp:
    dr = csv.DictReader(fp)
    fisheries = list(dr)


len_f = len(fisheries)


class TestLogicalFisheries(unittest.TestCase):
    def test_unique_fisheries(self):
        logi = set(tuple(k.get(t) for t in ('year', 'iso3_code', 'fao_area_code', 'GFWCategory')) for k in fisheries)
        self.assertEqual(len(logi), len_f)


if __name__ == '__main__':
    unittest.main()
