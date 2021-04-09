library(tidyverse)
path <- here::here("data/watson/watson_codes.xlsx")

grab_clean_data <- function(sheet) {
  readxl::read_excel(path, sheet=sheet) %>% janitor::clean_names()
  # apparently it just returns the last thing automatically?
}

sheets <- readxl::excel_sheets(path)
watson_dd <- lapply(sheets, grab_clean_data)
watson_dd <- setNames(watson_dd, sheets)

get_gear_by_code <- function(code) {
  watson_dd$Gear %>% filter(gear == code)
}

get_gear_by_name <- function(name) {
  watson_dd$Gear %>% filter(str_detect(vb_desc, name), str_detect(fao_gear_name, name))
}

##############################################################################################

##This scripts contains all the functions needed to query the watson data base. This group of functions are under the watson_family.

##get_watson_data()

get_watson_data <- function(year_query = NULL,
                            include_ind = TRUE,
                            include_non_ind = TRUE){

  if(include_ind){

    watson_index_raw_ind <- read.csv(here::here("data/watson/watson_index_per_fishing_event_ind.csv")) %>%
      clean_names() %>%
      rename(year = i_year) %>%
      mutate(id = as.character(id)) %>%
      mutate(productive_sector = "industrial") %>%
      distinct()
  }

  if(include_non_ind){

    watson_index_raw_Nind <- read.csv(here::here("data/watson/watson_index_per_fishing_event_Nind.csv")) %>%
      clean_names() %>%
      rename(year = i_year) %>%
      mutate(id = as.character(id)) %>%
      mutate(productive_sector = "non_industrial") %>%
      distinct()
  }

  if(include_ind & include_non_ind){
    watson_index_all <- rbind(watson_index_raw_ind, watson_index_raw_Nind) %>%
      distinct() %>%
      rename(watson_country_id = c_number,
             taxon_key = taxonkey)
    return(watson_index_all)
  }

  if(include_ind & !include_non_ind){

    return(watson_index_raw_ind)
  }

  if(include_non_ind & !include_ind){

    return(watson_index_raw_Nind)
  }


}

##test
# watson_all <- get_watson_data()
# watson_ind <- get_watson_data(include_non_ind = FALSE)
# watson_non_ind <- get_watson_data(include_ind = FALSE)

##
##watson_all_names() -- This functions reads in the watson clean data and joins it to the country master table and species master table.
##It does not need any input and it's outcome is the watson clean data joined to the maaster country and watson species code.

##Note: As for now it only includes the watson taxa name!!

watson_all_names <- function(watson_data) {

  master_countries <- read_csv(here::here("mapping_tables/master_countries.csv"))

  watson_master_species <- read_csv(here::here("mapping_tables/master_species_watson_taxon.csv")) %>%
    select(taxon_key, taxon_name, common_name, isscaap_group) %>% ##this selection allows us to get one row per taxon_key
    distinct()

  watson_gear_names <- read_csv(here::here("mapping_tables/master_gear_mapping.csv")) %>%
    select(gear = WatsonGearCode, gear_name =VonBrandtDescription) %>%
    distinct(gear, .keep_all = T)

  watson_clean <- watson_data %>%
    left_join(master_countries, by = "watson_country_id") %>%
    left_join(watson_master_species, by= "taxon_key") %>%
    left_join(watson_gear_names, by = "gear")

  return(watson_clean)
}

##test
#watson_clean <- watson_all_names()



## watson_catch_by_x: Queries Watson catch data by year, fishing sector, country, and/or species.
## year_data = to any year from 1950 to 2015
## country = flag using ISO 3 letters in quotations
## taxon_type = Any taxa defined in the master_scpecies_watson_taxon.csv (taxon_key,taxon_name, common_name,scientific_name, 3alpha_code, name_en, genus, family        "major_group, isscaap_group.
## taxon_name = Any specific taxon under the defined taxon_type.

##NOTES: As for now you always have to define a year and a productive sector


##Probably it would be better to find an alternative solution for reading in the watson master species
watson_master_species <- NULL



