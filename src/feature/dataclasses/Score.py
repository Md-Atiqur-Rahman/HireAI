from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Score:
    experience: float
    education: float
    technical_skills: float
    others: float
    total: float
    status: str
    is_matched: bool