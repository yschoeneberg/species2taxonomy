# Species2taxonomy
Takes a list of species and returns the higher NCBI-Taxonomy.

## Dependencies
- Python 3
  - ete3 Toolkit (tested with v3.1.2)
  - Pandas (tested with v1.5.3)
 
To set up a conda environment:
```
conda create -c conda-forge -n blast2tax pandas ete3=3.1.2
```
## Input
A text file with one species name per line (with white spaces). 
## Output
A tsv file containig the species and the higher taxonomy information extracted from NCBI.
## Command Line Options
```
            Usage: species2taxonomy_v0.1.0.py [options]\
                  Version: 0.1.0
                  
                  REQUIRED:
                    -i    File containing the species list with one species per line.
                    -o    Output file
                  
                  OPTIONAL:
                    -r     Comma seperated list of taxonomic ranks to extract. Must be ranks of the NCBI-Taxonomy.
                    -s    Skip Taxonomy Database Update
                    -f    Skip failed taxIDs and write those to 'failed_taxids.tsv'
                    -h    Display this help message
```
