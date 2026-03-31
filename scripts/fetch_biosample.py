import requests
import argparse
import xml.etree.ElementTree as ET
import csv
import os

# return list of sample IDs used later to fetch metadata
def search_genus(genus):
    response = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=biosample&term={genus}&retmode=json")
    return response.json()

# counts how many hits there are, and lists first 5 IDs to see if it worked properly
def extract_search_results(search_response):
    count = search_response['esearchresult']['count']
    ids = search_response['esearchresult']['idlist']
    return count, ids

# fetches xml if not present in data/
def fetch_sample_metadata(sample_id, cache_dir="data/"):
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{sample_id}.xml")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            xml_content = f.read()
        print(f"Loaded {sample_id} from cache!")
    else:
        response = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id={sample_id}&retmode=xml")
        xml_content = response.text

        with open(cache_file, 'w') as f:
            f.write(xml_content)
        print(f"Downloaded and cached {sample_id}")
    return xml_content

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
    parser.add_argument('-n', '--num-samples', type=int, default=10, help='Number of samples to process (default: 10)')
    parser.suggest_on_error = True
    return parser.parse_args()


 # Main       
args = parse_arguments()
resp_json = search_genus(args.genus)
count, ids = extract_search_results(resp_json)
print(f"Found {count} samples")
print(f"Processing first {args.num_samples} IDs: {ids[:args.num_samples]}")

# Collect all sample data
all_samples = []
for sample_id in ids[:args.num_samples]:
    xml_content = fetch_sample_metadata(sample_id)
    data = parse_sample_xml(xml_content)
    data['sample_id'] = sample_id
    all_samples.append(data)

print(f"Collected {len(all_samples)} samples")
write_to_csv(all_samples, args.output)