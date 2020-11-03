

rule all:
    input:
        [expand("grch38-{build}/genes.gtf.gz", build=range(77, 100)),
         expand("grch38-{build}/genes.csv", build=range(77, 100)),
         expand("grch37-{build}/genes.gtf.gz", build=range(77, 100)),
         expand("grch37-{build}/genes.csv", build=range(77, 100)),
        ]


rule convert_gtf:
    input:
        "{assembly}-{build}/genes.gtf.gz"
    output:
        "{assembly}-{build}/genes.csv"
    params:
        slurm__hours=1,
        slurm__cores=4,
        slurm__mem=5
    shell:
        """
        zcat {input} \
            | awk -F"\\t" '{{if ($3 == "gene") {{split($9, a,";"); print a[1] a[3]}} }}' \
            | cut -d" " -f2,4 --output-delimiter , \
            | tr -d '"' > {output}
        """


rule get_gtf37:
    output:
        "grch37-{build}/genes.gtf.gz"
    params:
        slurm__skip=True
    shell:
        """
        wget \
            ftp://ftp.ensembl.org/pub/grch37/release-{wildcards.build}/gtf/homo_sapiens/Homo_sapiens.GRCh37.{wildcards.build}.gtf.gz \
            -O {output}
        """


rule get_gtf:
    output:
        "grch38-{build}/genes.gtf.gz"
    params:
        slurm__skip=True
    shell:
        """
        wget \
            ftp://ftp.ensembl.org/pub/release-{wildcards.build}/gtf/homo_sapiens/Homo_sapiens.GRCh38.{wildcards.build}.gtf.gz \
            -O {output}
        """
