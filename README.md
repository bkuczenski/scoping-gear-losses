![](https://zenodo.org/badge/doi/10.5281/zenodo.4706051.svg)

# scoping-gear-losses
Estimation of lost fishing gear based on observed vessel activity

## Project Description
The goal of this project is to estimate the flow of fishing gear into the sea that results from normal industrial fishing activity.  We attempt to model the relationship between effort and catch by linking reports of landed fishery catch with observations of fishing effort using telemetry data from Global Fishing Watch.  We then use the resulting relationship to estimate the dissipation of fishing gear using stochastic simulation.

## Software Design

The code for organizing catch and effort data was written in R.  There are three main steps, comprised of the three files in `scripts/analysis`:
 1. `cleans_fao_datarepository.Rmd` Compute allocation factors to each logical fishery based on the Perez Roda database.
 2. `match_catch_effort.Rmd` Assign catch to fisheries and match with GFW effort data. Used to generate most of the output data used in the simulation and the paper.
 3. `quantile_reg.Rmd` Compute quantile regression results for effort intensity, used to estimate total fishing effort.

Thereafter, the effort intensity models are linked to gear intensity and dissipation models to predict gear losses.  This step happens in python using the [unit gears](https://github.com/bkuczenski/unit_gears) framework (JIE article). The code for this step is found in the `fishery_model` python package.


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
