from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    source: str
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    posted_at: Optional[str] = None
    employment_type: Optional[str] = None
    score: float = 0.0
    raw: Optional[str] = None
