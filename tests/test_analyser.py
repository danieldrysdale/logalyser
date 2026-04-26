from pathlib import Path

from logalyser.parser import parse_log
from logalyser.analyser import analyse

SAMPLE_LOG = Path(__file__).parent / "data" / "sample.log"


def _get_result():
    entries = list(parse_log(SAMPLE_LOG))
    return analyse(entries)


def test_total_entries():
    result = _get_result()
    assert result.total_entries == 28


def test_level_counts():
    result = _get_result()
    assert result.level_counts["ERROR"] > 0
    assert result.level_counts["WARNING"] > 0
    assert result.level_counts["INFO"] > 0


def test_errors_by_process():
    result = _get_result()
    assert "conveyor" in result.errors_by_process
    assert "io_process" in result.errors_by_process


def test_timeline_buckets():
    result = _get_result()
    # Sample log spans multiple hours
    assert len(result.entries_by_hour) >= 3


def test_time_range():
    result = _get_result()
    assert result.time_start is not None
    assert result.time_end is not None
    assert result.time_end > result.time_start


def test_message_normalisation():
    result = _get_result()
    # WAGO errors should be collapsed into one message key
    wago_keys = [k for k in result.top_messages if "WAGO" in k]
    assert len(wago_keys) == 1