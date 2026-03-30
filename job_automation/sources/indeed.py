from typing import List

from ..models import Job
from .base import JobSource


class IndeedSource(JobSource):
    def fetch(self) -> List[Job]:
        # Placeholder. Indeed has strict terms and anti-bot protections.
        # Implement via official APIs/feeds if you have access.
        return []
