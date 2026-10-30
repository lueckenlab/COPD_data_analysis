"""Assemble the panels from ../images into the main and supplementary figures.

Every figure is laid out once, in millimetres on a 183 mm wide canvas (Nature double column, at most 170 mm tall),
and rendered twice: as a vector PDF (../figures/*.pdf, with PNG previews) and as slides of an editable PowerPoint deck
(../Vlad_COPD_visualisation.pptx). Panel labels are 8 pt bold lower-case letters; all other text is Arial, 5-7 pt.

The schematic parts of Fig. 1a-c and Fig. 3d (BioRender icons and text) are not produced by the notebooks. Fig. 1 is taken as
laid out by hand on the first slide of LAYOUT_DECK (panels included); the schematic of Fig. 3d and the tissue icons come from the
original slide deck (ORIGINAL_DECK) and are re-laid out here.

Usage: python assemble_figures.py                      all figures and the full deck
       python assemble_figures.py Fig_4 --deck ../Fig_4.pptx   only the named figures, deck written to --deck
"""
import argparse
import io
from pathlib import Path

import pymupdf
from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Mm, Pt

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
IMAGES = ROOT / "images"
FIGURES = ROOT / "figures"
ORIGINAL_DECK = ROOT / "Vlad_COPD_visualisation.pptx"
LAYOUT_DECK = ROOT / "Emphysema_progression_figures.pptx"  # Generated deck edited by hand: the source of the layout of Fig. 1
OUTPUT_DECK = ROOT / "Vlad_COPD_visualisation_updated.pptx"

PAGE_WIDTH_MM = 183
MAX_HEIGHT_MM = 170
LABEL_PT = 8      # Panel letters: 8 pt bold
TEXT_PT = 7       # Regular text
SMALL_TEXT_PT = 5 # Small annotations (minimum allowed)
ICON_MM = 5       # Tissue icons next to the panel letters

FONTS = {
    "regular": "/System/Library/Fonts/Supplemental/Arial.ttf",
    "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
}
PT_PER_MM = 72 / 25.4


# --- Items of the original deck -------------------------------------------------------------------------------------
def deck_shapes(slide_index, deck=ORIGINAL_DECK):
    """Shapes of a slide of a deck as plain dicts (positions in mm)."""
    slide = Presentation(deck).slides[slide_index]
    shapes = []
    for shape in slide.shapes:
        item = {
            "id": shape.shape_id, "name": shape.name, "x": shape.left / 36000, "y": shape.top / 36000,
            "w": shape.width / 36000, "h": shape.height / 36000,
        }
        if shape.shape_type == 13:  # Picture
            item.update(
                kind="image", blob=shape.image.blob, ext=shape.image.ext,
                crop=(shape.crop_left, shape.crop_top, shape.crop_right, shape.crop_bottom),
            )
        elif shape.has_text_frame and shape.text_frame.text.strip():
            frame = shape.text_frame
            run = frame.paragraphs[0].runs[0]
            item.update(
                kind="text", text=frame.text, align=str(frame.paragraphs[0].alignment or "LEFT"),
                anchor="middle" if frame.vertical_anchor == MSO_ANCHOR.MIDDLE else "top",
                size=run.font.size.pt if run.font.size else TEXT_PT, bold=bool(run.font.bold),
            )
        else:
            continue
        shapes.append(item)
    return shapes


def rescale(shapes, scale, dx, dy, exclude=()):
    """Scale shapes about the origin and shift them; text sizes are mapped onto the Nature sizes (7 pt, 5 pt)."""
    out = []
    for shape in shapes:
        if shape["id"] in exclude:
            continue
        item = dict(shape, x=shape["x"] * scale + dx, y=shape["y"] * scale + dy, w=shape["w"] * scale, h=shape["h"] * scale)
        if item["kind"] == "text":
            if item["bold"] and item["size"] >= 12:  # Panel letter
                item.update(kind="label", text=item["text"].lower())
            else:
                item["size"] = SMALL_TEXT_PT if item["size"] < 6 else TEXT_PT
        out.append(item)
    return out


def drawing_order(items):
    """Panels first, then icons and text on top, so that the white margins of the panels do not hide them."""
    return sorted(items, key=lambda item: {"panel": 0, "image": 1}.get(item["kind"], 2))


