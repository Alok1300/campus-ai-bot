import json
import os
from app.config import settings

def load_aliases():
    alias_file = os.path.join(settings.DATA_DIR, "aliases.json")
    if not os.path.exists(alias_file):
        return {}
    with open(alias_file, "r") as f:
        return json.load(f)

ALIASES = load_aliases()

def resolve_alias(name: str) -> str | None:
    if not name:
        return None
    normalized = name.lower().strip()
    return ALIASES.get(normalized)
