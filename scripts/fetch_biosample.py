import requests
import requests.exceptions
import argparse
import xml.etree.ElementTree as ET
import csv
import os

# return list of sample IDs used later to fetch metadata
def search_genus(genus, max_results=10000):
    try:
        response = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=biosample&term={genus}&retmode=json&retmax={max_results}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching for genus '{genus}': {e}")
        return None

# counts how many hits there are, and lists first 5 IDs to see if it worked properly
def extract_search_results(search_response):
    count = int(search_response['esearchresult']['count'])
    ids = search_response['esearchresult']['idlist']
    return count, ids

# fetches xml if not present in data/
def fetch_sample_metadata(sample_id, cache_dir="data/"):
    import os
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{sample_id}.xml")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            xml_content = f.read()
        print(f"Loaded {sample_id} from cache")
        return xml_content
    else:
        try:
            response = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id={sample_id}&retmode=xml")
            response.raise_for_status()
            xml_content = response.text
            
            with open(cache_file, 'w') as f:
                f.write(xml_content)
            print(f"Downloaded and cached {sample_id}")
            return xml_content
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {sample_id}: {e}")
            return None 

# parse xml and extract info 
def parse_sample_xml(xml_content):
    root = ET.fromstring(xml_content)
    biosample = root.find('BioSample')

    data = {}
    
    organism = biosample.find('Description/Organism/OrganismName')
    data['species'] = organism.text if organism is not None else None
    
    attributes = biosample.findall('Attributes/Attribute')
    for attr in attributes:
        if attr.get('attribute_name') == 'collection_date':
            data["collection_date"] = attr.text
        if attr.get('attribute_name') == 'geo_loc_name':
            data["geo_loc_name"] = attr.text
        if attr.get('attribute_name') == 'platform':
            data["platform"] = attr.text

    owner = biosample.find('Owner/Name')
    data['owner_name'] = owner.text if owner is not None else None
    return data

# export to csv in cwd called tilleria_samples.csv
def write_to_csv(samples, filename="tilletia_samples.csv"):
    if not samples:
        return
    
    fieldnames = samples[0].keys()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(samples)

# CLI arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch NCBI BioSample data for a genus')
    parser.add_argument('-g', '--genus', required=True, help='Genus name to search for (e.g., Tilletia)')
    parser.add_argument('-o', '--output', default='samples.csv', help='Output CSV filename (default: samples.csv)')
    parser.add_argument('-n', '--num-samples', type=int, default=None, help='Number of samples to process (default: all)')    
    parser.suggest_on_error = True
    return parser.parse_args()


# Main       
args = parse_arguments()
resp_json = search_genus(args.genus)

count, ids = extract_search_results(resp_json)

if resp_json is None:
    print(f"Error: Could not search for genus '{args.genus}'. Please check your internet connection.")
    exit(1)

if count == 0:
    print(f"Error: No samples found for genus '{args.genus}'. Please check the genus name.")
    exit(1)


print(f"Found {count} samples")
print(f"Retrieved {len(ids)} sample IDs")

# If no limit specified, use all samples
if args.num_samples is None:
    samples_to_process = ids
    print(f"Processing all {len(ids)} samples")
else:
    samples_to_process = ids[:args.num_samples]
    print(f"Processing first {args.num_samples} samples")


# Collect all sample data
all_samples = []
failed_ids = []

for i, sample_id in enumerate(samples_to_process, 1):
    print(f"Processing sample {i}/{len(samples_to_process)}: {sample_id}")
    xml_content = fetch_sample_metadata(sample_id)
    
    if xml_content is None:
        failed_ids.append(sample_id)
        continue  # skip to next sample
    
    data = parse_sample_xml(xml_content)
    data['sample_id'] = sample_id
    all_samples.append(data)

if failed_ids:
    print(f"Warning: Failed to download {len(failed_ids)} samples")
    with open("failed_downloads.log", "w") as f:
        for failed_id in failed_ids:
            f.write(f"{failed_id}\n")
    print("Failed sample IDs written to failed_downloads.log")


print(f"Collected {len(all_samples)} samples")
write_to_csv(all_samples, args.output)
print(f"Data written to {args.output}")