def layout_items(slide_index):
    """Items of a slide of the hand-edited deck, as laid out there: panels (pictures named after a panel), images and text.

    Panel letters are the bold single-letter text boxes. Cropped panels keep their crop.
    """
    items = []
    for shape in deck_shapes(slide_index, deck=LAYOUT_DECK):
        if shape["kind"] == "image" and (IMAGES / f"{shape['name']}.pdf").exists():
            item = panel(shape["name"], shape["x"], shape["y"], raster="UMAP" in shape["name"], crop=shape["crop"])
            item.update(w=shape["w"], h=shape["h"])  # Size as placed by hand
        elif shape["kind"] == "text" and shape["bold"] and len(shape["text"]) == 1:
            item = label(shape["text"], shape["x"], shape["y"])
        else:
            item = dict(shape)
        items.append(item)
    return items


def bounding_box(shapes):
    x0 = min(s["x"] for s in shapes)
    y0 = min(s["y"] for s in shapes)
    x1 = max(s["x"] + s["w"] for s in shapes)
    y1 = max(s["y"] + s["h"] for s in shapes)
    return x0, y0, x1, y1


# --- Layout helpers ---------------------------------------------------------------------------------------------------
def panel_size(name):
    rect = pymupdf.open(IMAGES / f"{name}.pdf")[0].rect
    return rect.width / PT_PER_MM, rect.height / PT_PER_MM


def panel(name, x, y, width=None, raster=False, crop=(0, 0, 0, 0)):
    """A panel produced by the notebooks, placed at (x, y) mm; `width` rescales it (the aspect ratio is kept).

    `crop` = fractions (left, top, right, bottom) of the panel cut away; (x, y) and the size are those of the visible part.
    """
    w, h = panel_size(name)
    if width is not None:
        h, w = h * width / w, width
    left, top, right, bottom = crop
    return {"kind": "panel", "name": name, "x": x, "y": y, "w": w * (1 - left - right), "h": h * (1 - top - bottom), "raster": raster, "crop": crop}


def label(letter, x, y):
    return {"kind": "label", "text": letter, "x": x, "y": y, "w": 6, "h": 5}


def text(string, x, y, w, h, size=TEXT_PT, align="CENTER", anchor="top"):
    return {"kind": "text", "text": string, "x": x, "y": y, "w": w, "h": h, "size": size, "align": align, "anchor": anchor, "bold": False}


def icon(blob, x, y, height=ICON_MM):
    pix = pymupdf.Pixmap(blob)
    return {"kind": "image", "blob": blob, "x": x, "y": y, "w": height * pix.width / pix.height, "h": height}


def clip_rect(item, rect):
    """The part of a panel's own page that is visible after cropping (in points), or None without crop."""
    left, top, right, bottom = item.get("crop", (0, 0, 0, 0))
    if not any((left, top, right, bottom)):
        return None
    return pymupdf.Rect(rect.x0 + left * rect.width, rect.y0 + top * rect.height, rect.x1 - right * rect.width, rect.y1 - bottom * rect.height)


# --- Figures ----------------------------------------------------------------------------------------------------------
def figure_1():
    """Schematics (a-c) and UMAPs (d, e), exactly as laid out by hand on the first slide of LAYOUT_DECK."""
    return layout_items(0)


def figure_2(icons):
    """SIMs signature (a), SIMs proportions (b, c), immunofluorescence of PRMT7 in lung macrophages (d micrographs, e quantification),
    PRMT7+ monocytes in blood (f-h). Positions as laid out by hand in LAYOUT_DECK, with d and e replaced."""
    lung, blood = icons["lung"], icons["blood"]
    y2, y3 = 47, 95
    items = [
        label("a", 1, 1), panel("Fig_2_a_SIMs_signature", 0, 0, width=178, crop=(0.012, 0, 0, 0)),  # Left margin cut to start at the page edge
        icon(lung, 0, 8), icon(blood, 0, 8 + 5 * 3.5 + 3),  # Next to the rows of the lung macrophages and of the blood monocytes
        label("b", 1, y2), icon(lung, 1, y2 + 6), panel("Fig_2_b_SIMs_spatial", 4, y2),
        label("c", 70, y2), icon(lung, 70, y2 + 6), panel("Fig_2_c_SIMs_proportion_SC", 73, y2),
        label("d", 118, y2), icon(lung, 118, y2 + 6), panel("Fig_2_d_PRMT7_immunofluorescence", 121.5, y2 + 2),
        label("e", 149.5, y2), icon(lung, 149.5, y2 + 4), panel("Fig_2_e_PRMT7_macrophages_IF", 151, y2),  # Icon above the y label
        label("f", 1, y3), icon(blood, 1, y3 + 6), panel("Fig_2_f_PRMT7_monocytes_proportion", 4, y3),
        label("g", 53, y3), icon(blood, 53, y3 + 6), text("bulk", 49, y3 + 12, 12, 3, size=SMALL_TEXT_PT), panel("Fig_2_g_PRMT7_monocytes_bulk", 56, y3),
        label("h", 104, y3), icon(blood, 104, y3 + 6), text("bulk", 100, y3 + 12, 12, 3, size=SMALL_TEXT_PT), panel("Fig_2_h_PRMT7_monocytes_survival", 107, y3),
    ]
    return items


