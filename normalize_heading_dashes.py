#!/usr/bin/env python3
"""
normalize_heading_dashes.py — Fix dash style on a specific, known set of
H2 headings in organization-my-locations.md.

These headings already have the right wording (someone renamed them in
an earlier pass) but use a plain hyphen with no surrounding spaces
("Create New Location-Basic Information") instead of the en dash with
spaces used everywhere else in the doc set ("Create New Location –
Basic Information"). This script only touches the exact strings listed
below — it does not do a general hyphen-to-en-dash regex sweep, so it
can't accidentally mangle a legitimate hyphen elsewhere (e.g. "Save/
Update" style text or a genuinely hyphenated word).

Usage:
    python normalize_heading_dashes.py docs/organization-my-locations.md --dry-run
    python normalize_heading_dashes.py docs/organization-my-locations.md
"""
import sys
import glob
import os

TARGET_FILE = "organization-my-locations.md"

# Exact old heading text (as currently in the file) -> corrected text.
FIXES = {
    "## Create New Location-Basic Information": "## Create New Location \u2013 Basic Information",
    "## Create New Location-Additional Information": "## Create New Location \u2013 Additional Information",
    "## Create New Location-Access Information": "## Create New Location \u2013 Access Information",
    "## Create New Location-Other Information": "## Create New Location \u2013 Other Information",
    "## Create New Location-Documents": "## Create New Location \u2013 Documents",
    "## Create New Location-Floors": "## Create New Location \u2013 Floors",
    "## Edit Buildings-Basic Information": "## Edit Buildings \u2013 Basic Information",
    "## Edit Buildings-Additional Information": "## Edit Buildings \u2013 Additional Information",
}


def process_file(path, dry_run=False):
    if os.path.basename(path) != TARGET_FILE:
        return None

    lines = open(path, encoding="utf-8").read().split("\n")
    pending = set(FIXES)
    changed = 0

    for i, line in enumerate(lines):
        if line in FIXES:
            new_line = FIXES[line]
            print(f"  {path}: \"{line[3:]}\" -> \"{new_line[3:]}\"")
            lines[i] = new_line
            pending.discard(line)
            changed += 1

    for missing in pending:
        print(f"  {path}: NOT FOUND \u2014 \"{missing[3:]}\" (already fixed, or wording differs)")

    if changed and not dry_run:
        open(path, "w", encoding="utf-8").write("\n".join(lines))

    return changed


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    patterns = [a for a in args if a != "--dry-run"]

    paths = []
    for arg in patterns:
        paths.extend(glob.glob(arg))
    if not paths:
        print("Usage: python normalize_heading_dashes.py docs/organization-my-locations.md [--dry-run]")
        return

    any_matched = False
    for p in paths:
        n = process_file(p, dry_run=dry_run)
        if n is None:
            continue
        any_matched = True
        verb = "would fix" if dry_run else "fixed"
        print(f"{p}: {verb} {n} heading(s)")

    if not any_matched:
        print(f"No file named {TARGET_FILE} was in the given paths.")


if __name__ == "__main__":
    main()
