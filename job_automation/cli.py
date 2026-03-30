import argparse
from pathlib import Path

from .config import load_settings
from .db import init_db, list_jobs, update_scores, upsert_jobs
from .exporter import export_packets
from .scoring import score_jobs
from .sources import CustomAPISource, IndeedSource, LinkedInSource, WellfoundSource


def _build_sources(settings):
    sources = []
    for src in settings.job_sources:
        if src == "linkedin":
            sources.append(LinkedInSource())
        elif src == "indeed":
            sources.append(IndeedSource())
        elif src == "wellfound":
            sources.append(WellfoundSource())
        elif src == "custom_api":
            sources.append(CustomAPISource(settings.custom_api_urls))
    return sources


def cmd_init_db(settings):
    init_db(settings.db_path)
    print(f"Initialized DB at {settings.db_path}")


def cmd_fetch(settings):
    sources = _build_sources(settings)
    all_jobs = []
    for source in sources:
        all_jobs.extend(source.fetch())

    count = upsert_jobs(settings.db_path, all_jobs)
    print(f"Fetched {count} jobs")


def cmd_score(settings):
    jobs = list_jobs(settings.db_path)
    scored = score_jobs(jobs, settings.keywords)
    update_scores(settings.db_path, scored)
    print(f"Scored {len(scored)} jobs")


def cmd_export(settings):
    jobs = list_jobs(settings.db_path)
    output_file = export_packets(jobs, settings.output_dir, settings.resume_path, settings.cover_letter_path)
    print(f"Exported application packets to {output_file}")


def build_parser():
    parser = argparse.ArgumentParser(description="Job automation toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Initialize the SQLite database")
    sub.add_parser("fetch", help="Fetch jobs from sources")
    sub.add_parser("score", help="Score jobs based on keywords")
    sub.add_parser("export", help="Export application packets")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()

    if args.command == "init-db":
        cmd_init_db(settings)
    elif args.command == "fetch":
        cmd_fetch(settings)
    elif args.command == "score":
        cmd_score(settings)
    elif args.command == "export":
        cmd_export(settings)


if __name__ == "__main__":
    main()
