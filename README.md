# Job-

Python-based job application automation toolkit that **collects postings, filters for Auckland (full-time/part-time) and New Zealand (full-time), scores matches, and prepares application packets**. The final application submit step is **manual** to respect job board terms of service.

## Features
- Sources: LinkedIn, Indeed, Wellfound (AngelList), Custom APIs/RSS
- Location filters: Auckland (FT/PT), New Zealand (FT)
- Scoring + ranking
- Application tracking database (SQLite)
- Manual-submit packet generator

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/example.env .env
python -m job_automation.cli init-db
python -m job_automation.cli fetch
python -m job_automation.cli score
python -m job_automation.cli export
```

## Configuration
Edit `.env` (see `config/example.env`):
- `JOB_SOURCES` (comma-separated): linkedin, indeed, wellfound, custom_api
- `CUSTOM_API_URLS` (comma-separated)
- `RESUME_PATH` and `COVER_LETTER_PATH`
- `KEYWORDS`

## Notes on job board terms
Many job boards prohibit automated form submission. This project **does not auto-submit applications**. It focuses on collecting listings, scoring them, and preparing an application packet so you can manually submit.

## Next steps
- Add real API keys (where supported)
- Extend source adapters with your own parsing logic
- Add notifications (email/Slack)