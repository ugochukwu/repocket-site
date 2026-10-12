"""Prove no old vocabulary remains in the English-visible text of the site pages.

Usage: python3 -I docs/qa-screenshots/repocket-site-543/check-vocab.py <repo-root> [<git-rev-for-german-compare>]

English-visible = text nodes, alt/title/aria-label/placeholder attributes, <title>, and the
description/og/twitter meta content, everywhere except inside an element marked data-l="de".
Also checks: no em or en dash in that text, and (with a rev) that every data-l="de" subtree is
byte-identical to the one at that rev.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

PAGES = ["index.html", "support.html", "press.html"]
OLD = re.compile(r"\b(owe|owes|owed|owing|borrow|borrows|borrowed|borrowing|lend|lends|lent|debt|debts|debtor|creditor)\b", re.I)
DASH = re.compile("[\u2013\u2014]")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ATTRS = ("alt", "title", "aria-label", "placeholder")
META_NAMES = {"description", "og:title", "og:description", "twitter:title", "twitter:description"}


class English(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, is_de)
        self.items = []  # (line, kind, text)
        self.skip_raw = 0

    def de_now(self):
        return any(d for _, d in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        is_de = a.get("data-l") == "de"
        de = self.de_now() or is_de
        line = self.getpos()[0]
        if not de:
            for k in ATTRS:
                if a.get(k):
                    self.items.append((line, f"{tag}@{k}", a[k]))
            if tag == "meta" and (a.get("name") in META_NAMES or a.get("property") in META_NAMES):
                self.items.append((line, f"meta:{a.get('name') or a.get('property')}", a.get("content", "")))
        if tag in ("script", "style"):
            self.skip_raw += 1
        if tag not in VOID:
            self.stack.append((tag, is_de))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip_raw = max(0, self.skip_raw - 1)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.skip_raw or self.de_now() or not data.strip():
            return
        tag = self.stack[-1][0] if self.stack else "?"
        self.items.append((self.getpos()[0], f"text<{tag}>", data.strip()))


class German(HTMLParser):
    """Collects the raw source of every data-l="de" subtree, in order."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src_lines = src.splitlines(keepends=True)
        self.offsets = [0]
        for ln in self.src_lines:
            self.offsets.append(self.offsets[-1] + len(ln))
        self.src = src
        self.stack = []
        self.open_de = []  # (depth, start offset)
        self.chunks = []

    def off(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.off()
        is_de = dict(attrs).get("data-l") == "de"
        if tag in VOID:
            if is_de:
                end = self.src.index(">", start) + 1
                self.chunks.append(self.src[start:end])
            return
        self.stack.append(tag)
        if is_de:
            self.open_de.append((len(self.stack), start))

    def handle_endtag(self, tag):
        pos = self.off()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                depth = i + 1
                while self.open_de and self.open_de[-1][0] >= depth:
                    d, start = self.open_de.pop()
                    end = self.src.index(">", pos) + 1
                    if d == depth:
                        self.chunks.append(self.src[start:end])
                del self.stack[i:]
                break


def german_chunks(src):
    g = German(src)
    g.feed(src)
    return g.chunks


def main():
    root = Path(sys.argv[1])
    rev = sys.argv[2] if len(sys.argv) > 2 else None
    bad = 0
    for page in PAGES:
        src = (root / page).read_text(encoding="utf-8")
        p = English()
        p.feed(src)
        hits = [(ln, k, t) for ln, k, t in p.items if OLD.search(t)]
        dashes = [(ln, k, t) for ln, k, t in p.items if DASH.search(t)]
        print(f"{page}: {len(p.items)} English-visible strings checked, "
              f"{len(hits)} with old words, {len(dashes)} with an em or en dash")
        for ln, k, t in hits + dashes:
            print(f"  line {ln} {k}: {t[:160]}")
        bad += len(hits) + len(dashes)
        if rev:
            old_src = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{page}"],
                                     capture_output=True, text=True, check=True).stdout
            a, b = german_chunks(old_src), german_chunks(src)
            same = a == b
            print(f"  German: {len(b)} data-l=\"de\" subtrees, identical to {rev}: {same}")
            if not same:
                bad += 1
    sys.exit(1 if bad else 0)


main()
