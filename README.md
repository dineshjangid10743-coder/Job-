# Job Application Automation System

Automate the generation of tailored CVs, cover letters, outreach emails, and job-tracking entries for multiple job types (finance, audit, part-time, full-time, graduate roles).

---

## Quick Start

```bash
# 1. Install Python 3.8+ (no external dependencies required)

# 2. Edit your personal profile
nano data/user_profile.json

# 3. Generate a single application (interactive)
python scripts/generate_application.py

# 4. Generate a single application (CLI flags)
python scripts/generate_application.py \
  --company "Deloitte NZ" \
  --job-title "Audit Senior" \
  --role-type audit \
  --seniority senior \
  --job-description "Lead risk-based audits for financial services clients."

# 5. Bulk generate from a JSON list
python scripts/generate_application.py --bulk examples/input/bulk_jobs.json

# 6. View and manage your tracker
python scripts/job_tracker.py list
python scripts/job_tracker.py summary
python scripts/job_tracker.py update --id 2 --status interviewed
python scripts/job_tracker.py export --output output/jobs.json
```

---

## Repository Structure

```
Job-/
├── templates/
│   ├── cv_nz_style.md        # NZ-style CV template
│   ├── cv_ats.md             # ATS-optimised CV template
│   ├── cover_letter.md       # Cover letter template
│   └── outreach_email.md     # Outreach / cold-email template
│
├── scripts/
│   ├── generate_application.py   # Main automation script
│   └── job_tracker.py            # Job tracking utility
│
├── data/
│   ├── user_profile.json     # Your personal details, skills, experience
│   └── job_history.csv       # Running log of all applications
│
├── examples/
│   ├── input/
│   │   ├── single_job.json   # Example single-job input
│   │   └── bulk_jobs.json    # Example bulk-job input (3 companies)
│   └── output/               # Sample generated documents
│
└── output/                   # Generated files go here (timestamped folders)
```

---

## Configuration

### User Profile (`data/user_profile.json`)

This file stores all your personal details, work history, education, and skills. Edit it before running the scripts.

Key fields:

| Field | Description |
|---|---|
| `full_name` | Your full name |
| `location` | City / country |
| `email` | Contact email |
| `phone` | Contact phone |
| `linkedin` | LinkedIn profile URL |
| `key_skills` | Array of skills |
| `work_experience` | Array of previous roles (each with title, company, dates, description, achievements) |
| `education` | Degree, institution, graduation year |
| `certifications` | Array of certifications |
| `role_summaries` | Role-type-specific profile summaries keyed by role type |
| `ats_keywords` | Role-type-specific ATS keyword lists |

### Role Types

| Role Type | Description |
|---|---|
| `finance` | Financial analysis, reporting, FP&A |
| `audit` | Internal / external audit |
| `part_time` | Part-time / casual roles |
| `full_time` | General full-time professional |
| `graduate` | Graduate programmes, entry-level |

### Seniority Levels

`entry`, `mid`, `senior`, `manager`, `director`

---

## Generated Output

Each run creates a **timestamped folder** inside `output/` (or your chosen `--output-dir`):

```
output/
└── 20240115_143022_deloitte_nz_audit_senior/
    ├── cv_nz_style.md
    ├── cv_ats.md
    ├── cover_letter.md
    ├── outreach_email.md
    └── tracking_entry.json
```

The job is also appended to `data/job_history.csv` automatically.

---

## Adding New Templates

1. Create a new `.md` file in `templates/` using `{{placeholder}}` syntax for variable substitution.
2. In `scripts/generate_application.py`, add the template file name to the `templates` dict inside `generate_application()`:

```python
templates = {
    "cv_nz_style.md": "cv_nz_style.md",
    "cv_ats.md": "cv_ats.md",
    "cover_letter.md": "cover_letter.md",
    "outreach_email.md": "outreach_email.md",
    "my_new_template.md": "my_new_template.md",   # ← add this
}
```

3. Any `{{key}}` in your template that matches a key in the context dict (see `build_context()`) will be replaced automatically. Add custom keys to `build_context()` if needed.

---

## Job Tracker

The tracker stores all applications in `data/job_history.csv`.

### Commands

```bash
# List all applications
python scripts/job_tracker.py list

# Show statistics (total, by status, by role type, interview rate)
python scripts/job_tracker.py summary

# Update application status
python scripts/job_tracker.py update --id 3 --status interview_scheduled

# Manually add an entry
python scripts/job_tracker.py add --company "ANZ" --job-title "FP&A Analyst" \
    --role-type finance --seniority mid

# Export to JSON
python scripts/job_tracker.py export --output output/jobs_export.json
```

### Valid Statuses

`applied`, `interview_scheduled`, `interviewed`, `offer_received`, `accepted`, `rejected`, `withdrawn`

---

## Bulk Generation

Create a JSON file (see `examples/input/bulk_jobs.json`) with a list of job objects:

```json
[
  {
    "company": "Deloitte New Zealand",
    "job_title": "Audit Senior",
    "role_type": "audit",
    "seniority": "senior",
    "job_description": "Lead audit engagements ...",
    "recipient_name": "Talent Acquisition Team",
    "company_address": "Auckland, NZ",
    "notes": "Applied via Seek"
  }
]
```

Then run:

```bash
python scripts/generate_application.py --bulk examples/input/bulk_jobs.json
```

---

## Requirements

- Python 3.8+
- No external packages required (uses only the Python standard library)

---

## Licence

MIT
