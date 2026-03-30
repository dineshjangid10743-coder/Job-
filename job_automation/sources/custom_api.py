import json
from typing import List

import requests

from ..models import Job
from .base import JobSource


class CustomAPISource(JobSource):
    def __init__(self, urls: List[str]):
        self.urls = urls

    def fetch(self) -> List[Job]:
        jobs: List[Job] = []
        for url in self.urls:
            if not url:
                continue
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            items = data if isinstance(data, list) else data.get("jobs", [])
            for item in items:
                jobs.append(
                    Job(
                        source="custom_api",
                        title=item.get("title", ""),
                        company=item.get("company", ""),
                        location=item.get("location", ""),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                        posted_at=item.get("posted_at"),
                        employment_type=item.get("employment_type"),
                        raw=json.dumps(item),
                    )
                )
        return jobs
