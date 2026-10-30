# Reproducibility of the main figures

This repository contains the minimal data and code needed to regenerate the data-based panels of the main figures.
The slide decks and the `data/` and `full/` folders are not committed (`.gitignore`).

```
.
├── code/     Jupyter notebooks, one per figure, and the assembly script
├── data/     Supplementary tables used by the notebooks (git-ignored, see below)
├── images/   Generated panels (PDF and PNG)
├── figures/  Assembled figures (PDF with PNG previews)
├── full/     The complete original analysis (notebooks, raw data, intermediate results); git-ignored, not distributed
├── Vlad_COPD_visualisation_updated.pptx   Assembled figures as editable slides (git-ignored)
├── Emphysema_progression_figures.pptx     The assembled slides after hand editing; the layout of Fig. 1 is read from its first slide (git-ignored)
└── Fig_4.pptx                             Fig. 4 and its supplementary figure as slides (added later, see below; git-ignored)
```

## Notebooks

| Notebook | Panels |
|---|---|
| `code/Fig_1.ipynb` | 1d lung UMAP, 1e blood UMAP |
| `code/Fig_2.ipynb` | 2a SIMs signature (one panel with the lung macrophage and blood monocyte heatmaps, shared colour bar), 2b SIMs proportion in GeoMx data, 2c SIMs proportion in lung single-cell data, 2d CD68 / PRMT7 immunofluorescence micrographs (raw images with labels, scale bar and inset added), 2e PRMT7+ macrophages in lung sections (immunofluorescence quantification), 2f PRMT7+ monocytes proportion in blood single-cell data, 2g predicted percentage of PRMT7+ monocytes in COPDGene, 2h survival by predicted percentage of PRMT7+ monocytes |
| `code/Fig_3.ipynb` | 3a lung DEGs, 3b blood DEGs, 3c validation of lung DEGs in GeoMx data, 3e validation in COPDGene predicted expression, 3f overlap of DEGs |
| `code/Fig_4.ipynb` | 4a association of the MOFAtalk factors with emphysema progression, 4b progression factor scores per sample, 4c sender → receiver views with the most variance explained by the progression factor, 4d SIM receptors with the most nominal incoming hits, 4e-f per-sample scores of the exemplar interactions into SIMs through TLR2 and NRP1; supplementary: expression of TLR2 and NRP1 in SIM pseudobulks |
| `code/Fig_S_annotation_markers.ipynb` | Supplementary: dot plots of annotation marker genes for the lung and blood cell types |
| `code/Fig_S_macrophage_markers.ipynb` | Supplementary: dot plots of macrophage subtype markers and inflammation markers in lung macrophages |
| `code/Fig_S_cells_per_sample.ipynb` | Supplementary: heatmap of the median percentage of cells of each lung cell type coming from one sample, per batch |
| `code/Fig_S_spatial_markers.ipynb` | Supplementary: unfiltered version of Fig. 3c with all lung DEGs validated in the GeoMx data |
| `code/figure_style.py` | Shared style: fonts, sizes and the `save_panel` helper used by all notebooks |
| `code/assemble_figures.py` | Assembles the panels into the figures: `figures/*.pdf` (vector) with PNG previews, and the slide deck `Vlad_COPD_visualisation_updated.pptx` (one slide per figure) |
| `code/00_prepare_tables_from_raw_data.ipynb` | Not needed to make the figures. Documents how the tables in `data/` were derived from the full single-cell objects, GeoMx and COPDGene files, which are not distributed here. |
| `code/00_prepare_ccc_tables.ipynb` | Not needed to make the figures. Documents how the cell-cell communication tables of Fig. 4 (Supplementary Tables 10-17) were extracted from the results of the cell-cell communication analysis (`full/ccc_progression/`, not distributed here). |

Panels not generated from data: 1a-c, 3d (schematics).

Each notebook runs from the `code` directory and writes its panels to `images/` as `Fig_<figure>_<panel>_<description>.pdf` and `.png`.
The assembly script then lays the panels out into the figures.

