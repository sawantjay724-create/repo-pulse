# repo-pulse

[![CI](https://github.com/YOUR-USERNAME/repo-pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-USERNAME/repo-pulse/actions)

A zero-dependency command-line tool that reads a git repository and shows:

- **Top authors** by commit count
- **Activity by weekday**
- **Hotspot files** that change most often (likely fragile or complex code)
- **Bus factor**: how few people made over half the commits

## Install

```bash
pip install git+https://github.com/YOUR-USERNAME/repo-pulse.git
```

Or from a clone:

```bash
git clone https://github.com/YOUR-USERNAME/repo-pulse.git
cd repo-pulse
pip install -e ".[dev]"
```

## Usage

```bash
repo-pulse                         # analyse the current directory
repo-pulse ~/code/myproject --since "6 months ago" --top 5
repo-pulse --json > stats.json     # machine-readable output
```

Example output:

```
Commits analysed: 128
Bus factor: 2

Top authors
  Alice                     71  ████████████████████████
  Bob                       40  ██████████████
  ...
```

## Development

```bash
pytest
```

The code lives in `repo_pulse/`: `core.py` (git parsing and statistics) and `cli.py` (output). Only Python 3.9+ and `git` are required.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
