from typing import Iterable, List

from .models import Job


def score_jobs(jobs: Iterable[Job], keywords: List[str]) -> List[Job]:
    keywords_lower = [k.lower() for k in keywords]
    scored = []
    for job in jobs:
        text = f"{job.title} {job.description} {job.company}".lower()
        score = 0
        for kw in keywords_lower:
            if kw and kw in text:
                score += 1
        job.score = float(score)
        scored.append(job)
    return scored
