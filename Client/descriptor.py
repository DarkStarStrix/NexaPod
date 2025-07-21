from dataclasses import dataclass, field
from typing import Any, Dict, Callable, List

@dataclass
class JobDescriptor:
    id: str
    image: str
    compute_estimate: float                   # in FLOPs
    inputs: Dict[str, str]                    # {name: uri}
    outputs: Dict[str, str]                   # {name: path}
    checker: Callable[[Dict[str, Any]], bool] = field(default=lambda out: True)
    tags: List[str] = field(default_factory=list)

