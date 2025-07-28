"""
Dynamically load and validate job result checkers.
"""
import importlib
import importlib.util
import os
from typing import Protocol, Dict, Any

class ResultChecker(Protocol):
    """Protocol for result checker callables."""
    def __call__(self, outputs: Dict[str, Any]) -> bool:
        ...

def load_checker(path: str) -> ResultChecker:
    """Load and return a result-checker plugin."""
    if os.path.isfile(path):
        spec = importlib.util.spec_from_file_location("plugin", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
    else:
        module = importlib.import_module(path)
    if not hasattr(module, 'check'):
        raise ImportError(f"No `check` function found in plugin at {path}")
    return getattr(module, 'check')
