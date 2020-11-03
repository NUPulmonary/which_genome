import os
import sys
import gzip


ref_dir = os.path.realpath(os.path.dirname(__file__))


def read_genes(f):
    result = []
    sep = "\t"
    if f.endswith(".csv"):
        f = open(f, "rt")
        sep = ","
    elif f.endswith(".gz"):
        f = gzip.open(f, "rt")
    else:
        f = open(f, "rt")

    for l in f:
        result.append(l.split(sep)[0])
    f.close()
    return result


def which_build(features):
    result = {}
    min_genes = None
    min_answer = None
    given_genes = read_genes(features)
    for d in os.listdir(ref_dir):
        dir_path = os.path.join(ref_dir, d)
        if not os.path.isdir(dir_path):
            continue
        ref_genes_path = os.path.join(dir_path, "genes.csv")
        if not os.path.exists(ref_genes_path):
            continue
        ref_genes = read_genes(ref_genes_path)
        result[d] = len(set(given_genes) - set(ref_genes))
        if min_genes is None:
            min_genes = result[d]
            min_answer = [d]
        elif result[d] < min_genes:
            min_genes = result[d]
            min_answer = [d]
        elif result[d] == min_genes:
            min_answer.append(d)
    if min_genes == 0:
        if len(min_answer) == 1:
            print(f"All genes in {features} come from build {min_answer[0]}")
        else:
            print(f"All genes in {features} come from builds {', '.join(min_answer)}")
    else:
        print(f"No build provides full set of genes for {features}. Here's the number of missing genes per build:")
        for build, num in sorted(result.items(), key=lambda x: x[1]):
            print(f"  {build}: {num}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: which_genome.py path/to/cellbrowser/features.tsv.gz")
        sys.exit(1)
    which_build(sys.argv[1])
