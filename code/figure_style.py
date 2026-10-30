"""Shared style of all figure panels.

Follows the Nature journals figure guidelines: sans-serif typeface (Arial / Helvetica), text between 5 and 7 pt,
single column 89 mm, double column 183 mm, maximum height 170 mm. Panels are drawn at their final print size,
so the font sizes below are the sizes in the assembled figure.
"""
from pathlib import Path

import matplotlib.pyplot as plt

FONT_SIZE = 7        # Titles, axis labels, legend titles, annotations (maximum allowed)
SMALL_FONT_SIZE = 6  # Tick labels, legend entries, p-values
DENSE_FONT_SIZE = 5  # Gene names and other dense labels (minimum allowed)

MM = 1 / 25.4        # Inches per mm
SINGLE_COLUMN_MM = 89
DOUBLE_COLUMN_MM = 183

IMAGES = Path("../images")


def set_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": FONT_SIZE,
        "axes.titlesize": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "xtick.labelsize": SMALL_FONT_SIZE,
        "ytick.labelsize": SMALL_FONT_SIZE,
        "legend.fontsize": SMALL_FONT_SIZE,
        "legend.title_fontsize": FONT_SIZE,
        "axes.linewidth": 0.5,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.major.size": 2,
        "ytick.major.size": 2,
        "lines.linewidth": 1,
        "patch.linewidth": 0.5,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,  # Keep text editable in the PDFs
        "ps.fonttype": 42,
    })


def figure_size(width_mm, height_mm):
    """Figure size in inches from the size in mm of the final panel."""
    return (width_mm * MM, height_mm * MM)


def save_panel(name, png_dpi=300, tight=True):
    """Save the current figure as PDF and PNG. Use a higher `png_dpi` for panels with many points, where the PNG goes into the paper.

    `tight=False` keeps the full figure canvas instead of cropping to the content, for panels whose axes are placed at fixed positions.
    """
    IMAGES.mkdir(exist_ok=True)
    bbox_inches = "tight" if tight else None
    plt.savefig(IMAGES / f"{name}.pdf", bbox_inches=bbox_inches)
    plt.savefig(IMAGES / f"{name}.png", dpi=png_dpi, bbox_inches=bbox_inches)


# --- Helpers for scanpy dot plots and matrix plots -------------------------------------------------------------------

DOTPLOT_LEGEND_MM = 22  # Width reserved for the legends drawn next to a dot plot


def fit_dots_to_cells(plot, fill=0.8):
    """Rescale the dots of a scanpy DotPlot so that the largest dot (fraction = dot_max) fits inside one cell of the grid.

    Must be called after `make_figure()`, because the size of a cell is taken from the laid-out axes; call it before `add_dotplot_legends`
    so that the size legend uses the rescaled sizes. Dot sizes are areas in points^2, so the diameter of the largest dot is set to `fill` times the
    smaller side of a cell. Scanpy's own sizing does not depend on the figure size and overflows the cells for small figures.
    """
    fig = plot.fig
    ax = plot.ax_dict["mainplot_ax"]
    position = ax.get_position()
    width_pt = position.width * fig.get_figwidth() * 72
    height_pt = position.height * fig.get_figheight() * 72
    n_cols, n_rows = len(plot.var_names), len(plot.categories)
    cell_pt = min(width_pt / n_cols, height_pt / n_rows)
    largest_dot = (fill * cell_pt) ** 2

    factor = largest_dot / plot.largest_dot  # Sizes are proportional to largest_dot when smallest_dot is 0
    for collection in ax.collections:
        collection.set_sizes(collection.get_sizes() * factor)
    plot.largest_dot = largest_dot


def thin_scanpy_lines(plot, bracket_lw=0.5, dendrogram_lw=0.75):
    """Thin the marker group brackets and dendrogram lines of a scanpy DotPlot / MatrixPlot (call after make_figure)."""
    gene_group_ax = plot.ax_dict.get("gene_group_ax")
    if gene_group_ax is not None:
        for patch in gene_group_ax.patches:
            patch.set_linewidth(bracket_lw)
    dendrogram_ax = plot.ax_dict.get("group_extra_ax")
    if dendrogram_ax is not None:
        for line in dendrogram_ax.lines:
            line.set_linewidth(dendrogram_lw)
        for collection in dendrogram_ax.collections:
            collection.set_linewidth(dendrogram_lw)


def add_dotplot_legends(plot, colorbar_title="Mean expression\nin group", size_title="Fraction of cells\nin group (%)", gap_mm=4, width_mm=16):
    """Compact size and colour legends to the right of a scanpy DotPlot created with legend(show=False)."""
    import matplotlib as mpl
    import numpy as np

    fig = plot.fig
    fig_width_mm, fig_height_mm = fig.get_size_inches() * 25.4
    right = max(ax.get_position().x1 for ax in plot.ax_dict.values() if ax is not None)
    top = plot.ax_dict["mainplot_ax"].get_position().y1
    x0 = right + gap_mm / fig_width_mm
    width = width_mm / fig_width_mm

    # Dot size legend
    fractions = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    sizes = fractions**plot.size_exponent * (plot.largest_dot - plot.smallest_dot) + plot.smallest_dot
    size_ax = fig.add_axes([x0, top - 6 / fig_height_mm, width, 4 / fig_height_mm])
    size_ax.scatter(np.arange(len(fractions)), np.zeros(len(fractions)), s=sizes, color="gray", edgecolor="black", linewidth=plot.dot_edge_lw)
    size_ax.set_xticks(np.arange(len(fractions)))
    size_ax.set_xticklabels((fractions * 100).astype(int), fontsize=SMALL_FONT_SIZE)
    size_ax.set_xlim(-0.6, len(fractions) - 0.4)
    size_ax.set_yticks([])
    size_ax.tick_params(axis="x", length=0, pad=1)
    for spine in size_ax.spines.values():
        spine.set_visible(False)
    size_ax.set_title(size_title, fontsize=FONT_SIZE, pad=2)

    # Colour bar
    colorbar_ax = fig.add_axes([x0, top - 22 / fig_height_mm, width, 2.5 / fig_height_mm])
    colorbar = fig.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(0, 1), cmap=plot.cmap), cax=colorbar_ax, orientation="horizontal")
    colorbar.set_ticks([0, 0.5, 1])
    colorbar_ax.tick_params(labelsize=SMALL_FONT_SIZE, length=2, pad=1)
    colorbar_ax.set_title(colorbar_title, fontsize=FONT_SIZE, pad=2)
