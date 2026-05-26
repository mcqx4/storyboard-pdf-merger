"""Smoke tests."""
from storyboard_pdf_merger import LAYOUTS

def test_layouts_present():
    assert "6-panel" in LAYOUTS
    assert "9-panel" in LAYOUTS
    assert "12-panel-widescreen" in LAYOUTS
    assert "8-panel-vertical" in LAYOUTS
    assert "4-panel-detail" in LAYOUTS

def test_layout_geometry():
    l = LAYOUTS["6-panel"]
    assert l.cols * l.rows == 6
    assert l.aspect_w / l.aspect_h > 1.5  # widescreen

if __name__ == "__main__":
    test_layouts_present()
    test_layout_geometry()
    print("OK")
