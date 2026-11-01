"""Render static slides as PNG and .anim slides as MP4 (deterministic frames via window.setT)."""
import sys, pathlib, subprocess, shutil
from playwright.sync_api import sync_playwright

html, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2])
fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
H = int(sys.argv[4]) if len(sys.argv) > 4 else 1350
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": H})
    pg.goto(html.as_uri())
    pg.wait_for_timeout(900)
    for i, el in enumerate(pg.query_selector_all("section.s"), 1):
        n = int(el.get_attribute("id")[1:])
        if "anim" in (el.get_attribute("class") or ""):
            dur = float(el.get_attribute("data-dur"))
            fr = out / f"frames{i}"
            shutil.rmtree(fr, ignore_errors=True); fr.mkdir()
            total = int(dur * fps)
            for k in range(total):
                pg.evaluate(f"setT({n},{k/fps})")
                el.screenshot(path=str(fr / f"{k:04d}.png"))
            el.screenshot(path=str(out / f"slide-{i:02d}.png"))  # last frame as poster
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(fr / "%04d.png"),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(out / f"slide-{i:02d}.mp4")], check=True)
            shutil.rmtree(fr)
        else:
            el.screenshot(path=str(out / f"slide-{i:02d}.png"))
    b.close()
