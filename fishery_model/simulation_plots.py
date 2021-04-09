from .gear_loss_estimators import total_across, unit_samples, unit_diss

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


def intensity_fig(study):
    ucll = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='drifting_longlines')})
    uctw = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='trawlers')})
    ucsn = pd.DataFrame({'tau %s' % k.tau: unit_samples(k) for k in study.result_sets(gear='seiners')})

    dsll = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='drifting_longlines')})
    dstw = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='trawlers')})
    dssn = pd.DataFrame({'tau %s' % k.tau: unit_diss(k) for k in study.result_sets(gear='seiners')})

    sgn = next(study.proxy_sets('set_gillnets'))
    fad = next(study.proxy_sets('FADs'))

    f = plt.figure(figsize=(12, 7.5))
    ax1 = plt.subplot(5, 2, 1)
    sns.histplot(uctw, element=_element, log_scale=True, bins=100, ax=ax1)
    ax1.set_ylabel('trawlers')
    ax3 = plt.subplot(5, 2, 3)
    sns.histplot(ucsn, element=_element, log_scale=True, bins=100, ax=ax3)
    ax3.set_ylabel('seiners')
    ax5 = plt.subplot(5, 2, 5)
    sns.histplot(ucll, element=_element, log_scale=True, bins=100, ax=ax5)
    ax5.set_ylabel('long line')
    ax7 = plt.subplot(5, 2, 7)
    sns.histplot({'Set gillnets': list(unit_samples(sgn))}, element=_element, log_scale=True, bins=100, ax=ax7,
                 color=[0, 0.6, 0])
    ax7.set_ylabel('Set gillnets')
    ax9 = plt.subplot(5, 2, 9)
    sns.histplot({'Tuna p.s. drifting FADs': list(unit_samples(fad))}, element=_element, log_scale=True, bins=100,
                 ax=ax9, color=[0, 0.6, 0])
    ax9.set_ylabel('dFADs')
    _set_all_xlims([ax1, ax3, ax5, ax7, ax9])

    ax9.set_xlabel('Gear Usage Intensity (kg*year / tonne capture) - 2018', fontsize=12)

    ax2 = plt.subplot(5, 2, 2)
    # sns.histplot(vstw, element='step', log_scale=True, bins=100, ax=ax2)
    sns.histplot(dstw, element=_element, log_scale=True, bins=100, ax=ax2)
    ax2.set_ylabel('trawlers')
    ax4 = plt.subplot(5, 2, 4)
    # sns.histplot(vssn, element='step', log_scale=True, bins=100, ax=ax4)
    sns.histplot(dssn, element=_element, log_scale=True, bins=100, ax=ax4)
    ax4.set_ylabel('seiners')
    ax6 = plt.subplot(5, 2, 6)
    # sns.histplot(vsll, element='step', log_scale=True, bins=100, ax=ax6)
    sns.histplot(dsll, element=_element, log_scale=True, bins=100, ax=ax6)
    ax6.set_ylabel('long line')
    ax8 = plt.subplot(5, 2, 8)
    # sns.histplot({'Set gillnets': list(vessel_samples(sgn))}, element='step', log_scale=True, bins=100, ax=ax8, color=[0, 0.6, 0])
    sns.histplot({'Set gillnets': list(unit_diss(sgn))}, element=_element, log_scale=True, bins=100, ax=ax8,
                 color=[0, 0.6, 0])
    ax8.set_ylabel('Set gillets')
    ax10 = plt.subplot(5, 2, 10)
    # sns.histplot({'Set gillnets': list(vessel_samples(sgn))}, element='step', log_scale=True, bins=100, ax=ax8, color=[0, 0.6, 0])
    sns.histplot({'Tuna p.s. Drifting FADs': list(unit_diss(fad))}, element=_element, log_scale=True, bins=100, ax=ax10,
                 color=[0, 0.6, 0])
    ax10.set_ylabel('dFADs')
    _set_all_xlims([ax2, ax4, ax6, ax8, ax10])

    # ax8.set_xlabel('Gear operation per GFW vessel (kg*year / vessel) - 2018', fontsize=12)
    ax10.set_xlabel('Dissipation intensity (kg / tonne capture) - 2018', fontsize=12)

    for ax in ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8:
        ax.set_xticklabels([])

    return f


def run_plots(study, total_fig=_total_fig, int_fig=_int_fig):
    total_dissipation_fig(study)
    plt.savefig(total_fig, bbox_inches='tight')

    intensity_fig(study)
    plt.savefig(int_fig, bbox_inches='tight')
