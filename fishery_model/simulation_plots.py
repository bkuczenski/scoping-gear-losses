from .gear_loss_estimators import total_across, unit_samples, unit_diss, total_operation

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_style('darkgrid')

def _set_all_xlims(axen):
    _x = ()
    for ax in axen:
        ax.set_yticks([])
        _xl = ax.get_xlim()
        if _x == ():
            _x = _xl
        else:
            _x = [min([_x[0], _xl[0]]), max([_x[1], _xl[1]])]
    print(_x)
    for ax in axen:
        ax.set_xlim(_x)

_element = 'poly'  # or 'step'

_total_fig = 'dissipation-to-ocean.pdf'
_int_fig = 'gear-diss-intensity.pdf'


def total_dissipation_fig(study):
    # TODO: Make these persistent (probably as part of study) so that they don't need to get recomputed
    dfll = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='drifting_longlines')})
    dftw = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='trawlers')})
    dfsn = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='seiners')})

    sgn = next(study.proxy_sets('set_gillnets'))
    fad = next(study.proxy_sets('FADs'))

    # This is facet a of 4-facet plot with shared x axis
    f = plt.figure(figsize=(8, 6))

    ax1 = plt.subplot(5, 1, 1)
    sns.histplot(dftw, element=_element, log_scale=True, bins=100, ax=ax1)
    ax1.set_ylabel('trawlers')
    ax2 = plt.subplot(5, 1, 2)
    sns.histplot(dfsn, element=_element, log_scale=True, bins=160, ax=ax2)
    ax2.set_ylabel('seiners')
    ax3 = plt.subplot(5, 1, 3)
    sns.histplot(dfll, element=_element, log_scale=True, bins=100, ax=ax3)
    ax3.set_ylabel('long line')
    ax4 = plt.subplot(5, 1, 4)
    sns.histplot({'set gillnets': total_across(sgn)}, element=_element, log_scale=True, bins=160, ax=ax4)
    ax4.set_ylabel('set gillnets')
    ax5 = plt.subplot(5, 1, 5)
    sns.histplot({'tuna p.s. drifting FADs': total_across(fad)}, element=_element, log_scale=True, bins=160, ax=ax5,
                 color=[0, 0.6, 0])
    ax5.set_ylabel('dFADs')
    _set_all_xlims([ax1, ax2, ax3, ax4, ax5])
    ax5.set_xlabel('Total apparent dissipation to ocean (kg) - 2018')
    for ax in ax1, ax2, ax3, ax4:
        ax.set_xticklabels([])
    return f





def dissipation_w_op_fig(study):
    """
    This figure is no good-- too duplicative of the dissipation figure, and the proxy gear operation results
    don't make sense
    """

    def _axen(_gear, _row, _a, _b, bins=100):
        _ri = _row * 2
        _axl = plt.subplot(5, 2, _ri - 1)
        sns.histplot(_a, element=_element, log_scale= True, bins=bins, ax=_axl)
        _axl.set_ylabel(_gear)

        _axr = plt.subplot(5, 2, _ri)
        sns.histplot(_b, element=_element, log_scale=True, bins=bins, ax=_axr)
        _axr.set_ylabel(_gear)

        return _axl, _axr

    # TODO: Make these persistent (probably as part of study) so that they don't need to get recomputed
    dfll = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='drifting_longlines')})
    dftw = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='trawlers')})
    dfsn = pd.DataFrame({'tau %s' % k.tau: total_across(k) for k in study.result_sets(gear='seiners')})

    goll = pd.DataFrame({'tau %s' % k.tau: total_operation(k) for k in study.result_sets(gear='drifting_longlines')})
    gotw = pd.DataFrame({'tau %s' % k.tau: total_operation(k) for k in study.result_sets(gear='trawlers')})
    gosn = pd.DataFrame({'tau %s' % k.tau: total_operation(k) for k in study.result_sets(gear='seiners')})

    sgn = next(study.proxy_sets('set_gillnets'))
    fad = next(study.proxy_sets('FADs'))

    # This is facet a of 4-facet plot with shared x axis
    f = plt.figure(figsize=(12, 7.5))

    ax1, ax2 = _axen('trawlers', 1, gotw, dftw)
    ax3, ax4 = _axen('seiners', 2, gosn, dfsn, bins=160)
    ax5, ax6 = _axen('long line', 3, goll, dfll)
    ax7, ax8 = _axen('set gillnets', 4,
                     {'set gillnets': total_operation(sgn)},
                     {'set gillnets': total_across(sgn)}, bins=160)
    ax9, ax10 = _axen('dFADs', 5,
                     {'tuna p.s. drifting FADs': total_operation(fad)},
                     {'tuna p.s. drifting FADs': total_across(fad)}, bins=160)


    _set_all_xlims([ax1, ax3, ax5, ax7, ax9])
    _set_all_xlims([ax2, ax4, ax6, ax8, ax10])
    ax9.set_xlabel('Total gear operation (kg*h) - 2018')
    ax10.set_xlabel('Total apparent dissipation to ocean (kg) - 2018')

    for ax in (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8):
        ax.set_xticklabels([])

    return f



def intensity_fig(study):
    # TODO: Make these persistent (probably as part of study) so that they don't need to get recomputed
    usll = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='drifting_longlines')})
    ustw = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='trawlers')})
    ussn = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='seiners')})

    udll = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='drifting_longlines')})
    udtw = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='trawlers')})
    udsn = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='seiners')})

    def _axen(_gear, _row, _a, _b):
        _ri = _row * 2
        _axl = plt.subplot(5, 2, _ri - 1)
        sns.histplot(_a, element=_element, log_scale=True, ax=_axl, fill=False)
        _axl.set_ylabel(_gear)

        _axr = plt.subplot(5, 2, _ri)
        sns.histplot(_b, element=_element, log_scale=True, ax=_axr, fill=False)
        _axr.set_ylabel(_gear)

        return _axl, _axr

    sgn = next(study.proxy_sets('set_gillnets'))
    fad = next(study.proxy_sets('FADs'))

    # This is facet a of 4-facet plot with shared x axis
    f = plt.figure(figsize=(12, 7.5))

    ax1, ax2 = _axen('trawlers', 1, ustw, udtw)
    ax3, ax4 = _axen('seiners', 2, ussn, udsn)
    ax5, ax6 = _axen('long line', 3, usll, udll)
    ax7, ax8 = _axen('set gillnets', 4,
                     {'set gillnets': unit_samples(sgn)},
                     {'set gillnets': unit_diss(sgn)})
    ax9, ax10 = _axen('dFADs', 5,
                      {'tuna p.s. drifting FADs': unit_samples(fad)},
                      {'tuna p.s. drifting FADs': unit_diss(fad)})

    _set_all_xlims([ax1, ax3, ax5, ax7, ax9])
    _set_all_xlims([ax2, ax4, ax6, ax8, ax10])
    ax9.set_xlabel('Gear Usage Intensity (kg*year / tonne capture) - 2018')
    ax10.set_xlabel('Dissipation intensity (kg / tonne capture) - 2018')

    for ax in (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8):
        ax.set_xticklabels([])

    return f


def run_plots(study, total_fig=_total_fig, int_fig=_int_fig):
    total_dissipation_fig(study)
    plt.savefig(total_fig, bbox_inches='tight')

    intensity_fig(study)
    plt.savefig(int_fig, bbox_inches='tight')
