#!/usr/bin/env python3
"""
job_tracker.py
--------------
Utilities for reading, writing, and reporting on the job-application tracker
stored in data/job_history.csv.

Usage:
    List all jobs:          python scripts/job_tracker.py list
    Show summary stats:     python scripts/job_tracker.py summary
    Update job status:      python scripts/job_tracker.py update --id 3 --status interview_scheduled
    Export to JSON:         python scripts/job_tracker.py export --output output/jobs.json
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
JOB_HISTORY_PATH = DATA_DIR / "job_history.csv"

CSV_FIELDS = [
    "id",
    "date_applied",
    "company",
    "job_title",
    "role_type",
    "seniority",
    "status",
    "notes",
    "follow_up_date",
    "outcome",
]

VALID_STATUSES = [
    "applied",
    "interview_scheduled",
    "interviewed",
    "offer_received",
    "accepted",
    "rejected",
    "withdrawn",
]


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def _ensure_csv(path: Path) -> None:
    """Create the CSV with headers if it does not exist."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def read_csv(path: Path = JOB_HISTORY_PATH) -> list:
    """Return all rows from the job history CSV as a list of dicts."""
    _ensure_csv(path)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list, path: Path = JOB_HISTORY_PATH) -> None:
    """Overwrite the CSV with the provided rows."""
    _ensure_csv(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _next_id(rows: list) -> int:
    """Return the next auto-increment ID."""
    if not rows:
        return 1
    return max(int(r.get("id", 0)) for r in rows) + 1


def append_to_csv(job: dict, path: Path = JOB_HISTORY_PATH) -> int:
    """
    Append a new job entry to the CSV tracker.

    Returns the new row ID.
    """
    _ensure_csv(path)
    rows = read_csv(path)
    new_id = _next_id(rows)
    new_row = {
        "id": new_id,
        "date_applied": datetime.now().strftime("%Y-%m-%d"),
        "company": job.get("company", ""),
        "job_title": job.get("job_title", ""),
        "role_type": job.get("role_type", ""),
        "seniority": job.get("seniority", ""),
        "status": job.get("status", "applied"),
        "notes": job.get("notes", ""),
        "follow_up_date": job.get("follow_up_date", ""),
        "outcome": job.get("outcome", ""),
    }
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(new_row)
    print(f"[Tracker] Added entry #{new_id}: {new_row['company']} — {new_row['job_title']}")
    return new_id


def update_status(row_id: int, status: str, path: Path = JOB_HISTORY_PATH) -> bool:
    """Update the status (and optionally outcome) of a job entry by ID."""
    if status not in VALID_STATUSES:
        print(f"[ERROR] Invalid status '{status}'. Choose from: {', '.join(VALID_STATUSES)}")
        return False
    rows = read_csv(path)
    updated = False
    for row in rows:
        if int(row.get("id", -1)) == row_id:
            row["status"] = status
            if status in ("accepted", "rejected", "withdrawn"):
                row["outcome"] = status
            updated = True
            break
    if not updated:
        print(f"[ERROR] No entry found with id={row_id}")
        return False
    write_csv(rows, path)
    print(f"[Tracker] Updated entry #{row_id} status → {status}")
    return True


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def list_jobs(rows: list) -> None:
    """Print all jobs in a human-readable table."""
    if not rows:
        print("No applications tracked yet.")
        return
    col_widths = [4, 12, 25, 30, 12, 8, 22]
    headers = ["ID", "Date", "Company", "Job Title", "Role Type", "Level", "Status"]
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print("\n" + header_line)
    print("-" * len(header_line))
    for row in rows:
        line = "  ".join(
            str(row.get(k, "")).ljust(w)
            for k, w in zip(
                ["id", "date_applied", "company", "job_title", "role_type", "seniority", "status"],
                col_widths,
            )
        )
        print(line)
    print()


def summary(rows: list) -> None:
    """Print summary statistics."""
    total = len(rows)
    if total == 0:
        print("No applications tracked yet.")
        return
    status_counts: dict = {}
    role_counts: dict = {}
    for row in rows:
        s = row.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        r = row.get("role_type", "unknown")
        role_counts[r] = role_counts.get(r, 0) + 1

    print(f"\n=== Job Application Summary ===")
    print(f"Total applications: {total}\n")
    print("By status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status:<25} {count}")
    print("\nBy role type:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role:<25} {count}")
    interview_rate = sum(
        1 for r in rows if r.get("status") in ("interview_scheduled", "interviewed", "offer_received", "accepted")
    )
    print(f"\nInterview rate: {interview_rate}/{total} ({round(100*interview_rate/total)}%)\n")


def export_to_json(rows: list, output_path: Path) -> None:
    """Export job history to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"[Tracker] Exported {len(rows)} entries to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Job application tracker.")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all tracked applications")
    sub.add_parser("summary", help="Show summary statistics")

    update_p = sub.add_parser("update", help="Update a job application status")
    update_p.add_argument("--id", type=int, required=True, help="Row ID to update")
    update_p.add_argument("--status", required=True, choices=VALID_STATUSES)

    export_p = sub.add_parser("export", help="Export job history to JSON")
    export_p.add_argument("--output", default="output/jobs.json", help="Output JSON path")

    add_p = sub.add_parser("add", help="Manually add a job entry")
    add_p.add_argument("--company", required=True)
    add_p.add_argument("--job-title", dest="job_title", required=True)
    add_p.add_argument("--role-type", dest="role_type", default="finance")
    add_p.add_argument("--seniority", default="mid")
    add_p.add_argument("--notes", default="")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "list":
        rows = read_csv()
        list_jobs(rows)

    elif args.command == "summary":
        rows = read_csv()
        summary(rows)

    elif args.command == "update":
        update_status(args.id, args.status)

    elif args.command == "export":
        rows = read_csv()
        export_to_json(rows, Path(args.output))

    elif args.command == "add":
        job = {
            "company": args.company,
            "job_title": args.job_title,
            "role_type": args.role_type,
            "seniority": args.seniority,
            "notes": args.notes,
        }
        append_to_csv(job)

    else:
        rows = read_csv()
        list_jobs(rows)
        summary(rows)


if __name__ == "__main__":
    main()
