[![GitHub Actions CI Status](https://github.com/beiko-lab/arete/workflows/nf-core%20CI/badge.svg)](https://github.com/beiko-lab/arete/actions?query=workflow%3A%22nf-core+CI%22)
[![GitHub Actions CI (test) Status](https://github.com/beiko-lab/arete/workflows/nf-test%20CI/badge.svg)](https://github.com/beiko-lab/arete/actions?query=workflow%3A%22nf-test+CI%22)

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A521.03.0--edge-23aa62.svg?labelColor=000000)](https://www.nextflow.io/)
[![run with conda](http://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/en/latest/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)
[![run with singularity](https://img.shields.io/badge/run%20with-singularity-1d355c.svg?labelColor=000000)](https://sylabs.io/docs/)

![ARETE Logo](docs/images/arete-logo-transparent.png)

## Introduction

**ARETE** is a bioinformatics best-practice analysis pipeline for AMR/VF LGT-focused bacterial genomics workflow.

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It uses Docker / Singularity containers making installation trivial and results highly reproducible.
Like other workflow languages it provides [useful features](https://www.nextflow.io/docs/latest/getstarted.html#modify-and-resume) like `-resume` to only rerun tasks that haven't already been completed (e.g., allowing editing of inputs/tasks and recovery from crashes without a full re-run).
The [nf-core](https://nf-cor.re) project provided overall project template, pre-written software modules when available, and general best practice recommendations.

## Pipeline summary

Read processing:

- Raw Read QC ([`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/))
- Read Trimming ([`fastp`](https://github.com/OpenGene/fastp))
- Trimmed Read QC ([`FastQC`](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/))
- Taxonomic Profiling ([`kraken2`](http://ccb.jhu.edu/software/kraken2/))

Assembly:

- Unicycler ([`unicycler`](https://github.com/rrwick/Unicycler))
- QUAST QC ([`quast`](http://quast.sourceforge.net/))
- CheckM QC ([`checkm`](https://github.com/Ecogenomics/CheckM))

Annotation:

- Bakta ([`bakta`](https://github.com/oschwengers/bakta))
- (_optionally_) Prokka ([`prokka`](https://github.com/tseemann/prokka))
- AMR ([`RGI`](https://github.com/arpcard/rgi))
- Plasmids ([`mob_suite`](https://github.com/phac-nml/mob-suite))
- Genomic Islands ([`IslandPath`](https://github.com/brinkmanlab/islandpath))
- Phage identification ([`PhiSpy`](https://github.com/linsalrob/PhiSpy))
- CAZY, VFDB, and BacMet query using DIAMOND ([`diamond`](https://github.com/bbuchfink/diamond))

Phylogeny:

- (_optionally_) Genome subsetting with PopPUNK ([See documentation](./docs/subsampling.md))
- PPanGGOLiN ([`PPanGGOLiN`](https://github.com/labgem/PPanGGOLiN))
- (_optionally_) Panaroo ([`panaroo`](https://github.com/gtonkinhill/panaroo))
- FastTree ([`fasttree`](http://www.microbesonline.org/fasttree/))
- (_optionally_) SNP-sites ([`SNPsites`](https://github.com/sanger-pathogens/snp-sites))
- (_optionally_) IQTree ([`iqtree`](http://www.iqtree.org/))

Other:

- PopPUNK ([`poppunk`](https://poppunk.net/))

Recombination:
Check recombination events within each PopPUNK cluster.

- Verticall ([`verticall`](https://github.com/rrwick/Verticall/))
- SKA2 ([`ska2`](https://github.com/bacpop/ska.rust))
- Gubbins ([`gubbins`](https://github.com/nickjcroucher/gubbins))

See our [roadmap](ROADMAP.md) for future development targets.

## Quick Start

1. Install [`nextflow`](https://nf-co.re/usage/installation)

2. Install [`Docker`](https://www.docker.com), [`Singularity`](https://sylabs.io/guides/3.0/user-guide/installation.html), or, as a last resort, [`Conda`](https://conda.io/miniconda.html). Also ensure you have a working `curl` installed (should be present on almost all systems).

Note: this workflow should also support [`Podman`](https://podman.io/), [`Shifter`](https://nersc.gitlab.io/development/shifter/how-to-use/) or [`Charliecloud`](https://hpc.github.io/charliecloud/) execution for full pipeline reproducibility. We have minimized reliance on `conda` and suggest using it only as a last resort (see [docs](https://nf-co.re/usage/configuration#basic-configuration-profiles)). Configure `mail` on your system to send an email on workflow success/failure (without this you may get a small error at the end `Failed to invoke workflow.onComplete event handler` but this doesn't mean the workflow didn't finish successfully).

3.  Download the pipeline and test with a `stub-run`. The `stub-run` will ensure that the pipeline is able to download and use containers as well as execute in the proper logic.

    ```bash
    nextflow run beiko-lab/ARETE -profile test,<docker/singularity/conda> -stub-run
    ```

    - Please check [nf-core/configs](https://github.com/nf-core/configs#documentation) to see if a custom config file to run nf-core pipelines already exists for your Institute. If so, you can simply use `-profile <institute>` in your command. This will enable either `docker` or `singularity` and set the appropriate execution settings for your local compute environment.
    - If you are using `singularity` then the pipeline will auto-detect this and attempt to download the Singularity images directly as opposed to performing a conversion from Docker images. If you are persistently observing issues downloading Singularity images directly due to timeout or network issues then please use the `--singularity_pull_docker_container` parameter to pull and convert the Docker image instead.

4.  Start running your own analysis (ideally using `-profile docker` or `-profile singularity` for stability)!

        ```bash
        nextflow run beiko-lab/ARETE -profile <docker/singularity> --input_sample_table samplesheet.csv --poppunk_model bgmm
        ```

    `samplesheet.csv` must be formatted `sample,fastq_1,fastq_2`

**Note**: If you get this error at the end `` Failed to invoke `workflow.onComplete` event handler `` it isn't a problem, it just means you don't have an sendmail configured and it can't send an email report saying it finished correctly i.e., its not that the workflow failed.

See [usage docs](docs/usage.md) for all of the available options when running the pipeline.

### Testing

To test the worklow on a minimal dataset you can use the test configuration (with either docker, conda, or singularity - replace `docker` below as appropriate):

    ```bash
    nextflow run beiko-lab/ARETE -profile test,docker
    ```

Due to download speed of the Kraken2, Bakta and CAZY databases this will take ~35 minutes.
However to accelerate it you can download/cache the database files to a folder (e.g., `test/db_cache`) and provide a database cache parameter. As well as set `--bakta_db` to the directory containing the Bakta database.

    ```bash
    nextflow run beiko-lab/ARETE -profile test,docker --db_cache $PWD/test/db_cache --bakta_db $PWD/baktadb/db-light
    ```

## Documentation

The ARETE pipeline comes with documentation about the pipeline: [usage](docs/usage.md) and [output](docs/output.md).

## Credits

ARETE was originally written and developed by [Finlay Maguire](https://github.com/fmaguire) and [Alex Manuele](https://github.com/alexmanuele), and is currently developed by [João Cavalcante](https://github.com/jvfe).

## Contributions and Support

<!--If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).-->

Thank you for your interest in contributing to ARETE. We are currently in the process of formalizing contribution guidelines. In the meantime, please feel free to open an issue describing your suggested changes.

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->

This pipeline uses code and infrastructure developed and maintained by the [nf-core](https://nf-co.re) initative, and reused here under the [MIT license](https://github.com/nf-core/tools/blob/master/LICENSE).

> The nf-core framework for community-curated bioinformatics pipelines.
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> Nat Biotechnol. 2020 Feb 13. doi: 10.1038/s41587-020-0439-x.

In addition, references of tools and data used in this pipeline are as follows can be found in the [`CITATIONS.md`](CITATIONS.md) file.
