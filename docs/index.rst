splinenorm
==========

.. raw:: html

   <p class="sn-lead">
   Lightweight tools for <strong>B-spline continuum normalization</strong> and
   weighted linear fitting of one-dimensional astronomical spectra.
   Decompose a spectrum into spline basis components, then solve for amplitudes
   with optional non-negative least squares.
   </p>

   <div class="sn-quick-links">
     <a href="examples/index.html">Examples</a>
     <a href="api.html">API reference</a>
     <a href="https://github.com/DGonzalezPicos/splinenorm">GitHub</a>
   </div>

Installation
------------

.. code-block:: bash

   pip install splinenorm

Development install:

.. code-block:: bash

   git clone https://github.com/DGonzalezPicos/splinenorm.git
   cd splinenorm
   pip install -e ".[dev]"

Quick start
-----------

.. code-block:: python

   import numpy as np
   from splinenorm import SplineModel, solve_linear

   flux = np.loadtxt("spectrum.txt")
   model = SplineModel(n_knots=10)
   components = model(flux)
   amplitudes = solve_linear(flux, np.ones_like(flux), components)

Examples
--------

Browse the :doc:`examples gallery <examples/index>` for step-by-step notebooks
with bundled spectroscopic data:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Getting started
      :link: examples/getting_started
      :link-type: doc
      :img-top: plots/remove_continuum_diagnostics.png
      :class-card: sd-card-hover

      Synthetic blaze injection and continuum removal.

   .. grid-item-card:: Fit continuum
      :link: examples/fit_continuum
      :link-type: doc
      :img-top: plots/fit_continuum_comparison.png
      :class-card: sd-card-hover

      Real M-dwarf data: flat vs. template continuum.

   .. grid-item-card:: Fit fringing
      :link: examples/fit_fringing
      :link-type: doc
      :img-top: plots/fit_fringing_diagnostics.png
      :class-card: sd-card-hover

      IFU fringing and companion recovery in high-contrast spectroscopy.

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

.. toctree::
   :maxdepth: 1
   :caption: Reference

   API <api>

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
