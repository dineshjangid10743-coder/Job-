from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass
class Settings:
    job_sources: list
    custom_api_urls: list
    keywords: list
    location_auckland: str
    location_nz: str
    resume_path: Path
    cover_letter_path: Path
    db_path: Path
    output_dir: Path


def load_settings(env_path: str = ".env") -> Settings:
    load_dotenv(env_path)

    job_sources = _split_env("JOB_SOURCES", "linkedin,indeed,wellfound,custom_api")
    custom_api_urls = _split_env("CUSTOM_API_URLS", "")
    keywords = _split_env("KEYWORDS", "")

    location_auckland = os.getenv("LOCATION_AUCKLAND", "auckland")
    location_nz = os.getenv("LOCATION_NZ", "new zealand")

    resume_path = Path(os.getenv("RESUME_PATH", "./docs/resume.pdf"))
    cover_letter_path = Path(os.getenv("COVER_LETTER_PATH", "./docs/cover_letter.pdf"))

    db_path = Path(os.getenv("DB_PATH", "./data/jobs.db"))
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))

    return Settings(
        job_sources=job_sources,
        custom_api_urls=custom_api_urls,
        keywords=keywords,
        location_auckland=location_auckland,
        location_nz=location_nz,
        resume_path=resume_path,
        cover_letter_path=cover_letter_path,
        db_path=db_path,
        output_dir=output_dir,
    )


def _split_env(key: str, default: str) -> list:
    value = os.getenv(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]
