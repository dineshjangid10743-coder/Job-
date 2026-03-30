import json
from pathlib import Path
from typing import Iterable

from .models import Job


def export_packets(jobs: Iterable[Job], output_dir: Path, resume_path: Path, cover_letter_path: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    packets = []
    for job in jobs:
        packets.append(
            {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "score": job.score,
                "resume": str(resume_path),
                "cover_letter": str(cover_letter_path),
            }
        )

    output_file = output_dir / "application_packets.json"
    output_file.write_text(json.dumps(packets, indent=2), encoding="utf-8")
    return output_file
