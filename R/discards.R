
## Discard family of functions
####This scripts contains all the functions needed to query the discards data base. These group of functions are unde the `discards_` family.

##Get Discard raw data and cleans t as needed for this project
discard_data_ <- NULL

get_discard_data <- function(){

  if(is.null(discard_data_)) {
    discard_data_ <- read_csv(here::here("data/perez-roda_discards/fao_elg_landdisc.csv"))
  }

discard_clean <- discard_data_ %>%
  clean_names() %>%
  select(country,fishery_id, fishery_name, gear, ocean, species_group=target, landings, discards= discards_mle, total_catch = total_catch_mle) %>%
  mutate(total_catch = round(total_catch, 3)) %>%
  mutate(discards = round(discards, 3)) %>%
  mutate(country = case_when(country ==  "Curacao" ~ "Curaçao",
                             country == "Cote d'Ivoire" ~ "Côte d'Ivoire",
                             country == "Fiji, Republic of" ~ "Fiji",
                             country == "Palestine, Occupied Tr." ~ "Palestine",
                             T ~ country)) ##Fixes discrepancies in country names with fao_landings country names
return(discard_clean)

}


##discards_all_names() -- This functions reads in the discards clean data and joins it to the country master table and species master table.
##It does not need any input and it's outcome is the discards clean data joined to the maaster country and the discards master species


discards_all_names <- function(discard_data) {

  master_countries <- read_csv(here::here("mapping_tables/master_countries.csv"))

  discards_clean <- discard_data %>%
    rename(fao_landing_c_name = country) %>%
    left_join(master_countries, by = "fao_landing_c_name")

  return(discards_clean)
}

##test
# discards_clean <- get_discard_data() %>%
#   discards_all_names()



#
##catch_by_x function for the discard database


## discard_catch_by_x: Queries the discard data by year, country and/or species group.
## year_data = only 2018
## country = country name using ISO 3 letters in quotations
## species = group of species as classified in the discard data
## input_data = clean discard data; outout of `discads_all_names()`

##NOTES: As for now you always have to define a year




# discards_catch_by_x <- function(year_data =NULL,
#                                 country = NULL,
#                                 species = NULL,
#                                 input_data = NULL){
#
#   discards_clean <- input_data
#
#
#   if(is.null(species)) {
#     print("Grouped by country and year")
#
#     discards_by_country_year <- discards_clean %>%
#       group_by(iso3_code, year) %>%
#       summarise(total_landings = sum(landings, na.rm = T),
#                 total_discards = sum(discards, na.rm = T))
#
#     total_country_year <- discards_by_country_year %>%
#       filter(iso3_code == country,
#              year == year_data)
#
#     return(total_country_year)
#   }
#
#
#   else if (is.null(country)) {
#
#     print("Grouped by species group and year")
#
#     discards_by_species_year <- discards_clean %>%
#       group_by(year, species_group) %>%
#       summarise(total_landings = sum(landings, na.rm = T),
#                 total_discards = sum(discards, na.rm = T))
#
#     total_year_species <- discards_by_species_year %>%
#       filter(year == year_data,
#              species == species_group)
#
#     return(total_year_species)
#
#   }
#
#   else {
#     print("Grouped by species group, country and year")
#
#     discard_by_species_country_year <- discards_clean %>%
#       group_by(year, species_group, iso3_code) %>%
#       summarise(total_landings = sum(landings, na.rm = T),
#                 total_discards = sum(discards, na.rm = T))
#
#     total_species_country_year <- discard_by_species_country_year %>%
#       filter(year == year_data,
#              species_group == species,
#              iso3_code == country)
#
#     return(total_species_country_year)
#
#   }
#
# }
#
#
