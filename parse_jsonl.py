import requests
import time
import json
import os
from tqdm import tqdm
from collections import defaultdict

def main():    
    # Create a nested defaultdict for automatic dictionary creation
    genotypes_by_rsid = defaultdict(lambda: defaultdict(dict))
    genotypes_by_gene = defaultdict(lambda: defaultdict(dict))
    
    # Read the JSONL file
    with open("genotypes.jsonl", "r") as f:
        for line in f:
            if not line.strip():
                continue
            
            try:
                # Parse each line as JSON
                snp_data = json.loads(line)
                # Extract the rsid and alleles
                rsid = snp_data.get('title', '').lower().split('(')[0].strip()
                # Sort the alleles so that we don't have to worry about the order on lookup
                alleles = sorted([snp_data.get('allele1', '').upper(), snp_data.get('allele2', '').upper()])
                allele1, allele2 = alleles


                gene = snp_data.get('gene') or ''
                summary = snp_data.get('summary') or ''
                magnitude = snp_data.get('magnitude') or 0
                repute = snp_data.get('repute') or ''
                    
                # Add the allele2 information - no need to check if dictionaries exist
                genotypes_by_rsid[rsid][allele1][allele2] = {
                    'gene': gene,
                    'summary': summary,
                    'magnitude': magnitude,
                    'repute': repute
                }

                if gene:
                    genotypes_by_gene[gene][allele1][allele2] = {
                        'rsid': rsid,
                        'summary': summary,
                        'magnitude': magnitude,
                        'repute': repute
                    }
            except Exception as e:
                print(f"Error parsing line. Skipping.")
                print(f"  Line: {line}")
                print(f"  Error: {e}")

    
    # Write the results to a JSON file
    with open('genotypes_by_rsid.json', 'w') as f:
        json.dump(genotypes_by_rsid, f, indent=2)

    with open('genotypes_by_gene.json', 'w') as f:
        json.dump(genotypes_by_gene, f, indent=2)
        
    print(f"Processed {len(genotypes_by_rsid)} rsids and {len(genotypes_by_gene)} genes into structured JSON format")

if __name__ == "__main__":
    main()
