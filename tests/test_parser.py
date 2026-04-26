from datetime import datetime
from pathlib import Path

from logalyser.parser import parse_log, LogEntry

SAMPLE_LOG = Path(__file__).parent / "data" / "sample.log"


def test_parse_returns_entries():
    entries = list(parse_log(SAMPLE_LOG))
    assert len(entries) > 0


def test_entry_fields():
    entries = list(parse_log(SAMPLE_LOG))
    first = entries[0]
    assert isinstance(first.timestamp, datetime)
    assert first.process == "convman"
    assert "startup" in first.message.lower()


def test_level_inference():
    entries = list(parse_log(SAMPLE_LOG))
    levels = {e.level for e in entries}
    assert "ERROR" in levels
    assert "WARNING" in levels
    assert "INFO" in levels


def test_bz2_not_found_raises():
    import pytest
    with pytest.raises(FileNotFoundError):
        list(parse_log(Path("nonexistent.log")))