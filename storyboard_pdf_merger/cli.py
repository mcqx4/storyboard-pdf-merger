"""Command-line interface."""
import argparse
import sys
from . import merge, LAYOUTS


def main():
    p = argparse.ArgumentParser(
        description="Merge AI image frames into a printable storyboard PDF.")
    p.add_argument("input_dir", help="Directory containing image frames")
    p.add_argument("--out", "--output", dest="output", default="storyboard.pdf",
                    help="Output PDF path (default: storyboard.pdf)")
    p.add_argument("--layout", default="6-panel", choices=list(LAYOUTS),
                    help="Panel layout (default: 6-panel)")
    p.add_argument("--aspect", default=None,
                    help="Override aspect ratio: 16:9, 2.39:1, 9:16, 4:3")
    p.add_argument("--title", default=None,
                    help="Header title for each page")
    p.add_argument("--annotations", default=None,
                    help="CSV with filename,scene,shot,type,intent,dialogue columns")
    p.add_argument("--dpi", type=int, default=300,
                    help="Output DPI (default: 300)")
    args = p.parse_args()

    try:
        r = merge(
            input_dir=args.input_dir,
            output_path=args.output,
            layout=args.layout,
            aspect=args.aspect,
            title=args.title,
            annotations_csv=args.annotations,
            dpi=args.dpi,
        )
        print(f"✓ Generated {r['pages']} pages from {r['frames']} frames → {r['output']} ({r['size_kb']} KB)")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
