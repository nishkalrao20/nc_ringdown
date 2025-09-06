#!/bin/bash
config_template="nc_ringdown/src/scripts/nc_fits_rit_non-spinning-equal-mass/config_RIT.ini"
output_dir="nc_ringdown/src/scripts/nc_fits_rit_non-spinning-equal-mass/"
csv_file="nc_ringdown/src/data/RIT_Parameters_non-spinning-equal-mass.csv"

awk -F, 'NR>1 && $34=="RIT" {print $33}' "$csv_file" | while read rit_id; do
    echo "Starting runs for RIT $rit_id"
    for seed in 1 2 3; do
        config_file="${output_dir}config_RIT_${rit_id}_${seed}.ini"
        sed -e "s/{rit_id}/$rit_id/g" -e "s/{seed}/$seed/g" "$config_template" > "$config_file"
        
        echo "Running RIT $rit_id with seed $seed"
        bayRing --config-file "$config_file" &
    done
    wait
    echo "Finished runs for RIT $rit_id"
done