#!/bin/env python
import os
import sys
import gzip

ref_dir = os.path.realpath(os.path.dirname(__file__))

def read_genes(f, idx=0, attribute="gene_id"):
    result = []
    sep = "\t"

    if f.endswith(".tsv"):
        with open(f, "rt") as csv_file:
            for line in csv_file:
                value = line.strip().split(sep)[idx]
                if value and value[0] == '"' and value[-1] == '"':
                    value = value[1:-1].replace('""', '"')
                if value:
                    result.append(value)
    elif f.endswith(".gz"):
        with gzip.open(f, "rt") as gz_file:
            for line in gz_file:
                if line.startswith("#"):
                    continue  # Skip comment lines

                fields = line.strip().split(sep)
                if fields[2] == "gene":  # Check if 'Feature' is 'gene'
                    gene_attribute = None
                    for attr in fields[8].split(';'):
                        key, val = attr.strip().split(" ")
                        if key == attribute:
                            gene_attribute = val.strip('"')
                            break
                    if gene_attribute:
                        result.append(gene_attribute)
    else:
        with open(f, "rt") as txt_file:
            for line in txt_file:
                if line.startswith("#"):
                    continue  # Skip comment lines

                fields = line.strip().split(sep)
                if fields[2] == "gene":  # Check if 'Feature' is 'gene'
                    gene_attribute = None
                    for attr in fields[8].split(';'):
                        key, val = attr.strip().split(" ")
                        if key == attribute:
                            gene_attribute = val.strip('"')
                            break
                    if gene_attribute:
                        result.append(gene_attribute)

    return result


def which_build(features, verbose=False):
    result = {}
    min_genes = None
    min_answer = None
    given_genes = read_genes(features)
    is_ensembl_ids = given_genes[0].startswith("ENS")
    ref_idx = 0
    if not is_ensembl_ids:
        ref_idx = 1
        attribute = 'gene_name'
    for d in os.listdir(ref_dir):
        dir_path = os.path.join(ref_dir, d)
        if not os.path.isdir(dir_path):
            continue
        ref_genes_path = os.path.join(dir_path, "genes.gtf.gz")
        if not os.path.exists(ref_genes_path):
            continue
        ref_genes = read_genes(ref_genes_path, idx=ref_idx,attribute=attribute)
        result[d] = set(given_genes) - set(ref_genes)
        if min_genes is None:
            min_genes = len(result[d])
            min_answer = [d]
        elif len(result[d]) < min_genes:
            min_genes = len(result[d])
            min_answer = [d]
        elif len(result[d]) == min_genes:
            min_answer.append(d)
    if min_genes == 0:
        if len(min_answer) == 1:
            print(f"All genes in {features} come from build {min_answer[0]}")
        else:
            print(f"All genes in {features} come from builds {', '.join(min_answer)}")
    else:
        print(f"No build provides full set of genes for {features}. Here's the number of missing genes per build:")
        for build, genes in sorted(result.items(), key=lambda x: len(x[1])):
            print(f"  {build}: {len(genes)}")
        if verbose:
            for build, genes in sorted(result.items(), key=lambda x: len(x[1])):
                print(f"Genes absent in build {build}:")
                genes = list(genes)
                for i in range(-(len(genes) // -10)): # this is math.ceil equivalent
                    print(f"  {' '.join(genes[i * 10:(i + 1) * 10])}")
                break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: which_genome.py [-v] path/to/cellbrowser/features.tsv.gz")
        sys.exit(1)
    args = []
    verbose = False
    for i in sys.argv[1:]:
        if i == "-v":
            verbose = True
        else:
            args.append(i)

    print(ref_dir)
    which_build(*args, verbose=verbose)
