"""Compilation-artifact cache: compile once, reuse across operations and sessions.

Opt-in in 2.9: nothing is written unless ``FLAMAPY_CACHE=1`` (3.0 flips this to an opt-out
``FLAMAPY_NO_CACHE``). Cache directory precedence: ``FLAMAPY_CACHE_DIR`` >
``$XDG_CACHE_HOME/flamapy`` > ``~/.flamapy/cache``. Artifacts are keyed by the model's
canonical hash, the target extension, the transformation's options and format version, and
the plugin version — and stored under ``<hash16>-<extension>-<digest>.<suffix>`` so
availability by (model, extension) is a glob away (the planner's ``artifact_available``
hook). Writes are atomic (``os.replace``); the cache is pruned LRU to
``FLAMAPY_CACHE_MAX_MB`` (default 500). A corrupt artifact is never fatal: loads fall back
to recomputation.
"""
import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

LOGGER = logging.getLogger('flamapy.cache')

DEFAULT_MAX_MB = 500


def enabled() -> bool:
    return os.environ.get('FLAMAPY_CACHE') == '1'


def directory() -> Path:
    explicit = os.environ.get('FLAMAPY_CACHE_DIR')
    if explicit:
        return Path(explicit)
    xdg = os.environ.get('XDG_CACHE_HOME')
    if xdg:
        return Path(xdg) / 'flamapy'
    return Path.home() / '.flamapy' / 'cache'


def artifact_key(
    model_hash: str,
    target_extension: str,
    options: dict[str, Any],
    format_version: int,
    plugin_version: str,
) -> str:
    canonical = '\x1f'.join([
        model_hash, target_extension,
        ';'.join(f'{key}={options[key]}' for key in sorted(options)),
        str(format_version), plugin_version,
    ])
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:32]


def artifact_path(
    model_hash: str, target_extension: str, key: str, suffix: str
) -> Path:
    return directory() / f'{model_hash[:16]}-{target_extension}-{key}.{suffix}'


def lookup(path: Path) -> Optional[Path]:
    """The artifact path if it exists (touching it for LRU), else None."""
    if not path.is_file():
        return None
    try:
        path.touch()
    except OSError:
        pass
    return path


def store(path: Path, write: Any) -> None:
    """Atomically create ``path`` by calling ``write(temporary_path)`` and renaming."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    os.close(handle)
    try:
        write(temporary)
        os.replace(temporary, path)
    except Exception:  # pylint: disable=broad-except
        LOGGER.exception('Could not store cache artifact %s', path)
        Path(temporary).unlink(missing_ok=True)
        return
    prune()


def available_for(model_hash: Optional[str], target_extension: str) -> bool:
    """Whether any artifact exists for (model, extension) — the planner's hook."""
    if not enabled() or not model_hash or not directory().is_dir():
        return False
    pattern = f'{model_hash[:16]}-{target_extension}-*'
    return any(directory().glob(pattern))


def prune(max_mb: Optional[int] = None) -> None:
    """Drop least-recently-used artifacts until the cache fits the size budget."""
    if max_mb is None:
        try:
            max_mb = int(os.environ.get('FLAMAPY_CACHE_MAX_MB', DEFAULT_MAX_MB))
        except ValueError:
            max_mb = DEFAULT_MAX_MB
    base = directory()
    if not base.is_dir():
        return
    files = [(path, path.stat()) for path in base.iterdir() if path.is_file()]
    total = sum(stat.st_size for _, stat in files)
    budget = max_mb * 1024 * 1024
    if total <= budget:
        return
    for path, stat in sorted(files, key=lambda item: item[1].st_mtime):
        try:
            path.unlink()
        except OSError:
            continue
        total -= stat.st_size
        if total <= budget:
            break


def info() -> dict[str, Any]:
    base = directory()
    files = [path for path in base.iterdir() if path.is_file()] if base.is_dir() else []
    return {
        'enabled': enabled(),
        'directory': str(base),
        'artifacts': len(files),
        'size_mb': round(sum(path.stat().st_size for path in files) / (1024 * 1024), 2),
    }


def clear() -> int:
    base = directory()
    removed = 0
    if base.is_dir():
        for path in base.iterdir():
            if path.is_file():
                try:
                    path.unlink()
                    removed += 1
                except OSError:
                    continue
    return removed