def figure_3(icons):
    lung, blood = icons["lung"], icons["blood"]
    # Schematic of the bulk validation (text boxes and arrows) from the original deck
    schematic = [s for s in deck_shapes(3) if s["id"] in (5, 6, 7, 8, 9, 10, 11)]
    x0, y0, _, _ = bounding_box(schematic)
    y2 = 108
    items = rescale(schematic, scale=0.8, dx=3 - x0 * 0.8, dy=y2 + 3 - y0 * 0.8)
    items += [
        label("a", 1, 1), icon(lung, 1, 7), panel("Fig_3_a_lung_DEGs", 4, 0),
        label("b", 1, 56), icon(blood, 1, 62), panel("Fig_3_b_blood_DEGs", 4, 55),
        label("c", 126, 1), icon(lung, 126, 7), panel("Fig_3_c_spatial_validation", 129, 0),
        label("d", 1, y2),
        label("e", 66, y2), panel("Fig_3_e_bulk_validation", 69, y2),
        label("f", 126, y2), panel("Fig_3_f_markers_overlap", 129, y2),
    ]
    return items


def figure_4():
    """Cell-cell communication: a-c in the first row, d (receptor summary) and e-f (exemplar interactions) in the second.

    The panels are saved uncropped with their axes at fixed positions, so placing them at the same y aligns the axes of a row.
    """
    y2 = 52
    items = [
        label("a", 0, 0), panel("Fig_4_a_mofa_factors", 1, 0),
        label("b", 44, 0), panel("Fig_4_b_progression_factor_scores", 45, 0),
        label("c", 90, 0), panel("Fig_4_c_top_views", 91, 0),
        label("d", 0, y2), panel("Fig_4_d_sim_receptors", 1, y2),
        label("e", 76, y2), panel("Fig_4_e_TLR2_interaction", 77, y2),
        label("f", 126, y2), panel("Fig_4_f_NRP1_interaction", 127, y2),
    ]
    return items


SUPPLEMENTARY = [
    "Supp_Fig_lung_annotation_markers",
    "Supp_Fig_blood_annotation_markers",
    "Supp_Fig_lung_macrophage_markers",
    "Supp_Fig_lung_macrophage_inflammation_markers",
    "Supp_Fig_lung_cells_per_sample_batch",
    "Supp_Fig_spatial_validation_all_genes",
    "Supp_Fig_ccc_focus_receptors_expression",
]


def all_figures():
    slide_2 = {s["id"]: s for s in deck_shapes(1)}
    icons = {"lung": slide_2[11]["blob"], "blood": slide_2[12]["blob"]}
    figures = {"Fig_1": figure_1(), "Fig_2": figure_2(icons), "Fig_3": figure_3(icons), "Fig_4": figure_4()}
    for name in SUPPLEMENTARY:
        figures[name] = [panel(name, 0, 0)]
    return figures


