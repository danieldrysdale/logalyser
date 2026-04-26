"""
parser.py - Log file parsing for warehouse automation system log files.

Supports plain text and bz2-compressed log files.
Log line format: DD/MM/YYYY HH:MM:SS.ffffff  [process] message
"""

import bz2
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator


LOG_PATTERN = re.compile(
    r'^(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\.\d+)'
    r'\s+\[(?P<process>[^\]]+)\]'
    r'\s+(?P<message>.+)$'
)

TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S.%f"


@dataclass
class LogEntry:
    timestamp: datetime
    process: str
    message: str
    raw: str

    @property
    def level(self) -> str:
        """Infer severity level from message content."""
        msg = self.message.upper()
        if msg.startswith("ERROR"):
            return "ERROR"
        elif msg.startswith("WARNING") or msg.startswith("WARN"):
            return "WARNING"
        elif msg.startswith("FATAL"):
            return "FATAL"
        else:
            return "INFO"


def _open_log(path: Path):
    """Return a text-mode file handle for plain or bz2 log files."""
    if path.suffix == ".bz2":
        return bz2.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def parse_log(path: Path) -> Iterator[LogEntry]:
    """
    Parse a log file and yield LogEntry objects for each valid line.
    Silently skips malformed lines.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    with _open_log(path) as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            match = LOG_PATTERN.match(line)
            if not match:
                continue
            try:
                timestamp = datetime.strptime(
                    match.group("timestamp"), TIMESTAMP_FORMAT
                )
            except ValueError:
                continue
            yield LogEntry(
                timestamp=timestamp,
                process=match.group("process"),
                message=match.group("message"),
                raw=line,
            )