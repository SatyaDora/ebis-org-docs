#!/usr/bin/env python3
"""
eliminate_h1_h2_duplicate.py — Remove the first H2 in a page when it just
repeats the H1 (page title), which happens because the pptx source has a
section-divider slide (title only) immediately followed by a content
slide that reuses the same title text.

Example, before:
    # Organization - Organizational Relationship

    ## Organization - Organizational Relationship

    - This section is used to create and manage relationships...

After:
    # Organization - Organizational Relationship

    - This section is used to create and manage relationships...

Matching is punctuation-tolerant: "Organization - Organizational
Relationship" (en dash) and "Organization-Organizational Relationship"
(no-space hyphen) are treated as the same title, since the pptx often
has inconsistent dash styles between the divider slide and the content
slide.

Only the FIRST H2 in the file is checked (that's where this pattern
occurs). Later H2s are left alone even if their text happens to repeat
elsewhere.

Usage:
    python eliminate_h1_h2_duplicate.py docs/*.md --dry-run
    python eliminate_h1_h2_duplicate.py docs/*.md
"""
import re
import sys
import glob

H1_RE = re.compile(r"^# (.+)$")
H2_RE = re.compile(r"^## (.+)$")
DASH_RE = re.compile(r"\s*[\u2013\u2014-]\s*")


def normalize(text):
    """Collapse any dash style/spacing to a single canonical form."""
    text = DASH_RE.sub(" - ", text.strip())
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def process_file(path, dry_run=False):
    lines = open(path, encoding="utf-8").read().split("\n")

    h1_idx = None
    h1_text = None
    for i, line in enumerate(lines):
        m = H1_RE.match(line)
        if m:
            h1_idx = i
            h1_text = m.group(1)
            break
    if h1_text is None:
        return 0

    # Find the first H2 anywhere after the H1.
    h2_idx = None
    h2_text = None
    for i in range(h1_idx + 1, len(lines)):
        m = H2_RE.match(lines[i])
        if m:
            h2_idx = i
            h2_text = m.group(1)
            break
    if h2_text is None:
        return 0

    if normalize(h1_text) != normalize(h2_text):
        return 0

    if dry_run:
        print(f"  {path}: removing duplicate H2 \"{h2_text}\" (matches H1 \"{h1_text}\")")
        return 1

    # Remove the H2 heading line itself, and collapse the resulting blank
    # line gap (keep at most one blank line where it was).
    del lines[h2_idx]
    while h2_idx < len(lines) and h2_idx > 0 and lines[h2_idx] == "" and lines[h2_idx - 1] == "":
        del lines[h2_idx]

    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"  {path}: removed duplicate H2 \"{h2_text}\" (matched H1 \"{h1_text}\")")
    return 1


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    patterns = [a for a in args if a != "--dry-run"]

    paths = []
    for arg in patterns:
        paths.extend(glob.glob(arg))
    if not paths:
        print("Usage: python eliminate_h1_h2_duplicate.py docs/*.md [--dry-run]")
        return

    total = 0
    for p in paths:
        total += process_file(p, dry_run=dry_run)

    verb = "would fix" if dry_run else "fixed"
    print(f"\n{verb} {total} file(s) with a duplicate H1/H2 title.")


if __name__ == "__main__":
    main()
