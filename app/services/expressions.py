from functools import lru_cache
import os
from app.core.config import _ALLOWED_EXPRESSIONS_EXTS, EXPRESSIONS_DIR


@lru_cache(maxsize=1)
def get_available_expressions() -> list[str]:
    try:
        files = os.listdir(EXPRESSIONS_DIR)
    except FileNotFoundError:
        return []
    names = []
    for f in files:
        if f.startswith("."):
            continue
        name, ext = os.path.splitext(f)
        if ext.lower() in _ALLOWED_EXPRESSIONS_EXTS and name:
            names.append(name)
    return sorted(set(names))

def refresh_expressions_cache() -> None:
    get_available_expressions.cache_clear()