Examples
========

Hands-on tutorials for ``splinenorm`` using bundled spectra in ``docs/data/``.
Each notebook is rendered below; use the toolbar to open it on GitHub or in Colab.

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Getting started
      :link: getting_started
      :link-type: doc
      :img-top: ../plots/remove_continuum_diagnostics.png
      :class-card: sd-card-hover

      Inject a synthetic blaze on a PHOENIX spectrum and recover the
      continuum-normalized shape with ``SplineModel`` and ``solve_linear``.

   .. grid-item-card:: Fit continuum
      :link: fit_continuum
      :link-type: doc
      :img-top: ../plots/fit_continuum_comparison.png
      :class-card: sd-card-hover

      Compare flat-line vs. PHOENIX-template continuum strategies on a real
      M-dwarf echelle order.

   .. grid-item-card:: Fit fringing
      :link: fit_fringing
      :link-type: doc
      :img-top: ../plots/fit_continuum_diagnostics.png
      :class-card: sd-card-hover

      Forward-model IFU fringes on a high-contrast spectrum and recover an
      injected companion signal.

.. toctree::
   :maxdepth: 1

   Getting started <getting_started>
   Fit continuum <fit_continuum>
   Fit fringing <fit_fringing>

Data and scripts
----------------

Example spectra ship with the repository under ``docs/data/`` (small ASCII
tables only). Re-run the notebooks after ``pip install -e ".[dev]"`` and
``pip install matplotlib ipython jupyter``.

``docs/high_contrast_specroscopy_speckles.py`` reproduces the fringing notebook
as a command-line demo using the same bundled data files.
