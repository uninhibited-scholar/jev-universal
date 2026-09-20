"""Private, short-lived storage for recoverable large tool output."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import time
from pathlib import Path

_ID_RE = re.compile(r"^(?P<session>[0-9a-f]{16})-(?P<output>[0-9a-f]{16})$")
OUTPUT_TTL_SECONDS = 3_600


def _session_key(session_id: str) -> str:
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:16]
    return f"session-{digest}"


def _store_root(root: Path | None = None) -> Path:
    return root if root is not None else Path(tempfile.gettempdir()) / "jev-output-store"


def store_output(
    session_id: str, text: str, root: Path | None = None
) -> tuple[str, Path]:
    base = _store_root(root)
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    if base.is_symlink():
        raise OSError("refusing symlinked output store")
    os.chmod(base, 0o700)
    session_dir = base / _session_key(session_id)
    if session_dir.is_symlink():
        raise OSError("refusing symlinked output directory")
    session_dir.mkdir(mode=0o700, exist_ok=True)
    os.chmod(session_dir, 0o700)
    output_id = os.urandom(8).hex()
    path = session_dir / f"{output_id}.txt"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    session_hash = session_dir.name.removeprefix("session-")
    return f"{session_hash}-{output_id}", path


def read_output(output_id: str, root: Path | None = None) -> str:
    match = _ID_RE.fullmatch(output_id)
    if not match:
        raise ValueError("invalid output id")
    base = _store_root(root)
    if base.is_symlink():
        raise FileNotFoundError("output is unavailable; store path is unsafe")
    session_dir = base / f"session-{match.group('session')}"
    if session_dir.is_symlink() or not session_dir.is_dir():
        raise FileNotFoundError("output is unavailable; it may have expired with its session")
    path = session_dir / f"{match.group('output')}.txt"
    if path.is_symlink() or not path.is_file():
        raise FileNotFoundError("output is unavailable; it may have expired with its session")
    if path.stat().st_mtime < time.time() - OUTPUT_TTL_SECONDS:
        path.unlink(missing_ok=True)
        raise FileNotFoundError("output expired; parked results are kept for one hour")
    return path.read_text(encoding="utf-8")


def cleanup_stale(root: Path | None = None, max_age_seconds: int = 86_400) -> None:
    base = _store_root(root)
    if not base.is_dir() or base.is_symlink():
        return
    cutoff = time.time() - min(max_age_seconds, OUTPUT_TTL_SECONDS)
    for path in base.glob("session-*"):
        if not re.fullmatch(r"session-[0-9a-f]{16}", path.name):
            continue
        if path.is_symlink():
            continue
        try:
            if not path.is_dir():
                continue
            for child in path.glob("*.txt"):
                if child.is_file() and not child.is_symlink() and child.stat().st_mtime < cutoff:
                    child.unlink(missing_ok=True)
            if not any(path.iterdir()):
                path.rmdir()
        except OSError:
            continue
