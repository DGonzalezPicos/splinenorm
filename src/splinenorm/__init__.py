"""Spline normalization tools for astronomical spectra."""

from splinenorm.functions import solve_linear
from splinenorm.spline_model import SplineModel

__all__ = ["SplineModel", "solve_linear", "__version__"]
__version__ = "0.1.0"
