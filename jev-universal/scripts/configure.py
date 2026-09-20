"""Backward-compatible helper: print portable config; never overwrite shipped files."""
from jev_universal.cli import client_config
import json
print(json.dumps(client_config("claude"), indent=2))
