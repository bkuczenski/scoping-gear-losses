# watson
Data from Watson (2017) [A database of global marine commercial, small-scale, illegal and unreported fisheries catch 1950–2014](https://www.nature.com/articles/sdata201739), subsequently expanded to 2015.

 - `watson_codes.xlsx` Locations of grid cells, gear names, taxa names, country names
 - `watson_codes_annotated.csv` Description of Watson's gear specifications

The data come partially aggregated in index form, which is sufficient to distinguish catch by year, country, species, and gear type.  Utility functions in `R/watson.R` enable some interpretive use of these files:

 - `watson_index_per_fishing_event_ind.csv` Industrial fishing activity, partially aggregated ([from utas.edu.au](https://data.imas.utas.edu.au/attachments/5c4590d3-a45a-4d37-bf8b-ecd145cb356d/IndexInd.csv))
 - `watson_index_per_fishing_event_Nind.csv` Non-industrial fishing activity, partially aggregated ([from utas.edu.au](https://data.imas.utas.edu.au/attachments/5c4590d3-a45a-4d37-bf8b-ecd145cb356d/IndexNInd.csv))

The fully-disaggregated, geographically-specific data reported in the full database are not used at all.  The current version of the database can be viewed at the [Institute for Marine & Antarctic Studies Webpage](https://metadata.imas.utas.edu.au/geonetwork/srv/eng/metadata.show?id=739) from the University of Tasmania.