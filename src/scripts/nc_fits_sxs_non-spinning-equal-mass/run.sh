#!/bin/bash
config_template="nc_ringdown/src/scripts/nc_fits_sxs_non-spinning-equal-mass/config_SXS.ini"
output_dir="nc_ringdown/src/scripts/nc_fits_sxs_non-spinning-equal-mass/"
csv_file="nc_ringdown/src/data/SXS_Parameters_non-spinning-equal-mass.csv"

awk -F, 'NR>1 && $34=="SXS" {print $33}' "$csv_file" | while read sxs_id; do
    echo "Starting runs for SXS $sxs_id"
    for seed in 1 2 3; do
        config_file="${output_dir}config_SXS_${sxs_id}_${seed}.ini"
        sed -e "s/{sxs_id}/$sxs_id/g" -e "s/{seed}/$seed/g" "$config_template" > "$config_file"
        
        echo "Running SXS $sxs_id with seed $seed"
        bayRing --config-file "$config_file" &
    done
    wait
    echo "Finished runs for SXS $sxs_id"
done
