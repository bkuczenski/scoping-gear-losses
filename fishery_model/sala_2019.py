"""
Supporting file for Sala 2019 trawl model

Contains a function that accepts a fishery model as input and returns the appropriate "cluster" from the
Sala study.  Unfortunately, the mediterranean trawlers are considerably smaller than the largest-scale models, so
large-scale trawl models will be inaccurately represented here.
"""

from collections import namedtuple

from .fishery import EFF_MAP


ClusterModel = namedtuple('ClusterModel', ('name', 'LOA', 'hp', 'GRT'))

clusters_list = [ClusterModel('Cluster 1', 8.19, 368.3, 42.88),
                 ClusterModel('Cluster 2', 15.33, 634.1, 87.53),
                 ClusterModel('Cluster 3', 19.77, 1345, 219.1),
                 ClusterModel('Cluster 4', 14.44, 1102, 65.11)]

mapping = {
    'Vessel length in meters': ('LOA', 1.0),
    'Gross Tonnage of vessel': ('GRT', 1.0),
    'Kilowatt of engine capacity': ('hp', 1.34)
}

for k, v in EFF_MAP.items():
    mapping[k] = mapping[v]


def _order_clusters(arg):
    if arg not in ('LOA', 'hp', 'GRT'):
        raise ValueError(arg)
    return sorted(clusters_list, key=lambda x: getattr(x, arg), reverse=True)

def get_Sala_cluster(scaling_unit, scaling_value):
    try:
        arg, scl = mapping[scaling_unit]
    except KeyError:
        arg, scl = mapping[scaling_unit.name]
    clusters = _order_clusters(arg)
    for cluster in clusters:
        if getattr(cluster, arg) < scaling_value * scl:
            return cluster.name
    return clusters[-1].name
