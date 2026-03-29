#!/usr/bin/env python3
"""
generate_application.py
-----------------------
Automates generation of tailored CVs, cover letters, outreach emails,
and job-tracking entries for multiple job types.

Usage:
    Interactive:   python scripts/generate_application.py
    Single job:    python scripts/generate_application.py --company "Deloitte" \
                       --job-title "Audit Senior" --role-type audit \
                       --seniority senior --job-description "Conduct risk-based audits..."
    Bulk:          python scripts/generate_application.py --bulk examples/input/bulk_jobs.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
DATA_DIR = REPO_ROOT / "data"
USER_PROFILE_PATH = DATA_DIR / "user_profile.json"
JOB_HISTORY_PATH = DATA_DIR / "job_history.csv"

VALID_ROLE_TYPES = ["finance", "audit", "part_time", "graduate", "full_time"]
VALID_SENIORITY = ["entry", "mid", "senior", "manager", "director"]


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

def load_template(template_name: str) -> str:
    """Load a Markdown template from the templates directory."""
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def render_template(template: str, context: dict) -> str:
    """Replace {{key}} placeholders with values from *context*."""
    def replacer(match):
        key = match.group(1).strip()
        return str(context.get(key, match.group(0)))  # keep placeholder if missing

    return re.sub(r"\{\{(.*?)\}\}", replacer, template)


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def load_user_profile() -> dict:
    """Load user profile data from data/user_profile.json."""
    if not USER_PROFILE_PATH.exists():
        print(f"[ERROR] user_profile.json not found at {USER_PROFILE_PATH}")
        sys.exit(1)
    with open(USER_PROFILE_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_context(profile: dict, job: dict) -> dict:
    """Merge user profile and job-specific data into a flat template context."""
    role_type = job.get("role_type", "finance").lower()
    company = job.get("company", "the company")
    job_title = job.get("job_title", "the role")
    seniority = job.get("seniority", "mid")
    job_description = job.get("job_description", "")
    recipient_name = job.get("recipient_name", "Hiring Manager")
    company_address = job.get("company_address", "")

    # Pick role-specific summary
    role_summaries = profile.get("role_summaries", {})
    profile_summary = role_summaries.get(role_type, profile.get("profile_summary", ""))

    # Build flat skills string (ATS version)
    skills = profile.get("key_skills", [])
    key_skills_flat = " | ".join(skills)

    # Build bulleted skills (NZ style)
    key_skills = "\n".join(f"- {s}" for s in skills)

    # Pick ATS keywords for the role
    ats_kws = profile.get("ats_keywords", {}).get(role_type, [])
    ats_keywords = ", ".join(ats_kws)

    # Work experience (up to 2 positions)
    exp = profile.get("work_experience", [])
    exp1 = exp[0] if len(exp) > 0 else {}
    exp2 = exp[1] if len(exp) > 1 else {}

    achievements_1 = "\n".join(f"- {a}" for a in exp1.get("achievements", []))
    achievements_2 = "\n".join(f"- {a}" for a in exp2.get("achievements", []))

    exp1_achs = exp1.get("achievements", ["", "", ""])
    exp2_achs = exp2.get("achievements", ["", "", ""])

    # Education
    edu = profile.get("education", {})

    # Certifications
    certs = profile.get("certifications", [])
    certifications = "\n".join(f"- {c}" for c in certs)
    certifications_flat = " | ".join(certs)

    # Cover letter paragraphs
    opening_paragraph = (
        f"I am writing to express my strong interest in the {job_title} position at "
        f"{company}. With my background in {role_type.replace('_', ' ')} and a "
        f"commitment to delivering high-quality results, I am confident I would be a "
        f"valuable addition to your team."
    )
    company_motivation = (
        f"{company}'s reputation for excellence and its commitment to professional "
        f"development make it an ideal place to advance my career. I am particularly "
        f"drawn to this {job_title} role given the opportunity to contribute to "
        f"meaningful work in {role_type.replace('_', ' ')}."
    )
    value_proposition = (
        f"My {seniority}-level experience in {role_type.replace('_', ' ')} has equipped "
        f"me with the technical skills and professional judgement needed to excel in this "
        f"role. I bring strong analytical skills, attention to detail, and the ability to "
        f"communicate complex information clearly to stakeholders at all levels."
    )
    closing_paragraph = (
        "I am enthusiastic about the opportunity to contribute to your team and am "
        "available for an interview at your convenience."
    )

    # Outreach email parts
    email_subject = f"Expression of Interest — {job_title} | {profile['full_name']}"
    opening_line = (
        f"I hope this message finds you well. My name is {profile['full_name']} "
        f"and I am reaching out regarding potential opportunities for a {job_title} "
        f"role at {company}."
    )
    body_paragraph = (
        f"I have {seniority}-level experience in {role_type.replace('_', ' ')} and "
        f"am particularly interested in {company} because of its strong industry "
        f"presence. I believe my background aligns well with the kind of talent you "
        f"value in your team."
    )
    call_to_action = (
        f"I would love the opportunity to connect for a brief conversation. "
        f"Please find my CV attached, and feel free to reach out at "
        f"{profile.get('email', '')} or {profile.get('phone', '')}."
    )

    return {
        # Personal details
        "full_name": profile.get("full_name", ""),
        "location": profile.get("location", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "linkedin": profile.get("linkedin", ""),
        # Profile
        "profile_summary": profile_summary,
        # Skills
        "key_skills": key_skills,
        "key_skills_flat": key_skills_flat,
        "ats_keywords": ats_keywords,
        # Experience – position 1
        "job_title_1": exp1.get("job_title", ""),
        "company_1": exp1.get("company", ""),
        "start_date_1": exp1.get("start_date", ""),
        "end_date_1": exp1.get("end_date", ""),
        "job_description_1": exp1.get("job_description", ""),
        "achievements_1": achievements_1,
        "achievement_1a": exp1_achs[0] if len(exp1_achs) > 0 else "",
        "achievement_1b": exp1_achs[1] if len(exp1_achs) > 1 else "",
        "achievement_1c": exp1_achs[2] if len(exp1_achs) > 2 else "",
        # Experience – position 2
        "job_title_2": exp2.get("job_title", ""),
        "company_2": exp2.get("company", ""),
        "start_date_2": exp2.get("start_date", ""),
        "end_date_2": exp2.get("end_date", ""),
        "job_description_2": exp2.get("job_description", ""),
        "achievements_2": achievements_2,
        "achievement_2a": exp2_achs[0] if len(exp2_achs) > 0 else "",
        "achievement_2b": exp2_achs[1] if len(exp2_achs) > 1 else "",
        "achievement_2c": exp2_achs[2] if len(exp2_achs) > 2 else "",
        # Education
        "degree": edu.get("degree", ""),
        "institution": edu.get("institution", ""),
        "graduation_year": edu.get("graduation_year", ""),
        "education_details": edu.get("education_details", ""),
        # Certifications
        "certifications": certifications,
        "certifications_flat": certifications_flat,
        # Job-specific
        "job_title": job_title,
        "company_name": company,
        "company_address": company_address,
        "role_type": role_type,
        "seniority": seniority,
        "job_description": job_description,
        "recipient_name": recipient_name,
        # Cover letter paragraphs
        "opening_paragraph": opening_paragraph,
        "company_motivation": company_motivation,
        "value_proposition": value_proposition,
        "closing_paragraph": closing_paragraph,
        # Outreach email parts
        "email_subject": email_subject,
        "opening_line": opening_line,
        "body_paragraph": body_paragraph,
        "call_to_action": call_to_action,
        # Meta
        "date": datetime.now().strftime("%d %B %Y").lstrip("0"),
    }


# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

def generate_application(job: dict, profile: dict, output_dir: Path) -> dict:
    """
    Generate all application documents for a single job.

    Returns a dict with paths to the generated files.
    """
    company_slug = re.sub(r"[^\w]+", "_", job.get("company", "company")).lower()
    title_slug = re.sub(r"[^\w]+", "_", job.get("job_title", "role")).lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{company_slug}_{title_slug}"
    dest = output_dir / folder_name
    dest.mkdir(parents=True, exist_ok=True)

    context = build_context(profile, job)

    templates = {
        "cv_nz_style.md": "cv_nz_style.md",
        "cv_ats.md": "cv_ats.md",
        "cover_letter.md": "cover_letter.md",
        "outreach_email.md": "outreach_email.md",
    }

    generated = {}
    for template_file, output_file in templates.items():
        raw = load_template(template_file)
        rendered = render_template(raw, context)
        out_path = dest / output_file
        out_path.write_text(rendered, encoding="utf-8")
        generated[output_file] = str(out_path)
        print(f"  [OK] {out_path.relative_to(REPO_ROOT)}")

    # Write job-tracking entry (JSON sidecar)
    tracking_entry = {
        "date_applied": datetime.now().strftime("%Y-%m-%d"),
        "company": job.get("company", ""),
        "job_title": job.get("job_title", ""),
        "role_type": job.get("role_type", ""),
        "seniority": job.get("seniority", ""),
        "status": "applied",
        "notes": job.get("notes", ""),
        "follow_up_date": "",
        "outcome": "",
        "output_folder": str(dest.relative_to(REPO_ROOT)),
    }
    tracking_path = dest / "tracking_entry.json"
    tracking_path.write_text(json.dumps(tracking_entry, indent=2), encoding="utf-8")
    generated["tracking_entry.json"] = str(tracking_path)
    print(f"  [OK] {tracking_path.relative_to(REPO_ROOT)}")

    return generated


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def prompt_job_details() -> dict:
    """Interactively prompt the user for job details."""
    print("\n=== Job Application Generator ===\n")
    company = input("Company name: ").strip()
    job_title = input("Job title: ").strip()
    print(f"Role type options: {', '.join(VALID_ROLE_TYPES)}")
    role_type = input("Role type: ").strip().lower()
    if role_type not in VALID_ROLE_TYPES:
        print(f"[WARN] '{role_type}' is not a standard role type. Using 'finance'.")
        role_type = "finance"
    print(f"Seniority options: {', '.join(VALID_SENIORITY)}")
    seniority = input("Seniority level: ").strip().lower()
    if seniority not in VALID_SENIORITY:
        print(f"[WARN] '{seniority}' is not a standard seniority. Using 'mid'.")
        seniority = "mid"
    job_description = input("Paste job description (single line, optional): ").strip()
    recipient_name = input("Recipient name (leave blank for 'Hiring Manager'): ").strip()
    notes = input("Notes (optional): ").strip()

    return {
        "company": company,
        "job_title": job_title,
        "role_type": role_type,
        "seniority": seniority,
        "job_description": job_description,
        "recipient_name": recipient_name or "Hiring Manager",
        "notes": notes,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate tailored job application documents."
    )
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--job-title", dest="job_title", help="Job title")
    parser.add_argument(
        "--role-type",
        dest="role_type",
        choices=VALID_ROLE_TYPES,
        default="finance",
        help="Type of role",
    )
    parser.add_argument(
        "--seniority",
        choices=VALID_SENIORITY,
        default="mid",
        help="Seniority level",
    )
    parser.add_argument("--job-description", dest="job_description", default="", help="Job description text")
    parser.add_argument("--recipient-name", dest="recipient_name", default="Hiring Manager")
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument(
        "--bulk",
        help="Path to a JSON file containing a list of job objects for bulk generation",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="output",
        help="Directory to save generated files (default: output/)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    profile = load_user_profile()
    output_dir = REPO_ROOT / args.output_dir

    if args.bulk:
        # Bulk mode: read list of jobs from JSON file
        bulk_path = Path(args.bulk)
        if not bulk_path.exists():
            print(f"[ERROR] Bulk file not found: {bulk_path}")
            sys.exit(1)
        with open(bulk_path, encoding="utf-8") as f:
            jobs = json.load(f)
        print(f"\nBulk generating {len(jobs)} application(s)...\n")
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {job.get('company')} — {job.get('job_title')}")
            generate_application(job, profile, output_dir)
            # Append to job history CSV
            from job_tracker import append_to_csv  # noqa: PLC0415
            append_to_csv(job, JOB_HISTORY_PATH)
        print("\nBulk generation complete.")

    elif args.company and args.job_title:
        # Single job from CLI flags
        job = {
            "company": args.company,
            "job_title": args.job_title,
            "role_type": args.role_type,
            "seniority": args.seniority,
            "job_description": args.job_description,
            "recipient_name": args.recipient_name,
            "notes": args.notes,
        }
        print(f"\nGenerating application for {job['company']} — {job['job_title']}...")
        generate_application(job, profile, output_dir)
        # Append to job history CSV
        sys.path.insert(0, str(Path(__file__).parent))
        from job_tracker import append_to_csv  # noqa: PLC0415
        append_to_csv(job, JOB_HISTORY_PATH)
        print("\nDone.")

    else:
        # Interactive mode
        job = prompt_job_details()
        print(f"\nGenerating application for {job['company']} — {job['job_title']}...")
        generate_application(job, profile, output_dir)
        sys.path.insert(0, str(Path(__file__).parent))
        from job_tracker import append_to_csv  # noqa: PLC0415
        append_to_csv(job, JOB_HISTORY_PATH)
        print("\nDone.")


if __name__ == "__main__":
    main()
