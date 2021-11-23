![](https://zenodo.org/badge/doi/10.5281/zenodo.4706051.svg)

# scoping-gear-losses
Estimation of lost fishing gear based on observed vessel activity

**Note: the `main` branch does not include results!**

Please checkout `populated` to find output files in the `output` folder-- or run the code according to the instructions below to regenerate them from inputs.

## Project Description
The goal of this project is to estimate the flow of fishing gear into the sea that results from normal industrial fishing activity.  We attempt to model the relationship between effort and catch by linking reports of landed fishery catch with observations of fishing effort using telemetry data from Global Fishing Watch.  We then use the resulting relationship to estimate the dissipation of fishing gear using stochastic simulation.

## Software Design

The code for organizing catch and effort data was written in R.  There are three main steps, comprised of the three files in `scripts/analysis`:
 1. `cleans_fao_datarepository.Rmd` Compute allocation factors to each logical fishery based on the Perez Roda database.
 2. `match_catch_effort.Rmd` Assign catch to fisheries and match with GFW effort data. Used to generate most of the output data used in the simulation and the paper.
 3. `quantile_reg.Rmd` Compute quantile regression results for effort intensity, used to estimate total fishing effort.

Thereafter, the effort intensity models are linked to gear intensity and dissipation models to predict gear losses.  This step happens in python using the [unit gears](https://github.com/bkuczenski/unit_gears) framework ([JIE article](https://doi.org/10.1111/jiec.13156)). The code for this step is found in the `fishery_model` python package.


## To reproduce the study results

### Part 1 - Catch and Effort Modeling

This section is executed in R. We recommend Rstudio. This code requires the data present in the `data` directory and populates CSV files in `output`. Note: for access to the pre-computed outputs, checkout the **populated** branch.

 1. Open the R project file in the present directory.
 2. Source "R/set_up.R" Required packages should be installed automatically.
 3. In sequence, run the scripts in the `scripts/analysis` directory:
    1. cleans_fao_datarepository.Rmd
    2. match_catch_effort.Rmd
    3. quantile_reg.Rmd
 4. If desired, review scripts in `scripts/figures_and_tables` for visualization options.

### Part 2 - Gear Loss Simulations

This section is executed in python.

 5. Create an appropriate environment for the project (python 3.6 or higher).
 6. In a shell, run `pip install -r requirements.txt`
 7. Execute `python run_simulation.py` to execute a full simulation.  Results are stored in `output/simulation` directory.
   - Use the switch `-n` to change the number of Monte Carlo iterations (default 1000)
   - Use the switch `-f` to generate figures equivalent to the publication figures.

For interactive or custom use, please review the two notebooks in the `jupyter` directory, as well as the documentation for `unit_gears`.

### Per-fishery Results

The study object can also be used for many other queries.  For instance, a table of gear use and dissipation per 
logical fishery can be produced by indexing across the result sets differently, as shown in 
`fishery_model.per_fishery_table()`:

    >>> import fishery_model
    >>> st = fishery_model.run_study(n=55, year='2018')
    >>> fishery_model.per_fishery_table(st, 'trawlers', '0.9')
         Country FAO  Year      Gear  tau unit_median unit_05 unit_95 oper_median   oper_05   oper_95 diss_median   diss_05   diss_95
    0       AGO  47  2018  trawlers  0.9        5.64    1.75    20.5     5.2e+05  1.61e+05  1.89e+06    1.66e+04  4.02e+03  7.76e+04
    1       ARG  41  2018  trawlers  0.9        4.07    1.51    17.9    4.96e+06  1.84e+06  2.18e+07    1.75e+05  6.19e+04   6.7e+05
    2       AUS  71  2018  trawlers  0.9        8.58    2.56      28    7.88e+05  2.35e+05  2.57e+06    2.39e+04   8.9e+03  8.89e+04
    3       AUS  81  2018  trawlers  0.9        7.86    2.17    19.6    1.07e+05  2.95e+04  2.67e+05    3.53e+03  1.19e+03     8e+03
    4       BEL  27  2018  trawlers  0.9        6.17    2.42    42.7    2.55e+05     1e+05  1.76e+06    9.19e+03  3.37e+03  5.05e+04
    ..      ...  ..   ...       ...  ...         ...     ...     ...         ...       ...       ...         ...       ...       ...
    108     USA  77  2018  trawlers  0.9        7.15    1.94    34.6     2.9e+04  7.85e+03   1.4e+05    1.02e+03       269   5.6e+03
    109     VNM  71  2018  trawlers  0.9        7.13    2.35    27.1    6.94e+06  2.29e+06  2.64e+07    2.35e+05  7.74e+04  1.13e+06
    110     ZAF  47  2018  trawlers  0.9        5.57    1.32    21.6    8.74e+05  2.07e+05  3.39e+06    2.61e+04  7.57e+03  1.13e+05
    111     ZAF  51  2018  trawlers  0.9        7.33    2.11    17.7    3.29e+03       948  7.95e+03        87.8      30.1       278
    112      NA  27  2018  trawlers  0.9        9.27    1.91    28.5    2.63e+03       543  8.09e+03        89.8      18.7       295
    >>>

## Repository Structure

```
-- data
   |__fao_landings
   |__gfw
   |__perez-roda_discards
   |__watson
-- doc
-- mapping_tables
-- output
   |__figures
   |__simulation
-- R
-- scripts
   |__analysis
   |__figures_and_table
   |__mapping_tables
-- .gitignore
-- .Rhistory
-- README.md
    
```

- **data:** contains all the raw data used in this part of the project organized by data source. The four main data source are: 
   - fao_landings: FAO publicly available global production
   - gfw: Global Fishing Watch vessel activity data. This data is not publicly available.
   - perez-roda_discards: publicly available data used in the FAO Third Assessment of Global discards
   - watson: Reginald Watson (2019) Global Fisheries Landings V4.0, Australian Ocean Data Network

For more detail on each data source please see [Wiki](https://github.com/bkuczenski/tnc-gear-data/wiki/data-(raw))

- **doc:** folder containing some documents related to the project.

- **mapping_tables:** all files used to re-conciliate countries, species, gear and FAO area names between data sources. This files were created for this project. Find more information about the content of these tables [here](https://github.com/bkuczenski/tnc-gear-data/wiki/Metadata:-Mapping-Tables)
   - **intermediate_files:** intermediate files used to create the countries mapping table. Files in this folder were altered manually. 
   
- **output:** contains all files created through the scripts of this project. All files can be reproduced by running one of the scripts and are part of the core results of the project, or by checking out the `populated` branch.
   
- **R:** R scripts that contain all functions needed for the project. Scripts are organized by data source.

- **scripts:** core data processing of the project.
   - **analysis:** Three main steps to reconcile catch and effort data: classify species into a logical fishery, group landings by fisheries gear type and match to effort data, analyse relationship by running multiple quantile regressions. 
   - **figures_and_tables:** scripts that create figures used in this project.
   - **mapping_table:** scripts used to create all the mapping tables used in this project. Each script documents the process and steps to create the final outcome.
