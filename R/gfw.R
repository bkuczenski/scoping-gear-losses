# This function requires a summary of GFW vessel data provided to the UCSB / TNC research team by Global Fishing Watch.
# The raw data are not available to the public, but the function generate_effort_bins() shows how the digest was created
# from the raw data.

source(here::here('R/set_up.R'))

## Checking Outliers

###Large vessels
#get gfw data and correct outliers
## For now, we just flag vessels with absurd engine power (>15000 kW) and re-map to a linear relationship by GFW gear class.
##This is mainly done to correct one spurious data point
corrects_gfw <- function() {  # this is incredibly hacky

  gfw_raw <- read_csv('here::here("bigdata/GFW_vessels_activity.csv")')

  gfw_corr <- gfw_raw %>%
    mutate(best_engine_power_kw = ifelse(best_engine_power_kw > 15000, NA, best_engine_power_kw)) %>%
    group_by(best_vessel_class) %>%
    do({
      lm_mod <- lm(best_engine_power_kw ~ best_length_m, data = .)
      length_kw_model <- predict(lm_mod, newdata = .[c('best_length_m')])
      data_frame(., length_kw_model)
    }) %>%
    ungroup() %>%
    mutate(best_engine_power_kw = ifelse(is.na(best_engine_power_kw), length_kw_model, best_engine_power_kw)) %>%
    select(-length_kw_model)

  return(gfw_corr)
}

##test
##gfw_clean <- corrects_gfw()

generate_effort_bins <- function() {

  gfw_corrected <- corrects_gfw()

  master_gear <- read_csv(here::here("mapping_tables/master_gear_mapping.csv"))
  
  gfw_categories <- master_gear %>%
    select(GFWClass, GFWCategory) %>%
    distinct()

  effort_bins <- gfw_corrected %>%
    rename(GFWClass = best_vessel_class,
           iso3_code = best_flag,
           fao_area_code = fao) %>%
    mutate(f_hours_length_m = fishing_hours*best_length_m,
           f_hours_gt = fishing_hours*best_tonnage_gt,
           f_hours_kw = fishing_hours*best_engine_power_kw) %>%
    filter(!is.na(fao_area_code)) %>%
    left_join(gfw_categories, by = "GFWClass") %>%
    group_by(year, iso3_code, fao_area_code, GFWCategory) %>%
    summarise(total_f_hours_length = sum(f_hours_length_m, na.rm = T),
              total_f_hours_tonnage = sum(f_hours_gt, na.rm = T),
              total_f_hours_kw = sum(f_hours_kw, na.rm = T),
              total_f_hours = sum(fishing_hours),
              total_hours = sum(hours),
              total_days = sum(fishing_days),
              n_vessel = n()) %>%
    ungroup()

  write_csv(effort_bins, here::here('data/gfw/gfw_effort_bins.csv'))
  return(effort_bins)
}




###GFW initial queries

## Function 1: total effort by scope. This functions allows us to save intermediate files effort data by different scopes (FAO regions, flag and vessel class)

total_effort <- function(.vars,
                         save_filepath = "intermediate_data/") {


  ##Summarized all effort parameters grouped by the variables determined in vars()
  effort_scope <- gfw_raw %>%
    mutate(kw_hours = best_engine_power_kw*hours,
           kw_days = best_engine_power_kw*days,
           gt_hours = best_tonnage_gt*hours,
           gt_days = best_tonnage_gt*days,
           length_hours = best_length_m*hours,
           length_days = best_length_m*days) %>%
    group_by_at(.vars) %>%
    summarise(n_vessels = n_distinct(mmsi),
              total_kw = sum(best_engine_power_kw, na.rm = T),
              total_hours = sum(hours, na.rm = T),
              total_length_m = sum(best_length_m, na.rm = T),
              total_tonnage_gt = sum(best_tonnage_gt, na.rm = T),
              total_days = sum(days, na.rm = T),
              total_kw_hours = sum(kw_hours, na.rm = T),
              total_kw_days = sum(kw_days, na.rm = T),
              total_gt_hours = sum(gt_hours, na.rm = T),
              total_gt_days = sum(gt_days, na.rm = T),
              total_length_hours = sum(length_hours, na.rm = T),
              total_length_days = sum(length_days, na.rm = T))


  return(effort_scope)

}



# To calculate the total effort per socpe, run the `total_effort()` function. In the argument include the function `dplyr::vars()` and inside the parenthesis name the variables you want the data to be grouped_by.

## Query 1
##1. **World fishig effort by vessel type** Total Efforrt per vessel class (gear type)
# Total effort by class: (count of mmsi, sum of kw, sum of length, sum of tonnage gt, sum of days, sum of fishing hours, sum of (kwhours), sum of (kwdays), sum of (tonnage hours), sum of (tonnagedays), sum of (lengthhours), sum of (lengthdays)), group by (FAO area, flag, vessel_class, year)


##query_1 <- total_effort(vars(year, mmsi, best_flag, best_vessel_class))


## Function 2: Total effort segment grouped by a specific variable. Where segment_type can be any variable (column name) of the `gfw_raw` data. Segment is any observation withing the selected segment_type

# The "..." represent any varibale of the data that we want to group_by to compute the summarize function for total_days, total_fishing_days and total hours.


total_effort_segment <- function(...,
                                 segment_type,
                                 segment) {
  ##enquoting objects this step is needed so then they can be unquote and be used as variables
  grouped <- quos(...)  ## quotes all input variables
  segment_type <- enquo(segment_type)
  segment <- enquo(segment)

  print(segment_type)
  print(segment)

  data_segment <- gfw_raw %>%
    filter(!!segment_type == !!segment) ##!! unquotes the objects so the can be read as variables

  ##Summarized all parameters grouped by the input variables
  effort_segment <- data_segment %>%
    # mutate(kw_hours = best_engine_power_kw*hours,
    #        kw_days = best_engine_power_kw*days,
    #        gt_hours = best_tonnage_gt*hours,
    #        gt_days = best_tonnage_gt*days,
    #        length_hours = best_length_m*hours,
    #        length_days = best_length_m*days) %>%
    group_by(!!!grouped) %>%
    summarise(total_fishing_days = sum(fishing_days, na.rm = T), ##CHCK!!!! THIS SHOULD BE FISHING DYAS??
              total_fishing_hours = sum(fishing_hours, na.rm = T),
              total_hours = sum(hours, na.rm = T)) %>%
    ungroup()


  return(effort_segment)

}

## Query 2: Focus on FAO region 87, southeast pacific. Sum of (days, fishing hours, total hours) group by (mmsi, flag, length, kw, tonnage, vessel class, year) where FAO area = 87
##2. For FAO area 87, sum of fishing days, hours grouped by veesel flag, length, kw, tonnage vessel classs, year


# query_2 <- total_effort_segment(year, mmsi, best_flag,best_length_m, best_engine_power_kw,best_tonnage_gt, best_vessel_class, segment_type = fao, segment = 87)


## Query 3: Focus on CHL. Sum of (days, fishing hours, total hours) group by (mmsi, FAO area, length, kw, tonnage, vessel class, year) where flag = CHL
##3. For CHL, sum of fishing days, hours grouped by veesel flag, length, kw, tonnage vessel classs, year

# query_3 <- total_effort_segment(year, mmsi, best_flag,best_length_m, best_engine_power_kw,best_tonnage_gt, best_vessel_class, segment_type = best_flag, segment = "CHL")






