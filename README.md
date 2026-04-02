# ncbi_query
API to query NCBI BioProjects on a genus level. 

The NCBI search function is often very frustrating to users, and they would like a neater way to query BioProjects that aggregates results in a tidy way. This tool searches the BioProjects database with a genus level query, retrieves all BioProjects, extracts some fields of interests, and plots the output in a few graphs and a summary table. Users can then narrow down their later get requests through SRA accessions without needing to access the NCBI interface.

## Use
### Installation
Everything is wrapped in a [Pixi](https://pixi.prefix.dev/latest/) environment. If you aren't running Pixi yet, follow the installation instructions in the tutorial and clone this repository
```
git clone https://github.com/lpotgieter/ncbi_query.git
```
and install the environment from the repository directory
```
pixi install
```

### Running the scripts
The codebase has several different components that can be run one by one from the CLI, or through Pixi tasks

#### One by One in the CLI
To query the NCBI BioProject database, run the `fetch_biosample.py` script. 

- [ ] `--genus` is a required flag to specify the genus you wish to search for. Here, we use Tilletia as a placeholder. 
- [ ] `--num-samples` sets the number of results to fetch. If nothing is specified, all results will be fetched.
- [ ] `--output` is the where the collected information from the XML's saved in `data/` will be written
  
```
pixi run python scripts/fetch_biosample.py --genus Tilletia --num-samples 15 --output tests/tilletia.csv
```

To summarise the output from the above table, run the `summary_bioprojects.py` script

- [ ] `--csv-file` is the output from `fetch_biosamples.py`
- [ ] `--prefix` to set the prefix of the generated output. Standard is `out`
```
pixi run python scripts/summary_bioprojects.py --csv-file tests/tilletia.csv --prefix tests/tilletia
```

#### As Pixi tasks

## Future Additions
A project like this is never truly done! There are 

1) A dashboard to have evrything in an interactive place
2) A filtering tool to only select species of interest in summary statistics
3) Incorporating [NCBI Datasets](https://www.ncbi.nlm.nih.gov/datasets/) into the tasks to pull from a list. The package has been included in the environment, so users could collect SRA data, and run the tool to pull genomes. To run `datasets` with this environment, for example
  ```
  pixi run datasets download genome accession --version
  ```
  Pulling in a bash loop to iterate through accessions in a list and parsing each line into the accession flag through variables would not be difficult if a user would like to automate this!
4) It might also be useful to be able to run this natively on more than one species, so inputting a list and running over the list of species one at a time, and outputting summaries for each species.