watson_catch_by_x <- function(year_data=NULL,
                              country=NULL,
                              taxon_name = NULL,
                              taxon_type = NULL,
                              fishing_sector=NULL,
                              input_data = NULL){


  watson_clean <- input_data


  if(is.null(watson_master_species)){
    watson_master_species <- read_csv(here::here("mapping_tables/master_species_watson_taxon.csv"))
  }



 ##Computations

  if(is.null(taxon_name)) {
    print("Grouped by country, year and productive sector")

    watson_country_year_ps <- watson_clean %>%
      group_by(iso3_code, year, productive_sector) %>%
      summarise(landings_total = sum(reported, na.rm = T),
                iuu = sum(iuu_total, na.rm = T),
                discard_total = sum(discards, na.rm = T))

    total_country_year_ps <- watson_country_year_ps %>%
      filter(iso3_code == country,
             year == year_data,
             productive_sector == fishing_sector)

    ##test
    # total_country_year_ps <- watson_country_year_ps %>%
    # filter(iso3_code == "USA",
    #        year == 2010,
    #        productive_sector == "industrial")


    return(total_country_year_ps)
  }


  else if (is.null(country)) {

    print("Grouped by species group and fishing sector")

    ##Enquoting arguments. First step to be able to use them as variables
    taxon_name <- enquo(taxon_name)
    taxon_type <- enquo(taxon_type)

    ##filter all the watson taxon under the speciefied taxon name
    selected_taxa <- watson_master_species %>%
      filter(!!taxon_type == !!taxon_name)


    ##test
    # selected_taxa <- watson_master_species %>%
    #   filter(family == "penaeidae")

    print(unique(selected_taxa$name_en))

    ##Create a list with all taxon key in the specified taxon name
    taxon_list <- selected_taxa %>%
      distinct(taxon_key) %>%
      pull(taxon_key)

    ##Computetion for the corresponding taxon keys
    watson_by_species_year <- watson_clean %>%
      filter(taxon_key %in% taxon_list) %>% ##fiters for all taxa in the specified group
      group_by(year, productive_sector) %>%
      summarise(landings_total = sum(reported, na.rm = T),
                iuu = sum(iuu_total, na.rm = T),
                discard_total = sum(discards, na.rm = T))

    total_year_species <- watson_by_species_year %>%
      filter(year == year_data,
             productive_sector == fishing_sector)

    ##test
    # total_year_species <- watson_by_species_year %>%
    #   filter(year == 2010,
    #          productive_sector == "industrial")



    return(total_year_species)

  }

  else {
    print("Grouped by species, country, year and productive sector")

    ##Enquoting arguments. First step to be able to use the as variables
    taxon_name <- enquo(taxon_name)
    taxon_type <- enquo(taxon_type)

    ##filter all the watson taxon under the speciefied taxon name
    selected_taxa <- watson_master_species %>%
      filter(!!taxon_type == !!taxon_name)

    ##test
    # selected_taxa <- watson_master_species %>%
    #   filter(family == "penaeidae")

    print(unique(selected_taxa$name_en))

    ##Create a list with all taxon key in the specified taxon name
    taxon_list <- selected_taxa %>%
      distinct(taxon_key) %>%
      pull(taxon_key)


    ##Computations
    watson_species_country_year <- watson_clean %>%
      filter(taxon_key %in% taxon_list) %>% ##fiters for all taxa in the specified group
      group_by(year, iso3_code, productive_sector) %>%
      summarise(landings_total = sum(reported, na.rm = T),
                iuu = sum(iuu_total, na.rm = T),
                discard_total = sum(discards, na.rm = T))

    total_species_country_year <- watson_species_country_year %>%
      filter(year == year_data,
             iso3_code == country,
             productive_sector == fishing_sector) %>%
      mutate(species_group = !!taxon_name)


    ##test
    # total_species_country_year <- watson_species_country_year %>%
    #   filter(year == 2010,
    #          iso3_code == "CHL",
    #          productive_sector == "industrial") %>%
    #   mutate(species_group = "penaeidae")



    return(total_species_country_year)

  }


}

##################################################################################

