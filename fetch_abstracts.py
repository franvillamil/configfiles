#!/usr/bin/env python3
"""
fetch_abstracts.py — Enrich a .bib file with abstracts from OpenAlex and Crossref.

Both APIs are free and require no key. They ask that you identify yourself
via the "polite pool" by including your email — this gets you better rate
limits, not worse. Set the EMAIL constant below before running.

Strategy per entry:
  1. If the entry already has an abstract field, skip it.
  2. Query OpenAlex by title + first-author surname.
  3. Fall back to Crossref the same way.
  4. Validate any candidate by checking year (±1) and author-surname overlap.
  5. Only write the abstract if the match passes validation.

Output:
  - Writes <input>.enriched.bib next to the input file.
  - Writes <input>.report.csv with one row per entry: key, source, status,
    matched_title, score. Use this to spot-check uncertain matches.
  - Saves progress every 25 entries to <input>.progress.json so you can
    Ctrl-C and resume.

Dependencies:
    pip install bibtexparser requests rapidfuzz

Usage:
    python fetch_abstracts.py REF.bib
    python fetch_abstracts.py REF.bib --limit 50          # try first 50 entries
    python fetch_abstracts.py REF.bib --resume            # continue from progress file
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Optional

import bibtexparser
import requests
from rapidfuzz import fuzz

# ---------------------------------------------------------------------------
# CONFIG — edit before running
# ---------------------------------------------------------------------------
EMAIL = "francisco.villamil@uc3m.es"   # put a real address here for the polite pool

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"

# Be polite. OpenAlex says 10/sec is fine in the polite pool; Crossref says
# ~50/sec. We go slower to avoid bursts and to be a good citizen.
SLEEP_BETWEEN_REQUESTS = 0.4  # seconds

# Match thresholds
TITLE_FUZZ_THRESHOLD = 85     # 0-100, rapidfuzz token_set_ratio
YEAR_TOLERANCE = 1            # accept ±1 year (preprint vs. published, etc.)

REQUEST_TIMEOUT = 20          # seconds per HTTP request
MAX_RETRIES = 3               # per request, with exponential backoff

# ---------------------------------------------------------------------------


def normalize_text(s: str) -> str:
    """Lowercase, strip BibTeX braces/LaTeX, collapse whitespace, fold accents."""
    if not s:
        return ""
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\\[`'\"^~=.](\w)", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def first_author_surname(author_field: str) -> str:
    """
    BibTeX author fields look like:
        'Abadie, Alberto and Diamond, Alexis'
        '{Abou-Chadi}, Tarik and Finnigan, Ryan'
    Return the first author's surname, normalized.
    """
    if not author_field:
        return ""
    first = author_field.split(" and ")[0].strip()
    if "," in first:
        surname = first.split(",", 1)[0]
    else:
        surname = first.split()[-1] if first.split() else first
    return normalize_text(surname)


def clean_year(year_field) -> Optional[int]:
    if year_field is None:
        return None
    m = re.search(r"\d{4}", str(year_field))
    return int(m.group()) if m else None


def reconstruct_openalex_abstract(inverted_index: dict) -> str:
    """OpenAlex returns abstracts as {word: [positions]}. Rebuild the text."""
    if not inverted_index:
        return ""
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    if not positions:
        return ""
    return " ".join(positions[i] for i in sorted(positions))


def strip_jats(s: str) -> str:
    """Crossref abstracts often have JATS XML tags. Strip them."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def http_get(url: str, params: dict, headers: dict) -> Optional[dict]:
    """GET with retries and exponential backoff. Returns parsed JSON or None."""
    backoff = 1.0
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(backoff)
                backoff *= 2
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(backoff)
            backoff *= 2
    return None


# ---------------------------------------------------------------------------
# Validation: did we actually find the right paper?
# ---------------------------------------------------------------------------

