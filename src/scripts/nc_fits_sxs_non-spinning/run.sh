#!/bin/bash

for sxs_id in {0180,0007,0169,0030,0167,0295,0056,0296,0297,0298,0299,0063,0300,0301,0185,0303}; do
    sed "s/{sxs_id}/$sxs_id/g" nc_ringdown/src/scripts/nc_fits_sxs_non-spinning/config_SXS.ini > nc_ringdown/src/scripts/nc_fits_sxs_non-spinning/config_SXS_$sxs_id.ini
    bayRing --config-file nc_ringdown/src/scripts/nc_fits_sxs_non-spinning/config_SXS_$sxs_id.ini
done
