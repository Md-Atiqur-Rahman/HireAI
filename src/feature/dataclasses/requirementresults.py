from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RequirementResult:
    requirement: str
    status: str
    category: str
    matched_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    experience_check: Optional[str] = None
    reason: Optional[str] = None
    exp_ok: bool = False
    skills_ok: bool = False
    total_years: float = 0.0
    score: float = 0.0
