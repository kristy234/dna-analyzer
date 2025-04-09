# Fetch all SNPs from the SNPedia API
# Writes to genotypes.txt
# Last run: Fetching genotype data: 210 pages [02:00,  1.75 pages/s]

import requests
import time
import json
from tqdm import tqdm
import os

LIMIT = 500
OUTPUT_PATH = 'genotypes.txt'
DELAY = 0.1 # seconds

session = requests.Session()

def fetch_genotypes(cmcontinue=None):
    base_url = "https://bots.snpedia.com/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:Is_a_genotype",
        "cmlimit": LIMIT
    }
    
    if cmcontinue:
        params["cmcontinue"] = cmcontinue
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Validate response structure
        if 'query' not in data:
            raise ValueError("No 'query' field in response")
            
        if 'categorymembers' not in data['query']:
            raise ValueError("No 'categorymembers' field in query")
            
        results = data['query']['categorymembers']
        if not results:
            raise ValueError("Empty results")
            
        # Get the continue token for pagination
        continue_token = None
        if 'continue' in data:
            continue_token = data['continue'].get('cmcontinue')
            
        return results, continue_token
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching data: {e}")

def save_rsids(results, output_file):
    for item in results:
        # Get the title (SNP ID)
        rsid = item.get('title', '')
        
        # Check if it starts with 'rs' (case insensitive)
        if rsid.lower().startswith('rs'):
            # Write just the rsid to the file
            output_file.write(f"{rsid}\n")

def main():
    cmcontinue = None

    mode = 'a' if os.path.exists(OUTPUT_PATH) else 'w'
    with open(OUTPUT_PATH, mode) as f:
        # Create a progress bar without a total (dynamic mode)
        pbar = tqdm(desc="Fetching genotype data", unit=" pages")
        
        try:
            while True:
                try:
                    # Fetch the next page of results
                    results, next_cmcontinue = fetch_genotypes(cmcontinue)
                    if not results:
                        print("No results returned, stopping.")
                        break

                    # Write any RSIDs to the output file. Ignore anything th
                    save_rsids(results, f)
                    f.flush()
                    
                    # Update progress bar
                    pbar.update(1)
                    
                    # If there's no continue token, we've reached the end
                    if not next_cmcontinue:
                        print("Reached end of data. Stopping.")
                        break
                    
                    # Update the continue token for the next request
                    cmcontinue = next_cmcontinue
                    
                    # Add a small delay to be nice to the API
                    time.sleep(DELAY)
                except (ValueError, RuntimeError) as e:
                    print(f"Error: {e}")
                    break
        finally:
            pbar.close()

if __name__ == "__main__":
    main() 