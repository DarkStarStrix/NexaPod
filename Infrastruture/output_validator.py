from typing import Protocol, Dict, Any

class ResultChecker(Protocol):
    def __call__(self, outputs: Dict[str,Any]) -> bool:
        ...

# example plugin loader
def load_checker(path: str) -> ResultChecker:
    # dynamic import of user module
    # ...existing code...
    return lambda out: True

