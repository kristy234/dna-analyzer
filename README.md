# DNA Analyzer

A web application for analyzing DNA data using SNPedia information. All processing happens in the browser - your DNA data never leaves your device.

> **Disclaimer**: This tool is for informational purposes only. Genetic data from SNPedia may be incomplete, outdated, or misinterpreted without context. Do not use it for medical or diagnostic decisions. Always consult a healthcare professional for advice.

## Architecture

- Frontend-only React application
- Uses pre-scraped SNPedia data stored in `genotypes_by_rsid.json`
- All DNA processing happens in the browser for privacy
- No backend server or data transmission

## Features

- Upload and analyze DNA files in your browser
    - Supports Ancestry.com format (tab-separated with columns: rsid, chromosome, position, allele1, allele2)
    - Will add support for 23andMe and other formats in the future
- View genetic markers with:
  - Magnitude (impact level)
  - Repute (good/bad/other)
  - Gene information
  - Links to SNPedia for more details
- Color-coded cards for easy identification of good/bad reputes
- Infinite scroll for smooth browsing of large datasets

## Development

### Setup

1. Install dependencies:
   ```bash
   cd dna-insights
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

### Building for Production

```bash
npm run build
```

The built files will be in `dna-insights/dist/` and can be deployed to GitHub Pages.

## Licensing

This project uses a dual-license approach:

- **Project Code**: Licensed under the MIT License
- **Genetic Data**: The data in `dna-insights/public/genotypes_by_rsid.json.gz` is derived from SNPedia and is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0) license.

For more details, see the [LICENSE](LICENSE) file.

### Data Update Workflow (Maintainers Only)

The SNPedia data in `genotypes_by_rsid.json` needs to be periodically updated. Here's how:

1. Set up Python environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   source venv/bin/activate
   
   # Install required packages
   pip install -r requirements.txt
   ```

2. Fetch all SNP IDs:
   ```bash
   python fetch_genotypes.py
   # Creates genotypes.txt with all rsids
   ```

3. Fetch detailed SNP information:
   ```bash
   python fetch_info.py
   # Creates genotypes.jsonl with detailed SNP properties
   ```

4. Parse and structure the data:
   ```bash
   python parse_jsonl.py
   # Creates genotypes_by_rsid.json with structure:
   {
     "rsid": {
       "allele1": {
         "allele2": {
           "gene": "...",
           "summary": "...",
           "magnitude": ...,
           "repute": "..."
         }
       }
     }
   }
   ```

5. Move the updated file:
   ```bash
   mv genotypes_by_rsid.json dna-insights/public/
   ```

6. Compress the JSON file for faster loading:
   ```bash
   gzip -c dna-insights/public/genotypes_by_rsid.json > dna-insights/public/genotypes_by_rsid.json.gz
   ```

   The compressed file will be used by the application for faster loading times.
   The original JSON file is kept for reference and can be removed if needed.

## Privacy

- All DNA processing happens in your browser
- No data is sent to any server
- SNPedia data is stored locally in the application
- Your DNA file is only used for client-side matching

## License

- **Application Code**: MIT License - See LICENSE file for details
- **Genetic Data**: The genetic data used in this application is derived from SNPedia and is available under the Creative Commons Attribution-Noncommercial-Share Alike 3.0 United States License (CC-BY-NC-SA 3.0). See [SNPEDIA_LICENSE.md](SNPEDIA_LICENSE.md) for details.

## Deployment

This project is deployed to GitHub Pages at [https://kristy234.github.io/dna-analyzer/](https://kristy234.github.io/dna-analyzer/).

### Automatic Deployment

The project uses GitHub Actions to automatically deploy to GitHub Pages whenever changes are pushed to the `main` branch. The workflow:

1. Builds the project using Vite
2. Deploys the built files to GitHub Pages

### Manual Deployment

If you need to deploy manually:

1. Build the project:
   ```bash
   cd dna-insights
   npm run build
   ```

2. Push the changes to GitHub:
   ```bash
   git add .
   git commit -m "Update build"
   git push
   ```

The GitHub Actions workflow will automatically deploy the changes to GitHub Pages. 