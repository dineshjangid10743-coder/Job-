from typing import List

from ..models import Job
from .base import JobSource


class WellfoundSource(JobSource):
    def fetch(self) -> List[Job]:
        # Placeholder. Use Wellfound/AngelList APIs if available.
        return []
