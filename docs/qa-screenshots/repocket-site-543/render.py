"""Render index, support and press in English at 1440 and 375 with reduced motion.

Usage: python3 docs/qa-screenshots/repocket-site-543/render.py <base-url> <out-dir>
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
WIDTHS = [1440, 375]
written = []


def shot(page, name, **kw):
    p = out / name
    page.screenshot(path=str(p), **kw)
    written.append(p.name)


def el_shot(page, selector, name):
    loc = page.locator(selector).first
    loc.scroll_into_view_if_needed()
    # The sticky nav would sit over the top of an element shot; hide it without moving layout.
    page.add_style_tag(content="nav,.site-nav{visibility:hidden!important}")
    page.mouse.move(0, 0)
    page.wait_for_timeout(150)
    p = out / name
    loc.screenshot(path=str(p))
    page.evaluate("document.querySelectorAll('style').forEach(s => { if (s.textContent.startsWith('nav,.site-nav{visibility:hidden')) s.remove() })")
    written.append(p.name)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for w in WIDTHS:
        # A German browser language with rp-lang=de pre-set must still render English.
        ctx = browser.new_context(viewport={"width": w, "height": 900}, reduced_motion="reduce",
                                  locale="de-DE", device_scale_factor=1)
        ctx.add_init_script("try{localStorage.setItem('rp-lang','de')}catch(e){}")
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        # index
        page.goto(f"{base}/index.html", wait_until="networkidle")
        lang = page.evaluate("document.documentElement.getAttribute('data-lang')")
        assert lang == "en", f"index renders {lang} at {w}"
        page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
        page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
        page.wait_for_timeout(600)
        shot(page, f"index-full-en-{w}.png", full_page=True)
        el_shot(page, "#how", f"index-how-en-{w}.png")
        el_shot(page, "#price", f"index-price-en-{w}.png")
        el_shot(page, "#faq", f"index-faq-en-{w}.png")
        for i, beat in enumerate(["log", "home", "widget", "square"], 1):
            page.locator(f".beat[data-scr={beat}]").scroll_into_view_if_needed()
            page.evaluate("window.scrollBy(0, 0)")
            page.wait_for_timeout(250)
            shot(page, f"index-story-beat{i}-en-{w}.png")

        # support
        page.goto(f"{base}/support.html", wait_until="networkidle")
        assert page.evaluate("document.documentElement.getAttribute('data-lang')") == "en"
        shot(page, f"support-full-en-{w}.png", full_page=True)

        # press
        page.goto(f"{base}/press.html", wait_until="networkidle")
        page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
        page.wait_for_timeout(600)
        shot(page, f"press-full-en-{w}.png", full_page=True)
        el_shot(page, ".steps", f"press-steps-en-{w}.png")
        el_shot(page, "#overview", f"press-overview-en-{w}.png")
        for tab in ["frames", "screens"]:
            page.click(f"[data-tab={tab}]")
            page.wait_for_timeout(500)
            el_shot(page, "#screenshots", f"press-screenshots-{tab}-en-{w}.png")

        if errors:
            print(f"console errors at {w}: {errors}")
        ctx.close()
    browser.close()

print("\n".join(written))
