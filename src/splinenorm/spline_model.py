"""B-spline decomposition model for one-dimensional spectra.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.interpolate import InterpolatedUnivariateSpline


class SplineModel:
    """Decompose a 1D spectrum into spline basis components.

    Adapted from the `breads <https://github.com/jruffio/breads>`_ package.
    The spline-based continuum forward model follows Ruffio et al. (2023),
    AJ, 165, 113, https://doi.org/10.3847/1538-3881/acb34a.

    Parameters
    ----------
    n_knots
        Number of spline knots.
    spline_degree
        Spline polynomial degree (cubic splines by default).
    """

    def __init__(self, n_knots: int = 10, spline_degree: int = 3) -> None:
        if n_knots < 2:
            raise ValueError(f"n_knots must be at least 2, got {n_knots}")
        if spline_degree < 1:
            raise ValueError(f"spline_degree must be at least 1, got {spline_degree}")

        self.n_knots = n_knots
        self.spline_degree = min(spline_degree, n_knots - 1)

    def _build_design_matrix(
        self,
        sample_indices: NDArray[np.float64],
        knot_positions: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Return spline design matrix with shape ``(n_pixels, n_knots)``."""
        if knot_positions.size <= self.spline_degree:
            raise ValueError(
                "spline_degree must be smaller than the number of knots "
                f"({knot_positions.size})."
            )

        n_pixels = sample_indices.size
        design_matrix = np.zeros((n_pixels, self.n_knots), dtype=np.float64)

        knot_minimum = knot_positions.min()
        knot_maximum = knot_positions.max()
        in_range = (knot_minimum < sample_indices) & (sample_indices < knot_maximum)
        if not np.any(in_range):
            return design_matrix

        sample_indices_in_range = sample_indices[in_range]
        for knot_index in range(self.n_knots):
            basis_values = np.zeros(self.n_knots, dtype=float)
            basis_values[knot_index] = 1.0
            spline = InterpolatedUnivariateSpline(
                knot_positions,
                basis_values,
                k=self.spline_degree,
                ext=0,
            )
            design_matrix[in_range, knot_index] = spline(sample_indices_in_range)

        return design_matrix

    def __call__(self, spectrum: ArrayLike) -> NDArray[np.float64]:
        """Return spline components with shape ``(n_knots, n_pixels)``."""
        spectrum = np.asarray(spectrum, dtype=float)
        if spectrum.ndim != 1:
            raise ValueError(f"spectrum must be 1D, got shape {spectrum.shape}.")
        if spectrum.size == 0:
            raise ValueError("spectrum must contain at least one pixel.")

        sample_indices = np.arange(spectrum.size, dtype=float)
        knot_positions = np.linspace(-1.0, spectrum.size + 1.0, self.n_knots)
        design_matrix = self._build_design_matrix(sample_indices, knot_positions)
        return design_matrix.T * spectrum
