process PANAROO_RUN {
    tag "$meta.id"
    label 'process_high'

    conda (params.enable_conda ? "bioconda::panaroo=1.3.2" : null)
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/panaroo:1.3.2--pyhdfd78af_0':
        'quay.io/biocontainers/panaroo:1.3.2--pyhdfd78af_0' }"

    input:
    tuple val(meta), path(gff)

    output:
    tuple val(meta), path("results/*")                                      , emit: results
    tuple val(meta), path("results/final_graph.gml")        , optional: true, emit: graph_gml
    tuple val(meta), path("results/core_gene_alignment.aln"), optional: true, emit: aln
    path "results/aligned_gene_sequences/*aln.fas"          , optional: true, emit: accessory_aln
    path "versions.yml"                                                     , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    panaroo \\
        $args \\
        -t $task.cpus \\
        -o results \\
        -i $gff

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        panaroo: \$(echo \$(panaroo --version 2>&1) | sed 's/^.*panaroo //' ))
    END_VERSIONS
    """
    stub:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    mkdir -p results/aligned_gene_sequences/
    touch results/core_gene_alignment.aln
    touch results/final_graph.glm
    touch results/aligned_gene_sequences/group_0001.aln.fas
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        panaroo: \$(echo \$(panaroo --version 2>&1) | sed 's/^.*panaroo //' ))
    END_VERSIONS
    """
}
