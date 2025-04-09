import requests
import time
import json
import os
from tqdm import tqdm
from collections import defaultdict

INPUT_FILE = "genotypes.txt"
OUTPUT_FILE = "genotypes.jsonl"
DELAY = 0.05

session = requests.Session()

def first_or_none(value_list):
    return value_list[0] if value_list else None

def load_processed_titles():
    if not os.path.exists(OUTPUT_FILE):
        return set()
    with open(OUTPUT_FILE, "r") as f:
        return {json.loads(line)["title"] for line in f if line.strip()}
    

def fetch_info(title):
    query = f"[[{title}]]|?Rsnum|?Genotype|?Allele1|?Allele2|?Magnitude|?Repute|?Summary|?In gene"

    params = {
        "action": "ask",
        "format": "json",
        "query": query
    }
    try:
        r = session.get("https://bots.snpedia.com/api.php", params=params)
        r.raise_for_status()
        data = r.json()
        result = data.get("query", {}).get("results", {}).get(title, {})
        out = result.get("printouts", {})

        # Gene print out in the format:
        #   "In gene": [
        #     {
        #       "fulltext": "MTHFR",
        #       "fullurl": "https://bots.SNPedia.com/index.php/MTHFR",
        #       "namespace": 0,
        #       "exists": "1",
        #       "displaytitle": ""
        #     }
        gene_obj = first_or_none(out.get("In gene"))
        gene = gene_obj.get("fulltext") if isinstance(gene_obj, dict) else None

        return {
            "title": title,
            "rsid": first_or_none(out.get("Rsnum")),
            "genotype": first_or_none(out.get("Genotype")),
            "allele1": first_or_none(out.get("Allele1")),
            "allele2": first_or_none(out.get("Allele2")),
            "magnitude": first_or_none(out.get("Magnitude")),
            "repute": first_or_none(out.get("Repute")),
            "summary": first_or_none(out.get("Summary")),
            "gene": gene
        }
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return None

def main():
    with open(INPUT_FILE, "r") as infile:
        all_titles = [line.strip() for line in infile if line.strip()]

    processed = load_processed_titles()

    # Enhanced tqdm progress bar with better time estimates
    with open(OUTPUT_FILE, "a") as outfile, tqdm(
        total=len(all_titles), 
        desc="Fetching Genotypes", 
        unit="Genotype",
        unit_scale=True,
        mininterval=1.0,  # Update at most once per second
        smoothing=0.3     # Smoothing factor for the estimated time
    ) as pbar:
        for title in all_titles:
            if title in processed:
                pbar.update(1)
                continue

            result = fetch_info(title)
            if result:
                json.dump(result, outfile)
                outfile.write("\n")
                outfile.flush()

            time.sleep(DELAY)
            pbar.update(1)

    # Process OUTPUT_FILE into a JSON file
    print("Converting JSONL to structured JSON...")
    
    # Create a nested defaultdict for automatic dictionary creation
    genotypes = defaultdict(lambda: defaultdict(dict))
    
    # Read the JSONL file
    with open(OUTPUT_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
                
            # Parse each line as JSON
            snp_data = json.loads(line)
            
            # Extract the rsid and alleles
            rsid = snp_data.get('rsid', '').lower()
            allele1 = snp_data.get('allele1', '').upper()
            allele2 = snp_data.get('allele2', '').upper()
                
            # Add the allele2 information - no need to check if dictionaries exist
            genotypes[rsid][allele1][allele2] = {
                'gene': snp_data.get('gene'),
                'summary': snp_data.get('summary'),
                'magnitude': snp_data.get('magnitude'),
                'repute': snp_data.get('repute')
            }
    
    # Write the results to a JSON file
    with open('genotypes.json', 'w') as f:
        json.dump(genotypes, f, indent=2)
        
    print(f"Processed {len(genotypes)} genotypes into structured JSON format")

if __name__ == "__main__":
    main()
