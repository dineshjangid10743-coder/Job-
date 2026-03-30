from typing import List

from ..models import Job
from .base import JobSource


class LinkedInSource(JobSource):
    def fetch(self) -> List[Job]:
        # Placeholder. LinkedIn has strict terms and anti-bot protections.
        # Implement via official APIs/feeds if you have access.
        return []
