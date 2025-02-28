process CHUNKED_FASTTREE {
    label 'process_medium'

    conda (params.enable_conda ? "bioconda::fasttree=2.1.10" : null)
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/fasttree:2.1.10--h516909a_4' :
        'quay.io/biocontainers/fasttree:2.1.10--h516909a_4' }"

    input:
    path alignment
    val is_nt

    output:
    path "*.tre",         emit: phylogeny
    path "versions.yml" , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def type = is_nt ? '-nt' : ''
    """
    for aln in \$(ls $alignment); do

    if [[ \$(wc -l <\$aln) -ge 2 ]]; then
        sampleid=\$(basename \$aln .aln)

        fasttree \\
            $args \\
            -log \$sampleid".tre.log" \\
            $type \\
            \$aln \\
            > \$sampleid".tre"
    fi
    done

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        fasttree: \$(fasttree -help 2>&1 | head -1  | sed 's/^FastTree \\([0-9\\.]*\\) .*\$/\\1/')
    END_VERSIONS
    """
    stub:
    """
    touch fasttree_phylogeny.tre
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        fasttree: \$(fasttree -help 2>&1 | head -1  | sed 's/^FastTree \\([0-9\\.]*\\) .*\$/\\1/')
    END_VERSIONS
    """
}
