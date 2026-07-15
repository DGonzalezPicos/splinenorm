# splinenorm

Lightweight Python tools for **B-spline continuum normalization** and
weighted linear fitting of one-dimensional astronomical spectra.

## Features

- `SplineModel` — decompose a spectrum into B-spline basis components (adapted from [breads](https://github.com/jruffio/breads))
- `solve_linear` — fit design-matrix amplitudes with optional non-negative least squares, supporting diagonal or full inverse covariance

## Installation

```bash
pip install splinenorm
```

Development install:

```bash
git clone https://github.com/DGonzalezPicos/splinenorm.git
cd splinenorm
pip install -e ".[dev]"
```

## Documentation

Online docs: **https://dgonzalezpicos.github.io/splinenorm/**

The docs include rendered Jupyter notebooks with a figure gallery, API reference,
and GitHub/Colab launch links on each notebook page.

Build locally:

```bash
pip install -e ".[docs]"
make -C docs html
```

Open `docs/_build/html/index.html` in a browser.

## Examples

Jupyter notebooks in `docs/` walk through continuum removal, PHOENIX-template
fitting, and high-contrast IFU fringing recovery. Example spectra ship in
`docs/data/`; diagnostic figures are in `docs/plots/`.

| Notebook | Topic |
|---|---|
| `docs/examples/getting_started.ipynb` | Basic continuum removal |
| `docs/examples/fit_continuum.ipynb` | Flat vs. template continuum strategies |
| `docs/examples/fit_fringing.ipynb` | Fringing simulation and companion recovery |

## Tests

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
