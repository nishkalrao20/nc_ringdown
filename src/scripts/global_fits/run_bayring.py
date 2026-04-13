import os
import pandas as pd
import subprocess
import sys
import concurrent.futures
import time
from tqdm import tqdm  # Ensure you have installed this: pip install tqdm

csv_path = "nc_ringdown/src/data/RIT_Parameters_non-spinning.csv"
template = "nc_ringdown/src/scripts/global_fits/config_template.ini"
script_dir = "nc_ringdown/src/scripts/global_fits"
output_dir = "nc_ringdown/src/output/global_fits"

quantities = ['ecc', 'bmrg', 'emrg', 'jmrg', 'nu', 'nu_ecc', 'nu_bmrg', 'nu_emrg', 'nu_jmrg', 'nu_emrg_bmrg', 'nu_jmrg_bmrg', 'nu_emrg_jmrg']

MAX_WORKERS = 8 #os.cpu_count() 

def run_bayring_task(cmd):
    try:
        # Capture stderr to report errors without cluttering the progress bar
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return (True, None)
    except subprocess.CalledProcessError as e:
        return (False, f"Failed: {' '.join(cmd)} \nError: {e.stderr.decode()}")

df = pd.read_csv(csv_path)
# Ensure clean list of IDs
rit_ids = df[df['catalog'] == 'RIT']['ID'].astype(str).tolist()
rit_ids = sorted(list(set([x for x in rit_ids if x and x.lower() != 'nan'])))

print(f"Found {len(rit_ids)} RIT simulations to process.")

with open(template, 'r') as f:
    template_content = f.read()

tasks = []

print("Generating Configuration Files ---")

# Using tqdm for file generation step as well, though likely fast
for qty in tqdm(quantities, desc="Config Groups"):
    for dim in [1, 2, 3]:
        combo_dir = os.path.join(script_dir, f"{qty}_{dim}")
        os.makedirs(combo_dir, exist_ok=True)
        
        for rit_id in rit_ids:
            config_content = template_content.format(
                rit_id=rit_id,
                fitting_quantities=qty,
                fit_dim=dim
            )
            
            config_filename = f"config_RIT_{rit_id}.ini"
            config_path = os.path.join(combo_dir, config_filename)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            cmd = ["bayRing", "--config-file", config_path]
            
            # Check if output exists to skip task
            output_file = os.path.join(output_dir, f"{qty}_{dim}/RIT_{rit_id}/Algorithm/Evidence.txt")
            if os.path.exists(output_file):
                continue
            tasks.append(cmd)

print(f"Generated {len(tasks)} configuration files and tasks.")
print(f"\nExecuting {len(tasks)} runs in parallel (Workers: {MAX_WORKERS}) ---")

start_time = time.time()
failures = []

with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_cmd = {executor.submit(run_bayring_task, cmd): cmd for cmd in tasks}
    
    with tqdm(total=len(tasks), unit="task", desc="Running bayRing") as pbar:
        for future in concurrent.futures.as_completed(future_to_cmd):
            success, error_msg = future.result()
            
            if not success:
                failures.append(error_msg)
                pbar.set_postfix(failures=len(failures), refresh=False)
            
            pbar.update(1)

elapsed = time.time() - start_time
print(f"\nAll processing complete in {elapsed:.2f}s.")

if failures:
    print(f"\n!!! Encountered {len(failures)} errors !!!")
    print("Listing first 5 errors:")
    for err in failures[:5]:
        print("-" * 40)
        print(err)
else:
    print("Success: All tasks completed without errors.")