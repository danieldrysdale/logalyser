"""
analyser.py - Statistical analysis of parsed log entries.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from .parser import LogEntry


@dataclass
class AnalysisResult:
    total_entries: int = 0
    level_counts: Counter = field(default_factory=Counter)
    process_counts: Counter = field(default_factory=Counter)
    errors_by_process: dict = field(default_factory=lambda: defaultdict(list))
    entries_by_hour: dict = field(default_factory=lambda: defaultdict(int))
    top_messages: Counter = field(default_factory=Counter)
    time_start: datetime | None = None
    time_end: datetime | None = None


def analyse(entries: list[LogEntry], top_n: int = 10) -> AnalysisResult:
    """
    Analyse a list of LogEntry objects and return an AnalysisResult.
    """
    result = AnalysisResult()

    for entry in entries:
        result.total_entries += 1

        # Track time range
        if result.time_start is None or entry.timestamp < result.time_start:
            result.time_start = entry.timestamp
        if result.time_end is None or entry.timestamp > result.time_end:
            result.time_end = entry.timestamp

        # Count by level and process
        result.level_counts[entry.level] += 1
        result.process_counts[entry.process] += 1

        # Group errors and warnings by process
        if entry.level in ("ERROR", "WARNING", "FATAL"):
            result.errors_by_process[entry.process].append(entry)

        # Timeline — bucket by hour
        hour_key = entry.timestamp.strftime("%Y-%m-%d %H:00")
        result.entries_by_hour[hour_key] += 1

        # Count message frequency (strip SSCCs to avoid noise)
        normalised = _normalise_message(entry.message)
        result.top_messages[normalised] += 1

    # Trim top_messages to top_n
    result.top_messages = Counter(
        dict(result.top_messages.most_common(top_n))
    )

    return result


def _normalise_message(message: str) -> str:
    """
    Strip variable data (SSCCs, port numbers, attempt counts) from messages
    so that repeated messages with different values are counted together.
    """
    import re
    # Strip SSCCs (18-digit numbers)
    message = re.sub(r'\d{20}', '<SSCC>', message)
    # Strip port numbers
    message = re.sub(r'port \d+', 'port <N>', message)
    # Strip attempt counts
    message = re.sub(r'attempt \d+ of \d+', 'attempt <N> of <N>', message)
    return message