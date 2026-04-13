import os
import pandas as pd
import subprocess
import sys
import concurrent.futures
import time
import shutil
from tqdm import tqdm 

csv_path = "nc_ringdown/src/data/RIT_Parameters_non-spinning.csv"
template = "nc_ringdown/src/scripts/bayesian_global_fits/config_template.ini"
script_dir = "nc_ringdown/src/scripts/bayesian_global_fits"
output_dir = "nc_ringdown/src/output/bayesian_global_fits"

quantities = ['ecc', 'bmrg', 'emrg', 'jmrg', 'nu', 'nu_ecc', 'nu_bmrg', 'nu_emrg', 'nu_jmrg', 'nu_emrg_bmrg', 'nu_jmrg_bmrg', 'nu_emrg_jmrg']

MAX_WORKERS = 6#os.cpu_count() 

def run_bayring_task(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return (True, None)
    except subprocess.CalledProcessError as e:
        return (False, f"Failed: {' '.join(cmd)} \nError: {e.stderr.decode()}")

df = pd.read_csv(csv_path)
rit_ids = df[df['catalog'] == 'RIT']['ID'].astype(str).tolist()
rit_ids = sorted(list(set([x for x in rit_ids if x and x.lower() != 'nan'])))

print(f"Found {len(rit_ids)} RIT simulations to process.")

with open(template, 'r') as f:
    template_content = f.read()

tasks = []

print("Generating Configuration Files ---")

for qty in quantities:
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
            
            run_output_dir = os.path.join(output_dir, f"{qty}_{dim}/RIT_{rit_id}")

            output_file = os.path.join(run_output_dir, "Algorithm/Evidence.txt")
            if os.path.exists(output_file):
                continue
            
            tasks.append((cmd, run_output_dir))

print(f"Generated {len(tasks)} configuration files and tasks.")
print(f"\nExecuting {len(tasks)} runs in parallel (Workers: {MAX_WORKERS}) ---")

start_time = time.time()
failures = []

try:
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_info = {executor.submit(run_bayring_task, t[0]): t for t in tasks}
        
        try:
            with tqdm(total=len(tasks), unit="task", desc="Running bayRing") as pbar:
                for future in concurrent.futures.as_completed(future_to_info):
                    cmd, _ = future_to_info[future]
                    success, error_msg = future.result()
                    
                    if not success:
                        failures.append(error_msg)
                        pbar.set_postfix(failures=len(failures), refresh=False)
                    
                    pbar.update(1)
        
        except KeyboardInterrupt:
            print("\n\n!!! Interrupted by User (Ctrl+C) !!!")
            print("Stopping runs and deleting incomplete output directories...")
            
            executor.shutdown(wait=False, cancel_futures=True)
            
            deleted_count = 0
            for future, (cmd, run_dir) in future_to_info.items():
                if not future.done():
                    if os.path.exists(run_dir):
                        try:
                            shutil.rmtree(run_dir)
                            deleted_count += 1
                        except OSError as e:
                            print(f"Error deleting {run_dir}: {e}")
            
            print(f"Cleanup complete. Deleted {deleted_count} incomplete directories.")
            sys.exit(1)

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if 'failures' in locals() and not failures:
         failures.append(str(e))

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
