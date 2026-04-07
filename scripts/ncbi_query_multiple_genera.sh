#!/bin/bash
genus_file=${1:?Usage: ncbi_query_multiple_genera.sh <genus_file>}
genus_counts=${2:+--num-samples $2}

while IFS= read -r genus; do
    [[ -z "$genus" || "$genus" == \#* ]] && continue
    python scripts/fetch_biosample.py --genus "$genus" $genus_counts --output "tests/${genus}.csv"
done < "$genus_file"