
##FAO family of functions
##This scripts contains all the funstions needed to clean, use and query the fao fisheries landings data base. This group of functions are unde the `fao_` family.

##get and clean the FAO data
fao_data_ <- NULL

get_fao_landings <- function(year_query =NULL,
                             include_inland = FALSE,
                             include_aquaculture = FALSE) {
  if(is.null(fao_data_)) {
    fao_data_ <- read_csv(here::here("data/fao_landings/fao_global_production_1950_2018.csv"))
  }
  fao_landings <- fao_data_ %>%
    rename(country = "Country (Country)",
           species = "ASFIS species (ASFIS species)",
           fishing_area_name = "FAO major fishing area (FAO major fishing area)",
           production_source = "Detailed production source (Detailed production source)",
           unit = "Unit (Unit)") %>%
    #select(1:5, 66:71) %>% ##Note this line select years from 2010 to 2015
    gather(key = year, value = landings, 6:74) %>%
    mutate(landings = ifelse(landings == "...", NA, landings)) %>%
    mutate(landings = str_remove(landings, "[A-Z]+")) %>%
    mutate(landings = str_trim(landings, side = "both")) %>%
    mutate(landings = as.numeric(landings)) %>%
    mutate(year = as.numeric(year)) %>%
    mutate(species = str_to_lower(species)) %>%
    mutate(species = str_remove(species, "\\[")) %>%
    mutate(species = str_remove(species, "\\]")) %>% ## Remove brackets from species that their en_name is thier sci_name
    filter(!str_detect(country, "Totals"),
           unit != "Number")

  if(!include_inland) {
    fao_landings <- dplyr::filter(fao_landings,
                                  !str_detect(fishing_area_name, "Inland waters"))
  }
  if(!include_aquaculture) {
    fao_landings <- dplyr::filter(fao_landings,
                                  production_source=="Capture production")
  }


  if(!is.null(year_query)) {
    print("filtering")
    print(count(fao_landings))

    fao_landings <- fao_landings %>% dplyr::filter(year == year_query)
    print(count(fao_landings))
  }
  print(count(fao_landings))
  #print(unique(fao_landings$year))
  return(fao_landings)
}



##fao_all_names() -- This functions reads in the fao clean data and joins it to the country master table and species master table.
##It does not need any input and it's outcome is the fao clean data joined to the maaster country and the fao master species


fao_all_names <- function(fao_data) {

  master_countries <- read_csv(here::here("mapping_tables/master_countries.csv"))

  fao_master_species <- read_csv(here::here("mapping_tables/master_species_fao_landings.csv"))

  fao_fishing_areas <- read_csv(here::here("mapping_tables/fao_fishing_areas.csv"))

  fao_clean <- fao_data %>%
    rename(fao_landing_c_name = country) %>%
    left_join(master_countries, by = "fao_landing_c_name") %>%
    left_join(fao_master_species, by= "species") %>%
    left_join(fao_fishing_areas, by = "fishing_area_name")



  return(fao_clean)
}

##test
# fao_clean <- get_fao_landings() %>%
#   fao_all_names()


## fao_catch_by_x: Queries FAO landing data by year, country and/or species.
## year_data = to any year from 1950 to 2018
## country = flag using ISO 3 letters in quotations
## species_data = common name as in the FAO landing landing data
## Input_data = fao "clean" data to process

##NOTES: As for now you always have to define a year



fao_catch_by_x <- function(year_data =NULL,
                           country = NULL,
                           species_data = NULL,
                           input_data = NULL){ #

  fao_clean <- input_data


  if(is.null(species_data)) {
    print("Grouped by country and year")

    fao_by_country_year <- fao_clean %>%
      group_by(iso3_code, year) %>%
      summarise(landings_total = sum(landings, na.rm = T))

    total_country_year <- fao_by_country_year %>%
      filter(iso3_code == country,
             year == year_data)

    return(total_country_year)
  }


  else if (is.null(country)) {

    print("Grouped by species")

    fao_by_species_year <- fao_clean %>%
      group_by(year, species) %>%
      summarise(landings_total = sum(landings, na.rm = T))

    total_year_species <- fao_by_species_year %>%
      filter(year == year_data,
             species == species_data)

    return(total_year_species)

    }

  else {
    print("Grouped by species, country and year")

    fao_by_species_country_year <- fao_clean %>%
      group_by(year, species, iso3_code) %>%
      summarise(landings_total = sum(landings, na.rm = T))

    total_species_country_year <- fao_by_species_country_year %>%
      filter(year == year_data,
             species == species_data,
             iso3_code == country)

    return(total_species_country_year)

  }


}

##test
##fao_catch_by_x(year_data = 2017, country = "CHL", input_data = fao_clean)









