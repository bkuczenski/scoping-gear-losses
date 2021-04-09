# Fishing Vessel (MMSI) Info

**Description**: This table includes all MMSI that are included in the provisional daily fishing effort by MMSI data (fishing_effort_byvessel_v20190430). It includes all vessels that were identified as fishing vessels by the neural network and which were not identified as non-fishing vessels by registries and manual review. If an MMSI was matched to a fishing vessel on a registry, but the neural net did not classify it as a fishing vessel, it is not included on this list. There is only one row for each MMSI.

## Vessel classes

The following hierarchy is used to infer and assign vessel classes. The fishing and non-fishing categories contain nested vessel classes with increasing specificity that are assigned based on information available from registries or the neural net's confidence. For example, a vessel with a score of 0.3 for `tuna_purse_seines` and 0.3 for `other_purse_seines` would be classified as a `purse_seines`. In contrast, a vessel with a score of 0.6 for `tuna_purse_seines` would be classified as a `tuna_purse_seines`. If no fishing vessel class (or sub-class) inferred by the neural net receives a score (`inferred_vessel_class_score`) greater than 0.5, but the aggregate score of all fishing vessel classes exceeds 0.5, the vessel is classified as `fishing`.

It's also possible that the highest vessel class score inferred by the neural (`inferred_vessel_class_score`) net is for a non-fishing vessel class. In these instances, vessels are only included in this dataset if the aggregate score for fishing vessel classes (`inferred_vessel_class_ag_score`) exceeds 0.5.

```
 fishing:  
  squid_jigger:  
  drifting_longlines:  
  pole_and_line:  
  other_fishing:  
  trollers:  
  fixed_gear:  
    pots_and_traps:  
    set_longlines:  
    set_gillnets:  
  trawlers:  
  dredge_fishing:  
  seiners:  
   purse_seines:  
    tuna_purse_seines:  
    other_purse_seines:  
   other_seines:  
  driftnets:  

  non_fishing:  
    other_not_fishing:  
    passenger:  
    gear:  
    seismic_vessel:  
    helicopter:  
    cargo_or_tanker:  
      bunker_or_tanker:  
        bunker:  
        tanker:  
      cargo_or_reefer:  
        cargo:  
        reefer:  
    patrol_vessel:  
    research:  
    dive_vessel:  
    submarine:  
    dredge_non_fishing:  
    supply_vessel:  
    fish_factory:  
    tug:
  ```

## Table schema

- `mmsi`: Maritime Mobile Service Identity, the identifier for AIS  
- `flag`: an ISO3 value for the flag state of the vessel. If a value is not available from a manual review or from matching the vessels to registries, the MMSI mid code is used to identify the vessel flag state. A value of "UNK" means the flag state is unknown.  
- `vessel_class`: the best vessel class, combining the information available from registries and the results from the neural net. Vessel class used by Global Fishing Watch.  
- `registry_vessel_class`: the vessel class(es) as identified via vessel registries. Null values indicate the vessel was not matched to a registry or the registry did not indicate the vessel class.  
- `inferred_vessel_class`: the most likely vessel class as inferred by the neural net.  
- `inferred_vessel_class_score`: The neural net score for the inferred vessel class. Values approach 1 as confidence increases.  
- `inferred_vessel_class_ag`: final vessel class inferred by neural net. Matches inferred_vessel_class if `inferred_vessel_class_score` > 0.5. If no individual fishing vessel class received a neural net score > 0.5 but the cumulative neural net score for an aggregated fishing vessel class  (`inferred_vessel_class_ag_score`) exceeds 0.5, the aggregated vessel class is used.  
- `inferred_vessel_class_ag_score`: The cumulative neural net score for fishing vessel classes inferred by the neural net. Values approach 1 as confidence in the vessel being a fishing vessel increases.  
- `self_reported_fishing`: vessel consistently self-reports that it is a fishing vessel in AIS messages.  
- `length_m`: vessel overall length (meters). If a length is available from registries, the registry length is used. If not, the length inferred from the neural net is used.  
- `tonnage_gt`: vessel tonnage (gross tons). If a tonnage is available from registries, the registry tonnage is used. If not, the tonnage inferred from the neural net is used.  
- `engine_power_kw`: vessel engine power (kilowatts). If an engine power is available from registries, the registry engine power is used. If not, the engine power inferred from the neural net is used.  
- `active_2012`: the vessel was active enough to be inferred by the neural net in 2012  
- `active_2013`: the vessel was active enough to be inferred by the neural net in 2013    
- `active_2014`: the vessel was active enough to be inferred by the neural net in 2014      
- `active_2015`: the vessel was active enough to be inferred by the neural net in 2015     
- `active_2016`: the vessel was active enough to be inferred by the neural net in 2016      
- `active_2017`: the vessel was active enough to be inferred by the neural net in 2017      
- `active_2018`: the vessel was active enough to be inferred by the neural net in 2018    

## Tyler's additional notes

The vessel classes are nested and you are correct in that several classes result from ambiguous neural net results. For example, "tuna_purse_seines" are essentially large purse seine vessels (which mostly all target tuna) while "other_purse_seines" are generally smaller purse seine vessels (which mostly target other species). The "purse_seine" class is for vessels that our model/registry data was confident enough that a vessel was a purse seine but not confident specifically what class of purse seine. The "fixed_gear" class is similar (see the readme for the nested classes). 

The "other_fishing" class is a bit weird and includes all known fishing vessels not covered by the other fishing classes and is an output class of the neural net. If the net is confident enough that the vessel falls into this "other_fishing" category, it will be labeled as such, otherwise, it will be labeled as "fishing". We do not currently have generic descriptions of the vessel classes, but i'll work on one.

### BK's interpretation

Basically, `other_fishing` is non-modeled classes, `fishing` is any class (including non-modeled classes)

Right now, `other_fishing` is only used for trammel nets and tangle nets- this is almost surely not correct.  Rather, those are probably either set_gillnets (i.e. fixed_gear) or driftnets