from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

@dataclass
class JobDescriptor:
    """Descriptor for job configuration and validation."""
    id: str
    image: str
    compute_estimate: float
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    checker: Callable[[Dict[str, Any]], bool] = field(default=lambda out: True)
    tags: List[str] = field(default_factory=list)