##Partition gear -- This functions calculates the fraction catch by gear in a specific year / by the total catch that year. The outcome includs the partial fraction for only reported catch and the full fractions adding reported, iuu and discard.

##Input variables are: scope_type = as for now it has to be a column of the watson data base.scope_name = the specific region, area you want to query. For example if your scope is iso3_code, then the type would be the three letter code of the country you want the data ("USA", "CHL"). Note these letters have to be in quotation. year_data = define a year for your query. fishing_sector = "industrial", "non-industrial" or NULL were NULL calculates the fraction for the total catch (industrial + non-industrial). input_data = watson clean data ast the outcoum of watson_all_names()



watson_partition_gear <- function(scope_type = NULL,
                              scope_name = NULL,
                              year_data = NULL,
                              fishing_sector=NULL,
                              input_data = NULL){

  ##Equoting varibales to be used below
    scope_name <- enquo(scope_name)
    scope_type <- enquo(scope_type)


    if(is.null(fishing_sector)){

      watson_data <- input_data %>%
        select(-productive_sector)

    }


    else{
    #Note:enquoting has to happen inside the if else. Selecting a fishing sector if defined
    fishing_sector <- enquo(fishing_sector)
      watson_data <- input_data %>%
        filter(productive_sector == !!fishing_sector)

    }

  ##How much was resported, iuu and discarted per gear per year
  totals_gear_per_year <- watson_data %>%
    group_by(!!scope_type, year, gear_name) %>%
    summarize(total_reported_gear = sum(reported, na.rm = T),
           total_iuu_gear = sum(iuu_total, na.rm = T),
           total_discards_gear = sum(discards, na.rm = T)) %>%
    ungroup()


  ##test
  # totals_gear_per_year <- watson_clean_ind %>%
  #   group_by(iso3_code, year, gear_name) %>%
  #   summarise(total_reported_gear = sum(reported, na.rm = T),
  #          total_iuu_gear = sum(iuu_total, na.rm = T),
  #          total_discards_gear = sum(discards, na.rm = T)) %>%
  #   ungroup()


  ##Total reported, iuu and discard in a year
  fraction_gear_year <- totals_gear_per_year %>%
    group_by(!!scope_type, year) %>%
    mutate(total_reported_year = sum(total_reported_gear, na.rm = T),
           total_iuu_year = sum(total_iuu_gear, na.rm = T),
           total_discards_year = sum(total_discards_gear, na.rm = T)) %>%
    ungroup() %>%
    mutate(gear_fraction_reported = total_reported_gear/total_reported_year) %>%
    mutate(gear_fraction_full = (total_reported_gear+total_iuu_gear+total_discards_gear)/(total_reported_year +total_iuu_year + total_discards_year)) %>%
    mutate_if(is.numeric, round, 5)

  ##Test
  # fraction_gear_year <- totals_gear_per_year %>%
  #   group_by(iso3_code , year) %>%
  #   mutate(total_reported_year = sum(total_reported_gear, na.rm = T),
  #          total_iuu_year = sum(total_iuu_gear, na.rm = T),
  #          total_discards_year = sum(total_discards_gear, na.rm = T)) %>%
  #   ungroup() %>%
  #   mutate(gear_fraction_reported = total_reported_gear/total_reported_year) %>%
  #   mutate(gear_fraction_full = (total_reported_gear+total_iuu_gear+total_discards_gear)/(total_reported_year +total_iuu_year + total_discards_year)) %>%
  # mutate_if(is.numeric, round, 5)

  ##Returns the fractions for each gear for the specified scope and year
  outcome <- fraction_gear_year %>%
    select(year, !!scope_type, gear_name, gear_fraction_reported, gear_fraction_full) %>%
    filter(!!scope_type == !!scope_name,
           year == !!year_data) %>%
    arrange(desc(gear_fraction_full))

  ##test
  # outcome <- fraction_gear_year %>%
  #   select(iso3_code, year, gear_name, gear_fraction_reported, gear_fraction_full) %>%
  #   filter(iso3_code == "CHL",
  #          year == 2015)


  return(outcome)

}