```bash
cd code
jupyter nbconvert --to notebook --execute --inplace Fig_1.ipynb Fig_2.ipynb Fig_3.ipynb Fig_4.ipynb Fig_S_annotation_markers.ipynb Fig_S_macrophage_markers.ipynb Fig_S_cells_per_sample.ipynb Fig_S_spatial_markers.ipynb
python assemble_figures.py
```

The assembly script can also render a subset of the figures without touching the others, e.g. Fig. 4 and its supplementary figure
into their own deck (this is how `Fig_4.pptx` was made, after the slides of Fig. 1-3 had been edited by hand in `Emphysema_progression_figures.pptx`):

```bash
python assemble_figures.py Fig_4 Supp_Fig_ccc_focus_receptors_expression --deck ../Fig_4.pptx
```

The schematic of Fig. 3d and the tissue icons next to the panel letters are taken from the original slide deck
`Vlad_COPD_visualisation.pptx` by the assembly script (it needs `pymupdf` and `python-pptx`). Fig. 1 (schematics 1a-c and the UMAPs 1d-e)
is reproduced exactly as laid out by hand on the first slide of `Emphysema_progression_figures.pptx`, including the crop of the UMAP's margin;
the positions of the panels of Fig. 2 follow the second slide of that deck, with the new panels 2d-e in the place of the former
imaging mass cytometry panels.

## Data

The `data/` folder is excluded from version control (`.gitignore`) because it holds per-sample tables, including the
COPDGene-derived table, which is not public. The notebooks only display aggregate results (shapes, group summaries, model
summaries and figures), never rows of these tables.

Each table used for a figure is a supplementary table of the paper. The files are named `<table number>_<content>.csv` and numbered
in the order in which they appear in the analysis, starting from 2 because Supplementary Table 1 (cohort description) is already part of
the paper. Tables that are stored in, or can be recomputed from, the shared AnnData objects (UMAP coordinates, mean latent representations, signature log fold changes), the two colour tables and the immunofluorescence inputs are not supplementary tables and keep their names.

### Supplementary tables

