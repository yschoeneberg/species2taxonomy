#!/usr/bin/env python3
# species2taxonomy.py
# Author: Yannis Schöneberg <yannis.schoeneberg@gmx.de>
# This script takes in a list of species names and outputs the taxonomy data in a tsv file
# Version 0.1.0
import getopt
import sys
import os
import logging
import pandas as pd
from ete3 import NCBITaxa
from itertools import chain


def get_options(argv):
    global version
    global skip_update
    global skip_failed
    global ranks
    global fail_file
    version = "0.1.0"
    skip_update = False
    skip_failed = False
    ranks = ['kingdom', 'phylum', 'superclass', 'class', 'subclass', 'order', 'infraorder', 'superfamily', 'family', 'genus', 'species']
    fail_file = "failed_taxids.tsv"
    
    try:
        opts, args = getopt.getopt(argv, "hi:o:r:sf", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print(f"Usage: blast2taxonomy_v{str(version)}.py -i <infile> -o <outfile> -c <column taxids> -t <num threads>\n"
              f"Type blast2taxonomy_v{str(version)}.py -h for help")
    print (f"opts: {opts}")
    for opt, arg in opts:
        if opt == '-h':
            print(f"\nUsage: blast2taxonomy_v{str(version)}.py [options]\n"
                  f"Version: {str(version)}\n"
                  f"\n"
                  f"REQUIRED:\n"
                  f"\t-i\tFile containing the species list with one species per line.\n"
                  f"\t-o\tOutput file\n"
                  f"\n"
                  f"OPTIONAL:\n"
                  f"\t-r\tComma seperated list of taxonomic ranks to extract. Must be ranks of the NCBI-Taxonomy.\n"
                  f"\t-s\tSkip Taxonomy Database Update\n"
                  f"\t-f\tSkip failed taxIDs and write those to 'failed_taxids.tsv'\n"
                  f"\t-h\tDisplay this help message\n"
                  f"\n")
            sys.exit()
        elif opt == '-i':
            global species_infile
            species_infile = arg
        elif opt == '-o':
            global outfile
            outfile = arg
        elif opt == "-f":
            skip_failed = True
        elif opt == "-s":
            skip_update = True
            try:
                os.remove(fail_file)
            except FileNotFoundError:
                pass
            except Exception as e:
                raise e
        elif opt == "-r":
            ranks = arg.split(",")


def update_taxdb():
    logger.info(f"### Updating Taxonomy Database")
    ncbi.update_taxonomy_database()
    logger.info(f"Finished Updating Database")
    logger.info(f"Removing temporary files")
    os.remove("taxdump.tar.gz")


def get_taxonomy (species, ranks):
    taxids = ncbi.get_name_translator(species)
    taxids = list(taxids.values())
    taxids = list(chain(*taxids))

    taxonomic_info = []
    for id in taxids:
        lineage = ncbi.get_lineage(id)
        names = ncbi.get_taxid_translator(lineage)
        extracted_ranks = ncbi.get_rank(lineage)
        extracted_ranks = dict((val, key) for key, val in extracted_ranks.items())
        desired_taxids = [extracted_ranks.get(rank, 'Nan') for rank in ranks]
        tax_inf = [names.get(tid, 'Nan') for tid in desired_taxids]
        taxonomic_info.append(tax_inf)
    return taxonomic_info


if __name__ == '__main__':
    logger = logging.getLogger('my_logger')
    my_handler = logging.StreamHandler()
    my_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %("
                                     "message)s")
    my_handler.setFormatter(my_formatter)
    logger.addHandler(my_handler)
    logger.setLevel(logging.INFO)

    print(sys.argv)
    get_options(sys.argv[1:])

    logger.info(f"#### Extracting Taxonomy Information for given Species\n"
                f"{'Program Version:':<50} {str(version)}\n"
                f"{'Species List:':<50} {species_infile}\n"
                f"{'Output file:':<50} {outfile}\n"
                f"{'Skip Taxonomy DB update:':<50} {skip_update}\n"
                f"{'Skip failed Species:':<50} {skip_failed}\n")
    species = pd.read_csv(species_infile, sep="\t", dtype=str, header=None)
    species = species[0].values.tolist()
    global ncbi
    ncbi = NCBITaxa()
    if skip_update is False:
        update_taxdb()
    else:
        logger.info("Skipping Taxonomy Database Update")

    logger.info(f"Searching TaxIDs vs Taxonomy DB")
    taxlist = get_taxonomy(species, ranks)
    taxlist = [i for i in taxlist if i is not None]

    logger.info(f"Writing Taxonomy Information to: {outfile}")
    pd.DataFrame(taxlist, columns=ranks).to_csv(outfile, sep="\t", index=False)
    logger.info(f"Done")

