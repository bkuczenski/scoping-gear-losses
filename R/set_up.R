
##Main Functions of the project


## Set-up

options(scipen=999) ##Sets R not to use scientific notations

### Load libraries

load_pak <- function(pkg){
  new_pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
  if(length(new_pkg))
    install.packages(new_pkg, dependencies = TRUE)
  sapply(pkg, require, character.only = TRUE) ##require is equivalent to library but it does not print the warning messages. If a package was not loaded it prints FALSE. Good when loading packages through a function
}

##list of packages to be used in this script
common_packages <- c(
  "tidyverse", ## data manipulation includes ggplot, readr, stringr, tidyr
  "janitor", ##cleans data
  "here", ##sets working directory to the Rproject location
  "readxl" ##read data frame from excel
)
##install and load packeges
load_pak(common_packages)

additional_pkgs <- c(
  "pdftools", ## extraxt text from pdf
  "rvest", ## allows crapping data form the web
  "tidyr", ## tools to create tidy data
  "quantreg", ## computes quantile regressions
  "broom", ## Convert statistical analysis objects from R into tidy tibbles
  "qwraps2"
)

plotting_pkgs <- c(
  "RColorBrewer", ## color pallet
  "ggtext", ## ##Add variable colors into text in the title of the plot
  "patchwork", ## allows you to combine defferent plots into one figure
  "plotly"  ##created interactive plots

)