| Table | File | Content | Used in |
|---|---|---|---|
| 2 | `2_GeoMx_deconvolution_proportions.csv` | Deconvolved cell type proportions (%) of each GeoMx region of interest (`Mixture`), with its region, emphysema status and progression group | 2b |
| 3 | `3_lung_immune_cell_type_proportions.csv` | Percentage of each immune cell type among the immune cells of each lung sample, the number of cells of the sample (`n_cells`), smoking status and emphysema progression | 2c |
| 4 | `4_blood_cell_type_proportions.csv` | Percentage of each cell type in each blood sample, number of cells, smoking status and emphysema progression | 2f |
| 5 | `5_bulk_COPDGene_PRMT7_monocytes.csv` | Predicted fraction of PRMT7+ monocytes (InstaPrism) per COPDGene sample with the covariates of the mixed model (emphysema progression, lung density, percent emphysema, sex, smoking status, age, sequencing batch) and the survival data (vital status, days of follow-up since phase 2). Subject identifiers are removed and batches are recoded. Not public: distributed only under the COPDGene data use agreement. | 2g, 2h |
| 6 | `6_lung_deg_results.csv` | Cell type-specific pseudobulk differential expression (edgeR) between fast and slow progressors in the lung single-cell data: gene, log fold change, log CPM, F statistic, p-value and FDR per cell type and emphysema status | 3a, 3c, 3f, supplementary |
| 7 | `7_blood_deg_results.csv` | Same for the blood single-cell data | 3b, 3f |
| 8 | `8_GeoMx_DEG_results.csv` | Differential expression between fast and slow progressors in the GeoMx data (sheet "DE all" of the original spreadsheet): log fold changes and adjusted p-values per region, overall and within emphysema (`E`) and non-emphysema (`NOE`) samples | 3c, supplementary |
| 9 | `9_bulk_dge_results/<cell type>_Design2_emphysema_progression.csv` | Differential expression (limma) between fast and slow progressors of the predicted cell type-specific expression in COPDGene, one file per cell type (classical monocytes, PRMT7+ monocytes, CD4 T cells, regulatory T cells): gene, log fold change, p-value, adjusted p-value, average expression and confidence interval | 3e, 3f |
| 10 | `10_ccc_mofa_factor_progression_tests.csv` | t statistic and p-value of fast vs slow progression for each MOFAtalk factor (mixed model adjusted for batch, sex, emphysema and detection rate) | 4a |
| 11 | `11_ccc_samples.csv` | Emphysema progression group and MOFAtalk progression factor (Factor1) score of each lung sample of the cell-cell communication analysis | 4b, 4e, 4f, supplementary |
| 12 | `12_ccc_mofa_progression_factor_r2_per_view.csv` | Variance explained (R², %) by the progression factor in each sender → receiver view | 4c |
| 13 | `13_ccc_sim_receptor_summary.csv` | Per receptor on SIMs: number of incoming interactions with p < 0.05, mean t of the incoming interaction scores and edgeR statistic of the receptor gene in SIM pseudobulks | 4d |
| 14 | `14_ccc_exemplar_interaction_tests.csv` | Test results (t statistic, p-value) of the exemplar interactions DC1 → SIM: HMGB1 → TLR2 and DC2 → SIM: VEGFA → NRP1 | 4e, 4f |
| 15 | `15_ccc_exemplar_interaction_scores.csv` | Per-sample scores of the two exemplar interactions | 4e, 4f |
| 16 | `16_ccc_sim_pseudobulk_log_cpm.csv` | TLR2 and NRP1 expression (log1p CPM) in the SIM pseudobulk of each sample | Supplementary |
| 17 | `17_ccc_sim_edger_focus_receptors.csv` | edgeR test results (log fold change, p-value) of TLR2 and NRP1 in SIM pseudobulks, fast vs slow progressors | Supplementary |
| 18 | `18_lung_annotation_markers_mean_expression.csv` | Mean log-normalised expression of the annotation marker genes (columns) per lung cell type (rows) | Supplementary dot plot |
| 19 | `19_lung_annotation_markers_fraction_expressing.csv` | Fraction of cells expressing each annotation marker gene per lung cell type | Supplementary dot plot |
| 20 | `20_blood_annotation_markers_mean_expression.csv` | Mean log-normalised expression of the annotation marker genes per blood cell type | Supplementary dot plot |
| 21 | `21_blood_annotation_markers_fraction_expressing.csv` | Fraction of cells expressing each annotation marker gene per blood cell type | Supplementary dot plot |
| 22 | `22_lung_cell_counts_per_sample.csv` | Number of cells of each cell type (rows) in each lung sample (columns) | Supplementary heatmap |
| 23 | `23_lung_macrophage_markers_mean_expression.csv` | Mean log-normalised expression of macrophage and inflammation marker genes per lung macrophage subtype | Supplementary dot plots |
| 24 | `24_lung_macrophage_markers_fraction_expressing.csv` | Fraction of cells expressing each macrophage and inflammation marker gene per lung macrophage subtype | Supplementary dot plots |

### Other inputs

The first six files are derived from the shared AnnData objects by `00_prepare_tables_from_raw_data.ipynb` and are kept here only so that the notebooks run without the objects.

| File | Content | Used in |
|---|---|---|
| `lung_umap.csv` | UMAP coordinates (`UMAP1`, `UMAP2`) and cell type annotation of every cell of the lung single-cell data, one row per cell | 1d |
| `blood_umap.csv` | UMAP coordinates and cell type annotation of every cell of the blood single-cell data, one row per cell | 1e |
| `lung_macrophages_SIMs_signature_logFC.csv` | Log fold change of each SIMs signature gene (columns) in each lung macrophage subtype (rows) versus the other macrophages (scanpy t-test on log-normalised data) | 2a |
| `lung_macrophages_scanvi_mean.csv` | Mean scANVI latent representation (30 dimensions) of each lung macrophage subtype, used for the dendrogram ordering the subtypes | 2a, supplementary dot plots |
| `blood_monocytes_SIMs_signature_logFC.csv` | Log fold change of each SIMs signature gene in each blood monocyte subtype versus the other monocytes | 2a |
| `blood_monocytes_pca_mean.csv` | Mean PCA representation (100 components) of each blood monocyte subtype, used for the dendrogram | 2a |
| `lung_cell_type_colors.csv`, `blood_cell_type_colors.csv` | Colour of each cell type (styling only) | 1d, 1e |
| `SIMs_fluorescence_validation/Raw data for PRMT7 XW updated.xlsx` | Counts of PRMT7+ and total CD68+ macrophages per lung section (immunofluorescence), current smokers without emphysema, fast and slow progressors | 2e |
| `SIMs_fluorescence_validation/raw_images/*.png` | Raw CD68, PRMT7 and merged micrographs of a slow and a fast progressor, and the magnified region of the fast merged image, extracted from the embedded Photoshop objects of `PRMT7 Mac raw data.pptx` (same folder; `python-pptx` cannot read them, they were unpacked with `olefile` from the `CONTENTS` streams of `ppt/embeddings/oleObject*.bin`) | 2d |

