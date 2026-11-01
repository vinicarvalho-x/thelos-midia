import sys, pathlib
from playwright.sync_api import sync_playwright

html, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.goto(html.as_uri())
    pg.wait_for_timeout(800)
    for i, el in enumerate(pg.query_selector_all("section.s"), 1):
        el.screenshot(path=str(out / f"slide-{i:02d}.png"))
    b.close()