def is_good_match(
    candidate_title: str,
    candidate_year: Optional[int],
    candidate_authors: list[str],
    entry_title: str,
    entry_year: Optional[int],
    entry_surname: str,
) -> tuple[bool, float]:
    """
    Return (is_match, score 0-100).
    Require: title fuzz >= threshold AND (year within tolerance OR years unknown)
             AND first-author surname appears in candidate authors.
    """
    if not candidate_title or not entry_title:
        return False, 0.0

    title_score = fuzz.token_set_ratio(
        normalize_text(candidate_title), normalize_text(entry_title)
    )
    if title_score < TITLE_FUZZ_THRESHOLD:
        return False, title_score

    if entry_year is not None and candidate_year is not None:
        if abs(entry_year - candidate_year) > YEAR_TOLERANCE:
            return False, title_score

    if entry_surname and candidate_authors:
        cand_normalized = {normalize_text(a) for a in candidate_authors if a}
        if not any(entry_surname in c or c in entry_surname for c in cand_normalized):
            return False, title_score

    return True, title_score


# ---------------------------------------------------------------------------
# Source: OpenAlex
# ---------------------------------------------------------------------------

def query_openalex(title: str, surname: str, year: Optional[int]) -> Optional[dict]:
    params = {
        "search": title,
        "per-page": 5,
        "mailto": EMAIL,
    }
    headers = {"User-Agent": f"AbstractFetcher/1.0 (mailto:{EMAIL})"}
    data = http_get(OPENALEX_URL, params, headers)
    if not data or "results" not in data:
        return None

    for work in data["results"]:
        cand_title = work.get("title") or work.get("display_name") or ""
        cand_year = work.get("publication_year")
        cand_authors = []
        for a in (work.get("authorships") or []):
            name = (a.get("author") or {}).get("display_name", "")
            if name:
                cand_authors.append(name.split()[-1])
        ok, score = is_good_match(
            cand_title, cand_year, cand_authors,
            title, year, surname,
        )
        if not ok:
            continue
        abstract = reconstruct_openalex_abstract(work.get("abstract_inverted_index") or {})
        if not abstract:
            continue
        return {
            "abstract": abstract,
            "matched_title": cand_title,
            "score": score,
        }
    return None


# ---------------------------------------------------------------------------
# Source: Crossref
# ---------------------------------------------------------------------------

def query_crossref(title: str, surname: str, year: Optional[int]) -> Optional[dict]:
    params = {
        "query.title": title,
        "rows": 5,
        "mailto": EMAIL,
    }
    if surname:
        params["query.author"] = surname
    headers = {"User-Agent": f"AbstractFetcher/1.0 (mailto:{EMAIL})"}
    data = http_get(CROSSREF_URL, params, headers)
    if not data:
        return None
    items = (data.get("message") or {}).get("items") or []

    for work in items:
        titles = work.get("title") or []
        cand_title = titles[0] if titles else ""
        cand_year = None
        issued = work.get("issued") or work.get("published-print") or work.get("published-online")
        if issued and isinstance(issued.get("date-parts"), list) and issued["date-parts"]:
            dp = issued["date-parts"][0]
            if dp and isinstance(dp[0], int):
                cand_year = dp[0]
        cand_authors = [
            a.get("family", "") for a in (work.get("author") or []) if a.get("family")
        ]
        ok, score = is_good_match(
            cand_title, cand_year, cand_authors,
            title, year, surname,
        )
        if not ok:
            continue
        raw_abstract = work.get("abstract") or ""
        abstract = strip_jats(raw_abstract)
        if not abstract:
            continue
        return {
            "abstract": abstract,
            "matched_title": cand_title,
            "score": score,
        }
    return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def fetch_for_entry(entry: dict) -> tuple[str, str, str, float]:
    """
    Return (status, source, matched_title, score).
    status in {'found', 'no_match', 'skipped_has_abstract', 'skipped_no_title'}
    """
    if entry.get("abstract"):
        return "skipped_has_abstract", "", "", 0.0

    raw_title = entry.get("title", "")
    title = re.sub(r"[{}]", "", raw_title).strip()
    if not title:
        return "skipped_no_title", "", "", 0.0

    surname = first_author_surname(entry.get("author", ""))
    year = clean_year(entry.get("year"))

    result = query_openalex(title, surname, year)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    if result:
        entry["abstract"] = result["abstract"]
        return "found", "openalex", result["matched_title"], result["score"]

    result = query_crossref(title, surname, year)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    if result:
        entry["abstract"] = result["abstract"]
        return "found", "crossref", result["matched_title"], result["score"]

    return "no_match", "", "", 0.0