## Environment

Python 3.11 with scanpy 1.9.6, anndata 0.10.9, pandas 2.2.3, seaborn 0.13.2, matplotlib 3.8.2, statsmodels 0.14.5, lifelines 0.29.0, matplotlib-venn, adjustText.

## Figure style

All panels follow the Nature journals figure guidelines (`code/figure_style.py`): Arial, text between 5 and 7 pt
(7 pt for titles, axis labels and legend titles; 6 pt for tick labels, legend entries and p-values; 5 pt for gene names and other dense labels),
panels drawn at their final print size (single column 89 mm, double column 183 mm) and PDFs with editable text.
The size of each panel is set in its notebook with `figure_size(width_mm, height_mm)`; the panel sizes are chosen so that each
assembled figure is 183 mm wide and at most 170 mm tall, with 8 pt bold lower-case panel letters (`code/assemble_figures.py`).
Fig. 2d lays the raw micrographs out with the two sections as columns and the channels as rows (27 x 43 mm); the channel labels, the 20 µm scale bar
(length taken from the original slide, slow CD68 image only, as there) and the magnified region of the fast merged image (region from the original slide) are drawn by the notebook.
In the UMAPs, cell type labels (5 pt, in the cell type colours) are placed outside the embedding and connected to the cluster medians, so the panels are wider than the embedding itself.
Dot sizes in the dot plots are fitted to the cells of the laid-out plot (`fit_dots_to_cells`), so they never overlap.

## Notes

- Group labels in Fig. 4 and its supplementary figure: NE no emphysema, E emphysema; slow and fast emphysema progression. The panels of Fig. 4 are saved uncropped with their axes at fixed positions (`panel_axes` in `Fig_4.ipynb`, `save_panel(..., tight=False)`), so that the axes of a row align in the assembled figure.
- The p-values in Fig. 4a are nominal (linear models of the factor scores adjusted for batch, sex, emphysema and detection rate, donor-clustered standard errors). Panels 4e-f show the interactions with the lowest nominal p-value into the two focus receptors without p-values, because they were selected as the strongest cases and no SIM interaction reaches FDR < 0.1. The statistics were computed in the original analysis, the notebook only draws them.
- Significance in Fig. 2 uses the star notation (`p_value_label` in `Fig_2.ipynb`): *** p < 0.001, ** p < 0.01, * p < 0.05, ns not significant; Fig. 2e (Welch's t-test, fast vs slow, 5 vs 4 sections) and 2g (mixed model) show the exact p-value. The exact p-values are printed in the notebook.
- Confidence intervals of bar plots are bootstrapped by seaborn; the notebooks fix the random seed, so values can differ marginally from the published panels.
- The original notebooks of the analysis are in `full/` (`13_lung_data_analysis.ipynb`, `14_spatial_data_analysis.ipynb`, `16_blood_data_analysis.ipynb`, `17_overlapping_markers_analysis.ipynb`, `18_mac_mono_exploration.ipynb`, `31_analyse_bulk_data.ipynb`) and, for Fig. 4, in `full/ccc_progression/` (`15a_ccc_progression_compute.ipynb` computes, `15b_ccc_progression_figures.ipynb` draws the original figures; Fig. 4 corresponds to its `Figure1_main` without the volcano plot).
