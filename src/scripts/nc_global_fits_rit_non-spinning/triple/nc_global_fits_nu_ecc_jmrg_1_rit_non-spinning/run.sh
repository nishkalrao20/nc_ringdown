#!/bin/bash

csv_file="nc_ringdown/src/data/RIT_Parameters_non-spinning.csv"

awk -F, 'NR>1 && $34=="RIT" {print $33}' "$csv_file" | while read rit_id; do
    sed "s/{rit_id}/$rit_id/g" nc_ringdown/src/scripts/nc_global_fits_nu_ecc_jmrg_1_rit_non-spinning/config_RIT.ini > nc_ringdown/src/scripts/nc_global_fits_nu_ecc_jmrg_1_rit_non-spinning/config_RIT_$rit_id.ini
    bayRing --config-file nc_ringdown/src/scripts/nc_global_fits_nu_ecc_jmrg_1_rit_non-spinning/config_RIT_$rit_id.ini
done
