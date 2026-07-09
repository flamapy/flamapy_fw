"""Streaming results: operations whose (list-like) result can be consumed incrementally.

An operation opts in by inheriting :class:`StreamingOperation` and overriding
:meth:`iter_execute` with a real generator (e.g. pysat's configuration enumeration yields
each model as the solver produces it). The default implementation preserves semantics for
consumers that stream unconditionally: it executes fully and then yields.
"""
from typing import Any, Iterator

from flamapy.core.models import VariabilityModel


class StreamingOperation:
    def iter_execute(self, model: VariabilityModel) -> Iterator[Any]:
        """Lazily yield the operation's result items on ``model``.

        Default: run :meth:`execute` to completion and yield from :meth:`get_result` —
        override with a generator for true incremental results.
        """
        self.execute(model)  # type: ignore[attr-defined]
        yield from self.get_result()  # type: ignore[attr-defined]