def save_progress(progress_path: Path, done_keys: set, report_rows: list, entries: list):
    abstracts = {e["ID"]: e["abstract"] for e in entries if e.get("ID") and e.get("abstract")}
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({
            "done_keys": sorted(done_keys),
            "report_rows": report_rows,
            "abstracts": abstracts,
        }, f, ensure_ascii=False, indent=2)


def write_outputs(out_path: Path, report_path: Path, bib_db, report_rows: list):
    with open(out_path, "w", encoding="utf-8") as f:
        bibtexparser.dump(bib_db, f)
    with open(report_path, "w", encoding="utf-8", newline="") as f:
        if report_rows:
            writer = csv.DictWriter(f, fieldnames=list(report_rows[0].keys()))
            writer.writeheader()
            writer.writerows(report_rows)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("bibfile", type=Path, help="Input .bib file")
    parser.add_argument("--limit", type=int, default=None, help="Only process first N entries")
    parser.add_argument("--resume", action="store_true", help="Resume from progress file")
    args = parser.parse_args()

    if EMAIL == "your.email@example.com":
        print("WARNING: edit the EMAIL constant at the top of the script before running.", file=sys.stderr)
        print("OpenAlex and Crossref ask for an email so they can contact you if anything", file=sys.stderr)
        print("goes wrong. You get faster, more reliable service in their 'polite pool'.", file=sys.stderr)
        print("", file=sys.stderr)

    bib_path: Path = args.bibfile
    out_path = bib_path.with_suffix(".enriched.bib")
    report_path = bib_path.with_suffix(".report.csv")
    progress_path = bib_path.with_suffix(".progress.json")

    print(f"Reading {bib_path}...")
    with open(bib_path, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f)
    entries = bib_db.entries
    print(f"Loaded {len(entries)} entries.")

    if args.limit:
        entries = entries[: args.limit]
        bib_db.entries = entries
        print(f"Limiting to first {len(entries)} entries.")

    done_keys: set[str] = set()
    report_rows: list[dict] = []
    if args.resume and progress_path.exists():
        with open(progress_path, encoding="utf-8") as f:
            saved = json.load(f)
        done_keys = set(saved.get("done_keys", []))
        report_rows = saved.get("report_rows", [])
        saved_abstracts = saved.get("abstracts", {})
        for e in entries:
            if e.get("ID") in saved_abstracts:
                e["abstract"] = saved_abstracts[e["ID"]]
        print(f"Resuming: {len(done_keys)} entries already processed.")

    counts = {"found": 0, "no_match": 0, "skipped_has_abstract": 0, "skipped_no_title": 0}
    for row in report_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    try:
        for i, entry in enumerate(entries, 1):
            key = entry.get("ID", f"<entry {i}>")
            if key in done_keys:
                continue

            try:
                status, source, matched, score = fetch_for_entry(entry)
            except Exception as e:
                status, source, matched, score = "error", str(type(e).__name__), str(e)[:200], 0.0

            counts[status] = counts.get(status, 0) + 1
            done_keys.add(key)
            report_rows.append({
                "key": key,
                "status": status,
                "source": source,
                "year": entry.get("year", ""),
                "title": re.sub(r"[{}]", "", entry.get("title", ""))[:120],
                "matched_title": matched[:120] if matched else "",
                "score": f"{score:.0f}" if score else "",
            })

            if i % 10 == 0 or i == len(entries):
                summary = " ".join(f"{k}={v}" for k, v in counts.items() if v)
                print(f"  [{i}/{len(entries)}] {key:40s} -> {status:10s}  ({summary})")

            if i % 25 == 0:
                save_progress(progress_path, done_keys, report_rows, entries)

    except KeyboardInterrupt:
        print("\nInterrupted. Saving progress...")
        save_progress(progress_path, done_keys, report_rows, entries)
        write_outputs(out_path, report_path, bib_db, report_rows)
        sys.exit(1)

    save_progress(progress_path, done_keys, report_rows, entries)
    write_outputs(out_path, report_path, bib_db, report_rows)

    print()
    print("=" * 60)
    print("Done.")
    for k, v in counts.items():
        print(f"  {k:25s} {v}")
    print(f"\nEnriched bib:  {out_path}")
    print(f"Match report:  {report_path}")
    print(f"Progress file: {progress_path}  (delete when satisfied)")


if __name__ == "__main__":
    main()
