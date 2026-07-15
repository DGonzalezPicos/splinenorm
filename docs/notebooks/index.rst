Notebooks
=========

Interactive walkthroughs using bundled spectra in ``docs/data/``. Each notebook
can be read here, opened in Colab, or downloaded from the toolbar at the top of
the page.

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Getting started
      :link: ../Getting_Started
      :link-type: doc
      :img-top: ../plots/remove_continuum_diagnostics.png
      :class-card: sd-card-hover

      Inject a synthetic blaze on a PHOENIX spectrum and recover the
      continuum-normalized shape with ``SplineModel`` and ``solve_linear``.

   .. grid-item-card:: Fit continuum
      :link: ../Fit_Continuum
      :link-type: doc
      :img-top: ../plots/fit_continuum_comparison.png
      :class-card: sd-card-hover

      Compare flat-line vs. PHOENIX-template continuum strategies on a real
      M-dwarf echelle order.

   .. grid-item-card:: Fit fringing
      :link: ../Fit_Fringing
      :link-type: doc
      :img-top: ../plots/fit_continuum_diagnostics.png
      :class-card: sd-card-hover

      Forward-model IFU fringes on a high-contrast spectrum and recover an
      injected companion signal.

Data
----

Example spectra ship with the repository under ``docs/data/`` (small ASCII
tables only). Re-run the notebooks after ``pip install -e ".[dev]"`` and
``pip install matplotlib ipython jupyter``.

Script
------

``docs/high_contrast_specroscopy_speckles.py`` reproduces the fringing notebook
as a command-line demo using the same bundled data files.
