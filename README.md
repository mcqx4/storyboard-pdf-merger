# storyboard-pdf-merger

> Merge AI-generated image frames into a printable storyboard PDF. Works with any image source — Midjourney, DALL-E, Stable Diffusion, STORYLINER, or hand-scanned drawings.

[![PyPI](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What it does

```bash
$ storyboard-pdf-merger ./frames --layout 6-panel --out storyboard.pdf
✓ Found 18 frames in ./frames
✓ Layout: 6 panels per page, 16:9 ratio
✓ Generated 3 pages → storyboard.pdf (412 KB)
```

Takes a folder of PNG/JPG frames, lays them out as a proper storyboard with annotation rows, exports a single multi-page PDF ready for print or client review.

## Why this exists

Every AI image tool produces image files. Nobody has a clean utility that turns those files into a proper printable storyboard PDF with:

- Configurable panel layouts (6, 9, 12 per page)
- Configurable aspect ratios (16:9, 2.39:1, 9:16, 4:3)
- Annotation rows beneath each panel (for scene #, shot type, dialogue)
- Page numbers, header, footer
- Print-ready resolution

This utility fills that gap.

## Installation

```bash
pip install storyboard-pdf-merger
```

Or from source:

```bash
git clone https://github.com/mcqx4/storyboard-pdf-merger
cd storyboard-pdf-merger
pip install -e .
```

## Usage

```bash
# Basic — 6 panels per page, 16:9
storyboard-pdf-merger ./frames --out board.pdf

# Music video / vertical video
storyboard-pdf-merger ./frames --aspect 9:16 --layout 8-panel-vertical --out board.pdf

# Feature film / anamorphic
storyboard-pdf-merger ./frames --aspect 2.39:1 --layout 12-panel-widescreen --out board.pdf

# Detail sheet (4 large frames per page + side notes)
storyboard-pdf-merger ./frames --layout 4-panel-detail --out board.pdf

# With annotation labels from a CSV
storyboard-pdf-merger ./frames --annotations notes.csv --out board.pdf
```

Annotation CSV format:

```csv
filename,scene,shot,type,intent,dialogue
01.png,1,1A,WS,Establishing,
02.png,1,1B,MS,Push to her decision,"I'm leaving."
03.png,2,2A,CU,Reveal,
...
```

## Library use

```python
from storyboard_pdf_merger import merge

merge(
    input_dir="./frames",
    output_path="storyboard.pdf",
    layout="6-panel",
    aspect="16:9",
    title="NIGHTSHIFT — Storyboard V1",
    annotations_csv="./notes.csv",  # optional
)
```

## Supported layouts

| Layout | Frames/page | Aspect | Best for |
|--------|------------|--------|----------|
| `6-panel` | 6 | 16:9 | Universal default |
| `9-panel` | 9 | 16:9 | Dense dialogue scenes |
| `12-panel-widescreen` | 12 | 2.39:1 | Anamorphic features |
| `4-panel-detail` | 4 | 16:9 | Keyframe sheets with notes |
| `8-panel-vertical` | 8 | 9:16 | Music videos, vertical content |

## Pipeline use

This utility was extracted from [STORYLINER's](https://www.storyliner.online) export pipeline. Storyliner is an AI storyboard generator that turns scripts into production-ready boards in 2 minutes — but the PDF assembly logic is generally useful for anyone working with AI-generated frames from any source.

If you're generating frames with Midjourney or DALL-E and want them as a proper storyboard PDF, this is the tool you need.

If you want the whole script-to-PDF pipeline (with character consistency across frames), [Storyliner](https://www.storyliner.online) does that end-to-end.

## Print quality

Default DPI: 300. Output PDF works at A4 and US Letter without modification. For A3 printing, pass `--dpi 600`.

## Dependencies

- `Pillow` for image processing
- `PyMuPDF` for PDF generation

Both are pip-installable and stable across Python 3.8–3.12.

## Contributing

PRs welcome. Standard hygiene:

- One feature per PR
- Tests for new layouts
- Keep dependencies minimal

## License

MIT — see [LICENSE](LICENSE).
