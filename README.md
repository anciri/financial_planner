# Financial Planner

This project implements a small financial planning engine. Configuration is
stored in YAML files to make it easier to adapt parameters without changing the
code. The main script generates a sales plan that meets annual revenue goals
and consolidates cash flow and profit & loss statements.

## Structure

- `financial_planner/` package with the model implementation.
- `data/` YAML files with default configuration.
- `scripts/run_planner.py` command line interface.
- `tests/` simple unit tests.

## Usage

Install the dependencies (pandas, numpy, plotly, pyyaml) and run:

```bash
python -m financial_planner.scripts.run_planner --output-dir output
```

Results will be saved in `output/` and graphs displayed using Plotly.

Run tests with:

```bash
pytest
```
