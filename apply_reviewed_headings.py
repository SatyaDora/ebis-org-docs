#!/usr/bin/env python3
"""
apply_reviewed_headings.py — Apply a specific, hand-reviewed set of H2
heading renames (and a few heading splits) to organization-my-locations.md
and organization-my-organizations.md.

This is NOT a generic heuristic like relabel_duplicate_headings.py. Every
mapping below was worked out by actually reading the content under each
duplicate heading, so it only touches the two files it knows about, and
only the exact heading text listed in CONFIG. Anything that doesn't match
exactly is left untouched and reported.

RENAMES: old heading text -> new heading text (simple 1-for-1 rename).

SPLITS: a heading that bundles two tabs' content under one H2 gets split
into two H2s. "split_before" is the exact line (after stripping leading/
trailing whitespace) where the second tab's content begins; everything
from that line onward moves under the new second heading.

Usage:
    python apply_reviewed_headings.py docs/*.md --dry-run
    python apply_reviewed_headings.py docs/*.md
"""
import re
import sys
import glob
import os

HEADING_RE = re.compile(r"^## (.+)$")

CONFIG = {
    "organization-my-locations.md": {
        "renames": {
            "Create New Location": "Create New Location \u2013 Basic Information",
            "Create New Location 2": "Create New Location \u2013 Additional Information",
            "Create New Location 3": "Create New Location \u2013 Access Information",
            "Create New Location 4": "Create New Location \u2013 Other Information",
            "Create New Location 5": "Create New Location \u2013 Documents",
            "Create New Location 6": "Create New Location \u2013 Floors",
            "Edit Buildings": "Edit Buildings \u2013 Basic Information",
            "Edit Buildings 2": "Edit Buildings \u2013 Additional Information",
            "My Locations \u2013 Buildings \u2013 Floors": "My Locations \u2013 Buildings \u2013 Floors \u2013 Floor Details",
            "My Locations \u2013 Buildings \u2013 Floors 2": "My Locations \u2013 Buildings \u2013 Floors \u2013 Floor Plan & Availability",
        },
        "splits": {},
    },
    "organization-my-organizations.md": {
        "renames": {
            "Organization \u2013 My Organizations 3": "My Organizations \u2013 Edit Organization \u2013 Incorporation Details",
            "Organization \u2013 My Organizations 4": "My Organizations \u2013 Edit Organization \u2013 Documents",
            "Organization \u2013 My Organizations 5": "My Organizations \u2013 Edit Organization \u2013 Trade Listing",
            "Create Organization": "Create Organization \u2013 Basic Information",
            "Create Organization 2": "Create Organization \u2013 Incorporation Details",
            "Create Organization 5": "Create Organization \u2013 SMTP Domains",
        },
        "splits": {
            "Create Organization 3": {
                "first_title": "Create Organization \u2013 License Details",
                "second_title": "Create Organization \u2013 Trade Listing",
                "split_before": "- Trade Listing tab.",
            },
            "Create Organization 4": {
                "first_title": "Create Organization \u2013 Other Details",
                "second_title": "Create Organization \u2013 Documents",
                "split_before": "- Documents tab.",
            },
        },
    },
}


def process_file(path, dry_run=False):
    fname = os.path.basename(path)
    config = CONFIG.get(fname)
    if not config:
        return None  # not one of the files we have instructions for

    renames = config["renames"]
    splits = config["splits"]
    pending = set(renames) | set(splits)

    lines = open(path, encoding="utf-8").read().split("\n")
    out = []
    applied = []

    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEADING_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        text = m.group(1)

        if text in renames:
            new_text = renames[text]
            out.append(f"## {new_text}")
            applied.append((text, new_text, None))
            pending.discard(text)
            i += 1
            continue

        if text in splits:
            spec = splits[text]
            # Collect this heading's body (up to the next heading of any level).
            body_start = i + 1
            j = body_start
            while j < len(lines) and not re.match(r"^#{1,6} ", lines[j]):
                j += 1
            body = lines[body_start:j]

            split_idx = None
            for k, bline in enumerate(body):
                if bline.strip() == spec["split_before"]:
                    split_idx = k
                    break

            if split_idx is None:
                # Split marker not found; don't guess, leave heading as-is
                # but flag it.
                out.append(line)
                applied.append((text, None, "SPLIT MARKER NOT FOUND"))
                i += 1
                continue

            first_body = body[:split_idx]
            second_body = body[split_idx:]

            out.append(f"## {spec['first_title']}")
            out.extend(first_body)
            out.append(f"## {spec['second_title']}")
            out.extend(second_body)

            applied.append((text, f"{spec['first_title']} / {spec['second_title']}", "split"))
            pending.discard(text)
            i = j
            continue

        out.append(line)
        i += 1

    for old, new, note in applied:
        tag = " (split)" if note == "split" else ""
        if note == "SPLIT MARKER NOT FOUND":
            print(f"  {path}: COULD NOT SPLIT \"{old}\" \u2014 split marker text not found, left unchanged")
        else:
            print(f"  {path}: \"{old}\" -> \"{new}\"{tag}")

    for missing in pending:
        print(f"  {path}: NOT FOUND IN FILE \u2014 \"{missing}\" (heading text may have changed since this was written)")

    if applied and not dry_run:
        open(path, "w", encoding="utf-8").write("\n".join(out))

    return len(applied)


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    patterns = [a for a in args if a != "--dry-run"]

    paths = []
    for arg in patterns:
        paths.extend(glob.glob(arg))
    if not paths:
        print("Usage: python apply_reviewed_headings.py docs/*.md [--dry-run]")
        return

    any_matched = False
    for p in paths:
        n = process_file(p, dry_run=dry_run)
        if n is None:
            continue
        any_matched = True
        verb = "would apply" if dry_run else "applied"
        print(f"{p}: {verb} {n} change(s)")

    if not any_matched:
        print("No files matched organization-my-locations.md or organization-my-organizations.md.")


if __name__ == "__main__":
    main()
