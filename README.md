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
git clone https://github.com/<your-org>/splinenorm.git
cd splinenorm
pip install -e ".[dev]"
```

## Documentation

Online docs are published via GitHub Pages after pushing to `main`.
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
| `docs/Getting_Started.ipynb` | Basic continuum removal |
| `docs/Fit_Continuum.ipynb` | Flat vs. template continuum strategies |
| `docs/Fit_Fringing.ipynb` | Fringing simulation and companion recovery |

## Tests

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
