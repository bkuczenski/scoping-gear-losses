# Output Files

These files are generated during the execution of included software and are used to store intermediate and final results.

|File|Created in|Description |
|---|---|---|
|fao_fisheries_norm.csv| `cleans_fao_datarepository.Rmd` |Computes allocation factors for total catch by country to each logical fishery |
|total_catch_gear_sector.csv| `match_catch_effort.Rmd`| Save of `total_catch_sector` dataframe|
|catch_effort_ind.csv| `match_catch_effort.Rmd`| Catch matched to effort for GFW logical fisheries (industrial)|
|catch_effort_long.csv| `match_catch_effort.Rmd`| Effort-intensity of catch (3 metric) for each fishery, used for simulation|
|quantile_reg_results.csv| `quantile_reg.Rmd`| Quantile regression results for effort-intensity of catch by effort metric|
|**Summary Results**| | |
|method_paper_t1_total_gear8.csv|`total_catch_gear_sector_table.Rmd`| Catch by gear and sector, used in the JIE methods paper|
|vessel_activity_summary.csv|`vessel_activity_summary_table.Rmd`|A grouping of GFW data by vessel type|
|**SciAdv Results**| | |
|results_catch_effort.csv|`match_catch_effort.Rmd`|Results of the logical fishery mapping (Table 2)|
|results_catch_flows.csv|`match_catch_effort.Rmd`|Assigning catch to logical fisheries (Table 1)|
|results_effort_flows.csv|`match_catch_effort.Rmd`|Characteristics of effort data (not reported)|
|tuna_purse_seine_ind.csv|`match_catch_effort.Rmd`|Used to simulate dFAD use|




