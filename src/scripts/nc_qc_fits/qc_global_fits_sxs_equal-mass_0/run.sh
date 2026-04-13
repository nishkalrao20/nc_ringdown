#!/bin/bash

for sxs_id in {1477,0225,0219,0305,0224,0148,2086,0156,0172,3628,3627}; do
    sed "s/{sxs_id}/$sxs_id/g" nc_ringdown/src/scripts/nc_qc_fits/qc_global_fits_sxs_equal-mass_0/config_SXS.ini > nc_ringdown/src/scripts/nc_qc_fits/qc_global_fits_sxs_equal-mass_0/config_SXS_$sxs_id.ini
    bayRing --config-file nc_ringdown/src/scripts/nc_qc_fits/qc_global_fits_sxs_equal-mass_0/config_SXS_$sxs_id.ini
done
