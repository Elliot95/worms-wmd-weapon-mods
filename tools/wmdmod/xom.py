"""Reader for Team17 XOM containers (magic ``MOIK``).

Nothing here assumes a field layout we have not actually observed. The job of
this module right now is *structural*: locate the section tags and the string
table so we can learn the format from real files instead of guessing.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from pathlib import Path

MAGIC = b"MOIK"

#: Four-byte section tags seen in real containers.
KNOWN_TAGS = (b"TYPE", b"GUID", b"SCHM", b"STRS")

_TAG_RE = re.compile(b"|".join(re.escape(t) for t in KNOWN_TAGS))

_PRINTABLE = set(string.printable.encode("ascii")) - set(b"\t\n\r\v\f")


@dataclass
class Section:
    """One tagged section, as found by scanning."""

    tag: str
    offset: int
    #: Bytes from this tag up to the next tag (or EOF). Not a parsed length.
    span: int

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Section {self.tag} @0x{self.offset:x} span={self.span}>"


@dataclass
class XomFile:
    path: Path
    size: int
    has_magic: bool
    sections: list[Section] = field(default_factory=list)
    type_names: list[str] = field(default_factory=list)

    @property
    def tag_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for s in self.sections:
            counts[s.tag] = counts.get(s.tag, 0) + 1
        return counts


def ascii_runs(data: bytes, minimum: int = 4) -> list[tuple[int, str]]:
    """Yield ``(offset, text)`` for printable ASCII runs of ``minimum``+ chars."""
    out: list[tuple[int, str]] = []
    start = -1
    for i, b in enumerate(data):
        if b in _PRINTABLE:
            if start < 0:
                start = i
        else:
            if start >= 0 and i - start >= minimum:
                out.append((start, data[start:i].decode("ascii")))
            start = -1
    if start >= 0 and len(data) - start >= minimum:
        out.append((start, data[start:].decode("ascii")))
    return out


def scan(path: str | Path, *, read_limit: int | None = None) -> XomFile:
    """Structurally scan a ``.bdl`` / ``.xom`` file.

    ``read_limit`` caps how many bytes are read, so the 87 MB bundles can be
    probed cheaply. Pass ``None`` to read the whole file.
    """
    p = Path(path)
    size = p.stat().st_size
    with p.open("rb") as fh:
        data = fh.read(size if read_limit is None else min(read_limit, size))

    hits = [(m.start(), m.group()) for m in _TAG_RE.finditer(data)]
    sections: list[Section] = []
    for idx, (off, tag) in enumerate(hits):
        end = hits[idx + 1][0] if idx + 1 < len(hits) else len(data)
        sections.append(Section(tag.decode("ascii"), off, end - off))

    # Class names sit just after a TYPE tag; take the first ASCII run inside
    # each TYPE section that looks like an identifier.
    type_names: list[str] = []
    for s in sections:
        if s.tag != "TYPE":
            continue
        chunk = data[s.offset + len(s.tag) : s.offset + s.span]
        for _, text in ascii_runs(chunk, minimum=4):
            if text[0].isalpha() and all(c.isalnum() or c == "_" for c in text):
                type_names.append(text)
                break

    return XomFile(
        path=p,
        size=size,
        has_magic=data[: len(MAGIC)] == MAGIC,
        sections=sections,
        type_names=type_names,
    )
