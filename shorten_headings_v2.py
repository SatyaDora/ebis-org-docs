#!/usr/bin/env python3
"""
shorten_headings_v2.py — Clean up split docs pages so the Material
"Table of contents" (right rail) reads well.

Handles two cases:
  1. An H2 that exactly repeats the page's H1 (e.g. H1 "Organization -
     My Locations" followed immediately by H2 "Organization - My
     Locations") is REMOVED entirely — its content folds up under the H1,
     removing the redundant top TOC entry.
  2. Remaining H2s that repeat the H1 as a prefix, e.g.
     "Organization - My Locations - Create New Location (continued 6)"
     -> "Create New Location 6"
     The "(continued)" / "(continued N)" suffix is dropped; the first
     occurrence of a heading keeps no number, later ones get " 2", " 3", ...

Usage:
    python shorten_headings_v2.py docs/*.md
Add --dry-run to preview without writing.
"""
import re, sys, glob

CONTINUED_RE = re.compile(r"\s*\(continued(?:\s+(\d+))?\)\s*$", re.IGNORECASE)

def norm(s):
    return re.sub(r"[\u2013\u2014-]", "-", s).strip().lower()

def strip_prefix(text, h1_variants):
    stripped = text
    for variant in sorted(h1_variants, key=len, reverse=True):
        for sep in (" - ", " \u2013 ", " \u2014 ", "-", "\u2013"):
            lead = variant + sep
            if stripped.lower().startswith(lead.lower()):
                stripped = stripped[len(lead):].strip()
                return stripped
    return stripped

def process(path, dry_run=False):
    lines = open(path, encoding="utf-8").read().split("\n")

    h1 = None
    for l in lines:
        m = re.match(r"^# (.+)$", l)
        if m:
            h1 = m.group(1).strip()
            break
    if not h1:
        return 0, 0

    h1_variants = {h1, re.sub(r"[\u2013\u2014]", "-", h1)}

    out = []
    removed = 0
    changed = 0
    seen_base = {}
    i = 0
    n = len(lines)
    while i < n:
        l = lines[i]
        m = re.match(r"^(## )(.+)$", l)
        if not m:
            out.append(l)
            i += 1
            continue

        prefix, text = m.groups()
        base_no_suffix = CONTINUED_RE.sub("", text).strip()

        if norm(base_no_suffix) in {norm(v) for v in h1_variants}:
            removed += 1
            i += 1
            continue

        stripped = strip_prefix(base_no_suffix, h1_variants) or base_no_suffix
        key = stripped.lower()
        seen_base[key] = seen_base.get(key, 0) + 1
        cnt = seen_base[key]
        new_text = stripped if cnt == 1 else f"{stripped} {cnt}"

        if new_text != text:
            changed += 1
        out.append(f"{prefix}{new_text}")
        i += 1

    if (changed or removed) and not dry_run:
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return changed, removed

def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    patterns = [a for a in args if a != "--dry-run"]
    paths = []
    for p in patterns:
        paths.extend(glob.glob(p))
    if not paths:
        print("Usage: python shorten_headings_v2.py docs/*.md [--dry-run]")
        return
    for p in paths:
        changed, removed = process(p, dry_run)
        print(f"{p}: shortened {changed}, removed {removed} redundant H2(s)")

if __name__ == "__main__":
    main()
