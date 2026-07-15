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
     <a href="notebooks/index.html">Browse notebooks</a>
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

Notebooks
---------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Getting started
      :link: Getting_Started
      :link-type: doc
      :img-top: plots/remove_continuum_diagnostics.png
      :class-card: sd-card-hover

      Synthetic blaze injection and continuum removal.

   .. grid-item-card:: Fit continuum
      :link: Fit_Continuum
      :link-type: doc
      :img-top: plots/fit_continuum_comparison.png
      :class-card: sd-card-hover

      Real M-dwarf data: flat vs. template continuum.

   .. grid-item-card:: Fit fringing
      :link: Fit_Fringing
      :link-type: doc
      :img-top: plots/fit_continuum_diagnostics.png
      :class-card: sd-card-hover

      IFU fringing and companion recovery in high-contrast spectroscopy.

See the full :doc:`notebook gallery <notebooks/index>`.

.. toctree::
   :maxdepth: 2
   :caption: Notebooks
   :hidden:

   Gallery <notebooks/index>
   Getting Started <Getting_Started>
   Fit Continuum <Fit_Continuum>
   Fit Fringing <Fit_Fringing>

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   api

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
