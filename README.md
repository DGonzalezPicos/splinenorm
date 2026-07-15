# splinenorm

**B-spline continuum normalization** and
weighted linear fitting of astronomical spectra.

## Features

- `SplineModel` — decompose a spectrum into B-spline basis components (adapted from [breads](https://github.com/jruffio/breads); see [Ruffio et al. 2023](https://doi.org/10.3847/1538-3881/acb34a))
- `solve_linear` — fit design-matrix amplitudes with optional non-negative least squares, supporting diagonal or full inverse covariance

## Installation

Install from source:

```bash
git clone https://github.com/DGonzalezPicos/splinenorm.git
cd splinenorm
pip install -e ".[dev]"
```

## Documentation

Online docs: **https://dgonzalezpicos.github.io/splinenorm/**

The docs include Jupyter notebooks, API reference, and GitHub/Colab launch links.

## Examples

Jupyter notebooks in `docs/examples/` walk through continuum removal, PHOENIX-template
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

## Citation

If you use this package, please cite:

> González Picos et al. (2025), *Astronomy & Astrophysics*, [doi:10.1051/0004-6361/202451936](https://doi.org/10.1051/0004-6361/202451936)

The spline-based forward model follows Ruffio et al. (2023), *AJ*, 165, 113, [doi:10.3847/1538-3881/acb34a](https://doi.org/10.3847/1538-3881/acb34a). See [CITATION.cff](CITATION.cff) for machine-readable metadata.

## License

MIT — see [LICENSE](LICENSE).
