# logalyser

A command-line log analysis tool for warehouse automation logs.

Parses structured log output from conveyor and control processes,
surfaces error patterns, activity timelines, and message frequency — turning
raw log files into an actionable summary in seconds.

Supports plain text and bz2-compressed log files natively.

## Installation

Requires Python 3.12+.

```bash
git clone <repo-url>
cd logalyser
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### Analyse a log file

```bash
logalyser analyse path/to/logfile.log
logalyser analyse path/to/logfile.log.bz2
```

### Filter by severity level

```bash
logalyser analyse path/to/logfile.log --level ERROR
```

### Control the number of top messages shown

```bash
logalyser analyse path/to/logfile.log --top 20
```

## Example output

    ================================================================
      LOGALYSER REPORT
    ================================================================
      File analysed : logs/conveyor.log
      Time range    : 16/04/2026 01:15:03  →  16/04/2026 09:00:01
      Total entries : 28
    ================================================================
      ENTRIES BY SEVERITY
    ================================================================
      FATAL         0
      ERROR         6  ██████
      WARNING       2  ██
      INFO         20  ████████████████████
    ...
    ================================================================
      ACTIVITY TIMELINE  (entries per hour)
    ================================================================
      2026-04-16 01:00      4  ████
      2026-04-16 07:00     11  ███████████
      2026-04-16 08:00     10  ██████████
      2026-04-16 09:00      3  ███

## Project structure

    logalyser/
    ├── src/
    │   └── logalyser/
    │       ├── __init__.py
    │       ├── parser.py      # Log file parsing, bz2 support
    │       ├── analyser.py    # Statistical analysis
    │       └── cli.py         # Command-line interface
    ├── tests/
    │   ├── data/
    │   │   └── sample.log     # Representative sample log
    │   ├── test_parser.py
    │   └── test_analyser.py
    ├── pyproject.toml
    └── README.md
