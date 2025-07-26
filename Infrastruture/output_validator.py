import importlib
import importlib.util
import os
from typing import Protocol, Dict, Any

class ResultChecker(Protocol):
    def __call__(self, outputs: Dict[str,Any]) -> bool:
        ...

def load_checker(path: str) -> ResultChecker:
    """
    Dynamically load a result-checker plugin.
    Path can be a module name or a filesystem path to a .py file defining a `check(outputs)` function.
    """
    if os.path.isfile(path):
        spec = importlib.util.spec_from_file_location("plugin", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
    else:
        module = importlib.import_module(path)
    if not hasattr(module, 'check'):
        raise ImportError(f"No `check` function found in plugin at {path}")
    return getattr(module, 'check')  # type: ignore
