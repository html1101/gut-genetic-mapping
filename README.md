# Reproduction of Gut Microbiome Heritability Paper

Link to paper [here](https://elifesciences.org/articles/75419)!

## Data available from Github

The following is data available within the researcher's linked GitHub (linked as a submodule in `./reference_code`)

- `reference_code/Data/genotypes/clean_f2.{bed,bim,fam}`: 320 mice, 32,625 mouse SNPs (already present in the author-code submodule).
- `reference_code/Data/phenotypes/`: processed bacterial relative abundances, 606 assay profiles over DNA and RNA; six taxonomic ranks, plus taxonomy tables.
- `reference_code/Data/trait.list.{dna,rna}.csv`: assay-specific core-taxon lists.
- `data/external/elife-75419-supp1-v1.xlsx`: downloaded published estimates and ASV taxonomy.
- `data/external/PRJNA759194_runs.tsv`: downloaded ENA inventory of 700 SRA runs, URLs, sizes and checksums.
- `data/external/SRR15677983.fastq.gz`: one real FASTQ example, verified against the manifest's MD5.
- `data/external/published_figure1.jpg`: original figure for comparison.
- `data/external/provenance.json`: URLs, reference-code commit, file sizes and SHA-256 checksums.

