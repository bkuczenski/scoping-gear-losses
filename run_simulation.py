from fishery_model import tnc_gear_loss_params, simulation_table

import argparse

import os
from csv import QUOTE_ALL

diss_to_ocean_fig = os.path.join('output', 'simulation', 'Dissipation-to-ocean_script.pdf')
gear_intensity_fig = os.path.join('output', 'simulation', 'Gear-diss-intensity-fad_script.pdf')
results_csv = os.path.join('output', 'simulation', 'gear_diss_results_script.csv')


parser = argparse.ArgumentParser(description='Run Gear Loss Simulations')
parser.add_argument('-n', action='store', default=1000, type=int)
parser.add_argument('-f', action='store_true')


def run_study(n=1000):
    st = tnc_gear_loss_params()

    print('Executing gear loss study with n=%d iterations' % n)
    st.n_gfw = n
    st.n_prox = n
    return st


if __name__ == '__main__':
    args = parser.parse_args()
    study = run_study(n=args.n)

    tab = simulation_table(study)
    print(tab.to_latex(index=False))
    tab.to_csv(results_csv, index=False, quoting=QUOTE_ALL)

    if args.f:
        try:
            from fishery_model.simulation_plots import run_plots
            run_plots(study, total_fig=diss_to_ocean_fig, int_fig=gear_intensity_fig)
        except ImportError:
            print('Unable to generate plots-- try "pip install seaborn"')