# --- Renderers --------------------------------------------------------------------------------------------------------
def render_pdf(items, path):
    _, _, _, bottom = bounding_box(items)
    height = min(max(bottom + 1, 20), MAX_HEIGHT_MM)
    doc = pymupdf.open()
    page = doc.new_page(width=PAGE_WIDTH_MM * PT_PER_MM, height=height * PT_PER_MM)
    for item in drawing_order(items):
        rect = pymupdf.Rect(item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"]) * PT_PER_MM
        if item["kind"] == "panel":
            if item["raster"]:  # UMAPs: one vector point per cell makes the PDF heavy, the 1200 dpi PNG is used instead
                pixmap = pymupdf.Pixmap(str(IMAGES / f"{item['name']}.png"))
                clip = clip_rect(item, pymupdf.Rect(0, 0, pixmap.width, pixmap.height))
                if clip is not None:
                    pixmap = pymupdf.Pixmap(pixmap, pixmap.width, pixmap.height, clip.irect)  # Clip without resampling
                page.insert_image(rect, pixmap=pixmap)
            else:
                source = pymupdf.open(IMAGES / f"{item['name']}.pdf")
                page.show_pdf_page(rect, source, 0, clip=clip_rect(item, source[0].rect))
        elif item["kind"] == "image":
            page.insert_image(rect, stream=item["blob"])
        elif item["kind"] in ("label", "text"):
            bold = item["kind"] == "label"
            size = LABEL_PT if bold else item["size"]
            align = {"LEFT": pymupdf.TEXT_ALIGN_LEFT, "CENTER": pymupdf.TEXT_ALIGN_CENTER, "RIGHT": pymupdf.TEXT_ALIGN_RIGHT}
            key = next((k for k in align if k in str(item.get("align", "LEFT"))), "LEFT")
            lines = item["text"].count("\n") + 1
            if item.get("anchor") == "middle":
                rect.y0 += max(0, (rect.height - lines * size * 1.2) / 2)
            rect.y1 = max(rect.y1, rect.y0 + lines * size * 1.3 + 2)
            page.insert_textbox(
                rect, item["text"], fontsize=size, fontname="ArialB" if bold else "Arial",
                fontfile=FONTS["bold" if bold else "regular"], align=align[key],
            )
    doc.save(path, garbage=3, deflate=True)
    pymupdf.open(path)[0].get_pixmap(dpi=200).save(path.with_suffix(".png"))
    return height


def render_pptx(figures, path):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Mm(PAGE_WIDTH_MM), Mm(MAX_HEIGHT_MM)
    blank = prs.slide_layouts[6]
    for name, items in figures.items():
        slide = prs.slides.add_slide(blank)
        for item in drawing_order(items):
            x, y, w, h = (Mm(item[k]) for k in ("x", "y", "w", "h"))
            if item["kind"] == "panel":
                picture = slide.shapes.add_picture(str(IMAGES / f"{item['name']}.png"), x, y, width=w, height=h)
                picture.name = item["name"]
                picture.crop_left, picture.crop_top, picture.crop_right, picture.crop_bottom = item.get("crop", (0, 0, 0, 0))
            elif item["kind"] == "image":
                slide.shapes.add_picture(io.BytesIO(item["blob"]), x, y, width=w, height=h)
            else:
                bold = item["kind"] == "label"
                box = slide.shapes.add_textbox(x, y, w, h)
                frame = box.text_frame
                frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
                frame.word_wrap = True
                frame.vertical_anchor = MSO_ANCHOR.MIDDLE if item.get("anchor") == "middle" else MSO_ANCHOR.TOP
                for i, line in enumerate(item["text"].split("\n")):
                    paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
                    paragraph.alignment = {"CENTER": PP_ALIGN.CENTER, "RIGHT": PP_ALIGN.RIGHT}.get(
                        next((k for k in ("CENTER", "RIGHT") if k in str(item.get("align", ""))), None), PP_ALIGN.LEFT
                    )
                    run = paragraph.add_run()
                    run.text = line
                    run.font.name = "Arial"
                    run.font.size = Pt(LABEL_PT if bold else item["size"])
                    run.font.bold = bold
        slide.shapes.title  # No title placeholder on the blank layout; kept for clarity
        slide.name = name
    prs.save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("figures", nargs="*", help="names of the figures to render (default: all)")
    parser.add_argument("--deck", type=Path, default=OUTPUT_DECK, help="path of the PowerPoint deck to write")
    args = parser.parse_args()

    FIGURES.mkdir(exist_ok=True)
    figures = all_figures()
    if args.figures:
        unknown = set(args.figures) - set(figures)
        if unknown:
            parser.error(f"unknown figures: {', '.join(sorted(unknown))}; known: {', '.join(figures)}")
        figures = {name: figures[name] for name in args.figures}
    for name, items in figures.items():
        height = render_pdf(items, FIGURES / f"{name}.pdf")
        _, _, right, bottom = bounding_box(items)
        print(f"{name:50} content {right:6.1f} x {bottom:6.1f} mm -> page 183 x {height:.0f} mm")
    render_pptx(figures, args.deck)
    print("wrote", args.deck)
