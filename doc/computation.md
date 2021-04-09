# Computation Design

The analytic portion of the project encompasses all the information that can be extracted from the three core databases, collectively called the "reference data":
 * FAO Landings
 * Watson DB
 * Landings/Discards DB

Different parts of these databases provide different types of info for the project.  The key parameters we want to estimate from the reference data include:

 * Total capture F = C + U + D, Catch + unreported catch + discards, for a given scope
 * Partitioning total capture for a given scope between industrial and nonindustrial
 * Partitioning total capture for a given scope across gear types 

## Functional Operations

We have two groups of computations: scalar values and exchange (rational/fractional) values.  Scalar values have physical units and exchange values are ratios 
between two scalar values. 
Exchange values allow some scalar values to be estimated from other scalar values.

### Scalar Values

There are a total of **nine** scalar values in the reference data:

 * Reported Catch (FAO, Watson [industrial; non-industrial], landdisc)
 * Unreported Catch (Watson [industrial; non-industrial])
 * Discards (Watson [industrial; non-industrial], landdisc)

### Exchange Values

Relating to discards:

 * Discard Rate, Reported; D / (D+C) (Watson, landdisc)
 * Unreported Rate; U / (U+C) (Watson)
 * Discard Rate, Full; D / (U+C+D) (Watson)

Relating to gears:

 * Gear fraction, reported (C gear, scope / C total, scope)
 * Gear fraction, Full (C gear, scope + U gear, scope + D gear, scope) / (C scope + U scope + D scope)
 * Discard rate, gear, scope D gear, scope / (C gear, scope + D gear, scope)

## Definition of Scope

All three of the above parameters depend on an independent variable called "scope," which represents a definite portion of global catch.  Scope has three components:

 1. Data Year (1950-2018)
 2. Country (or none)
 3. Taxa specification (or none)
 
The scope specification is the user's method of defining what information they expect to receive.  We will use our harmonized **master tables** to define scope.  

 1. Data year is as-entered
 2. Country must be any entry from `master_country.csv` in one of the following columns: (`un_code`, `iso_2_code`, `iso3_code`)
 3. Taxa must be any entry from either `master_species` file in one of the following [shared] columns: (`name_en`, `3Alpha_code`, `Genus`, `Family`, `ISSCAAP_Group`). 
 Maybe others.
 
## Computing Scalar Values

The "Catch by x" function (issue #5) computes scalar values based on scope.  There should be a distinct "catch by x" function for each data source, and maybe a 
master function that simply concatenates them.  The operation of each function is to simply select and aggregate records.  All records should be selected for a given 
data source that match the specified scope, and the data values should be added together. In each case, the input scope specification should be given the *most 
expansive possible* interpretation.  If the taxa input is penaeidae, that should match watson "penaeus", "shrimps, prawns", "penaeidae", "artemisia longinaris", 
and several other Watson entries for the "penaeidae" family.

"Catch by x" encompasses all nine scalar values listed above.  

## Interpreting scope for the `landdisc` dataset

The `landdisc` dataset has the fewest entries.  There is only data for one year, 2018, and although nearly all countries are represented, the taxonomic specificity is limited 
to seven classes reported in the report in Annex A.  A taxa spec will have to be converted to one of these seven classes.

That file's independent values are: country, fishery name, gear, ocean, target.  The fishery name is interpretive and cannot be used for data selection.  However, the (country, gear, ocean, target) tuple is non-unique.

This file maps the independent variables to two data columns: reported catch and "Discards MLE" where MLE stands for ... something.

What the `landdisc` database can do for us is map country + gear type + target to discard rate, and so it thereby functions as an alternative metric for estimating discard 
rate.
