"""Simulate IFU fringing in high-contrast spectroscopy and recover a faint companion.

IFU fringes are modeled as a multiplicative pattern built from a
sinc-smoothed cosine carrier (etalon-like periodic modulation). The
diffracted starlight is forward-modeled with ``splinenorm`` using a PHOENIX
template modulated by B-splines; the residual is compared to the injected
companion spectrum.
"""

from __future__ import annotations

import argparse
import h5py
import numpy as np
from astropy import units as u
from matplotlib import pyplot as plt
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

from splinenorm.functions import solve_linear
from splinenorm.spline_model import SplineModel

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / "data"
PLANET_MODEL_FILE = DATA_DIR / "HD19467B_spectrum_bestfit_model.txt"
PHOENIX_H5 = Path(
    "/data2/picos/phoenix-newera/data_v2/"
    "lte05500-4.50-0.0.PHOENIX-NewEra-ACES-COND-2023.HSR.h5"
)
HOST_DISTANCE_PC = 32.03
DETECTOR_SPLIT_UM = 4.1  # NRS1 below, NRS2 at/above (JWST/NIRSpec)
DEFAULT_DETECTOR = 1
PSF_FLUX_SUPPRESSION = 100.0
N_KNOTS = 151
FRINGE_AMPLITUDE = 0.05
FRINGE_PERIOD_PIX = 100.0
FRINGE_SINC_SCALE = 2.5
FRINGE_SUPERSAMPLE = 10  # fine wavelength grid factor before interpolating to data
COMPANION_DEMO_SCALE = 1.0  # boost companion for visible recovery demo


def select_detector(wavelength: np.ndarray, detector: int = DEFAULT_DETECTOR) -> np.ndarray:
    """Return boolean mask for NRS1 (detector=1) or NRS2 (detector=2)."""
    if detector == 1:
        return wavelength < DETECTOR_SPLIT_UM
    if detector == 2:
        return wavelength >= DETECTOR_SPLIT_UM
    raise ValueError(f"detector must be 1 or 2, got {detector}")


def detector_label(detector: int) -> str:
    return f"NRS{detector}"


def load_planet_spectrum(
    detector: int = DEFAULT_DETECTOR,
    planet_model_file: Path = PLANET_MODEL_FILE,
) -> tuple[np.ndarray, np.ndarray]:
    """Load companion spectrum for one NIRSpec detector."""
    planet_data = np.loadtxt(planet_model_file, comments="#")
    wavelength = planet_data[:, 0]
    planet_flux = planet_data[:, 3]  # W m^-2 micron^-1
    detector_mask = select_detector(wavelength, detector)
    return wavelength[detector_mask], planet_flux[detector_mask]


def build_ifu_fringes(
    wavelength: np.ndarray,
    amplitude: float = FRINGE_AMPLITUDE,
    period_pix: float = FRINGE_PERIOD_PIX,
    sinc_scale: float = FRINGE_SINC_SCALE,
    supersample: int = FRINGE_SUPERSAMPLE,
) -> np.ndarray:
    """Return multiplicative IFU fringe pattern on the data wavelength grid.

    The sinc-smoothed carrier is evaluated on a supersampled wavelength grid
    with edge padding, then linearly interpolated onto ``wavelength`` to
    reduce boundary artifacts from the convolution.
    """
    wavelength = np.asarray(wavelength, dtype=float)
    if wavelength.size < 2:
        raise ValueError("wavelength must contain at least two points.")

    dlam = float(np.median(np.diff(wavelength)))
    period_um = period_pix * dlam

    pad_pix = int(4.0 * sinc_scale * supersample)
    wl_min = wavelength.min() - pad_pix * dlam / supersample
    wl_max = wavelength.max() + pad_pix * dlam / supersample
    n_fine = (wavelength.size - 1) * supersample + 1 + 2 * pad_pix
    wl_fine = np.linspace(wl_min, wl_max, n_fine)

    phase = 2.0 * np.pi * (wl_fine - wl_fine[0]) / period_um
    carrier = np.cos(phase)

    half_width = int(4.0 * sinc_scale * supersample)
    kernel_x = np.arange(-half_width, half_width + 1, dtype=float)
    kernel = np.sinc(kernel_x / (sinc_scale * supersample))
    kernel /= kernel.sum()

    modulated = np.convolve(carrier, kernel, mode="same")
    peak = np.max(np.abs(modulated))
    if peak > 0.0:
        modulated /= peak
    fringes_fine = 1.0 + amplitude * modulated

    return np.interp(wavelength, wl_fine, fringes_fine)


def load_star_template(
    planet_wavelength: np.ndarray,
    phoenix_h5: Path = PHOENIX_H5,
    distance_pc: float = HOST_DISTANCE_PC,
    resolution: float = 2700.0,
) -> np.ndarray:
    """Load, broaden, dilute, and resample a PHOENIX host-star template."""
    with h5py.File(phoenix_h5, "r") as handle:
        wavelength = handle["/PHOENIX_SPECTRUM/wl"][()] * 1e-4  # micron
        flux = 10.0 ** handle["/PHOENIX_SPECTRUM/flux"][()]  # erg s^-1 cm^-2 cm^-1

    flux *= 1e-7  # erg s^-1 cm^-2 nm^-1

    mask = (wavelength >= planet_wavelength.min()) & (
        wavelength <= planet_wavelength.max()
    )
    wavelength = wavelength[mask]
    flux = flux[mask]

    sigma = (1.0 / resolution) / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    spacing = np.mean(2.0 * np.diff(wavelength) / (wavelength[1:] + wavelength[:-1]))
    flux_broad = gaussian_filter1d(flux, sigma / spacing)

    flux_resampled = np.interp(planet_wavelength, wavelength, flux_broad)

    rsun_to_cm = u.Rsun.to(u.cm)
    pc_to_cm = u.pc.to(u.cm)
    dilution_factor = (1.0 * rsun_to_cm) ** 2 / (distance_pc * pc_to_cm) ** 2
    return flux_resampled * dilution_factor


def fit_forward_model(
    data: np.ndarray,
    star_template: np.ndarray,
    planet_template: np.ndarray | None = None,
    n_knots: int = N_KNOTS,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]:
    """Return amplitudes, forward model, and star/planet contributions."""
    spline_components = SplineModel(n_knots=n_knots)(star_template)
    inverse_variance = np.ones_like(data)

    if planet_template is None:
        amplitudes = solve_linear(data, inverse_variance, spline_components)
        starlight_contribution = amplitudes @ spline_components
        planet_amplitude = 0.0
        planet_contribution = np.zeros_like(data)
        return amplitudes, starlight_contribution, planet_amplitude, planet_contribution, starlight_contribution

    design_matrix = np.vstack([spline_components, planet_template[np.newaxis, :]])
    amplitudes = solve_linear(data, inverse_variance, design_matrix)
    starlight_contribution = amplitudes[:-1] @ spline_components
    planet_amplitude = float(amplitudes[-1])
    planet_contribution = planet_amplitude * planet_template
    forward_model = starlight_contribution + planet_contribution
    return amplitudes, forward_model, planet_amplitude, planet_contribution, starlight_contribution


def plot_recovery_dashboard(
    wavelength: np.ndarray,
    *,
    nrs: str,
    detector: int,
    star_signal: np.ndarray,
    injected_companion: np.ndarray,
    fringes: np.ndarray,
    star_fringed: np.ndarray,
    forward_star: np.ndarray,
    signal: np.ndarray,
    signal_fringed: np.ndarray,
    forward_model: np.ndarray,
    starlight_contribution: np.ndarray,
    planet_contribution: np.ndarray,
    planet_amplitude: float,
    finite: np.ndarray,
    n_knots: int,
    planet_plot_scale = 100.0
) -> plt.Figure:
    """Multi-panel GridSpec figure for injection and recovery diagnostics."""
    lw = 0.9
    wl = wavelength
    wl_f = wavelength[finite]

    starlight_subtracted = signal_fringed - starlight_contribution
    expected_planet_fringed = injected_companion * fringes
    fringe_recovery_residual = star_fringed - forward_star
    planet_recovery_residual = planet_contribution[finite] - expected_planet_fringed[finite]

    fig = plt.figure(figsize=(12, 13))
    gs = fig.add_gridspec(
        4,
        2,
        height_ratios=[1.15, 0.85, 1.15, 1.15],
        width_ratios=[1.0, 1.0],
        hspace=0.38,
        wspace=0.22,
    )

    # --- Row 0: pre-fringe signal and components --------------------------------
    ax_pre = fig.add_subplot(gs[0, :])
    ax_pre.plot(wl, signal, color="k", lw=lw, label="Total (star + planet)")
    ax_pre.plot(wl, star_signal, color="orangered", lw=lw, alpha=0.85, label="Star (PSF suppressed)")
    ax_pre.plot(wl, injected_companion * planet_plot_scale, color="tab:green", lw=lw, alpha=0.85, label=f"Planet x {planet_plot_scale}")
    ax_pre.set_ylabel("Flux (pre-fringe)")
    ax_pre.set_title("Combined spectrum before fringing")
    ax_pre.legend(loc="upper right", frameon=False, ncol=3, fontsize=9)

    # --- Row 1: fringe pattern | before vs after fringing -----------------------
    ax_fringe = fig.add_subplot(gs[1, 0])
    ax_fringe.plot(wl, fringes, color="orangered", lw=lw)
    ax_fringe.axhline(1.0, color="gray", ls=":", lw=0.8)
    ax_fringe.set_ylabel(r"$B_\lambda$")
    ax_fringe.set_title("Injected IFU fringe pattern")

    ax_ba = fig.add_subplot(gs[1, 1], sharex=ax_fringe)
    ax_ba.plot(wl, signal, color="slategray", lw=lw, alpha=0.8, label="Before fringing")
    ax_ba.plot(wl, signal_fringed, color="k", lw=lw, alpha=0.85, label="After fringing")
    ax_ba.set_ylabel("Flux")
    ax_ba.set_title("Effect of fringing on combined signal")
    ax_ba.legend(loc="upper right", frameon=False, fontsize=9)
    plt.setp(ax_fringe.get_xticklabels(), visible=False)
    plt.setp(ax_ba.get_xticklabels(), visible=False)

    # --- Row 2: star-only fringe model recovery ---------------------------------
    ax_star = fig.add_subplot(gs[2, :])
    ax_star.plot(wl, star_fringed, color="k", lw=lw, label="Star x fringes (data)")
    ax_star.plot(wl, forward_star, color="royalblue", lw=1.2, label=f"Spline fringe model ($N_k$={n_knots})")
    ax_star_r = ax_star.twinx()
    ax_star_r.plot(wl, fringe_recovery_residual, color="tab:purple", lw=0.8, alpha=0.7, label="Recovery residual")
    ax_star_r.axhline(0.0, color="gray", ls=":", lw=0.8)
    ax_star_r.set_ylabel("Fringe residual", color="tab:purple")
    ax_star_r.tick_params(axis="y", labelcolor="tab:purple")
    ax_star.set_ylabel("Flux")
    ax_star.set_title("Starlight fringe-model recovery")
    lines_l, labels_l = ax_star.get_legend_handles_labels()
    lines_r, labels_r = ax_star_r.get_legend_handles_labels()
    ax_star.legend(lines_l + lines_r, labels_l + labels_r, loc="upper right", frameon=False, fontsize=9)
    plt.setp(ax_star.get_xticklabels(), visible=False)

    # --- Row 3: forward model | planet after starlight subtraction --------------
    ax_fwd = fig.add_subplot(gs[3, 0])
    ax_fwd.plot(wl, signal_fringed, color="k", lw=lw, alpha=0.75, label="Fringed data")
    ax_fwd.plot(wl, forward_model, color="royalblue", lw=1.1, label="Joint forward model")
    ax_fwd.plot(wl, starlight_contribution, color="orangered", lw=0.9, ls="--", alpha=0.85, label="Starlight term")
    ax_fwd.plot(
        wl,
        planet_contribution,
        color="tab:green",
        lw=0.9,
        ls="--",
        alpha=0.85,
        label=f"Planet term (amp={planet_amplitude:.2f})",
    )
    ax_fwd.set_xlabel("Wavelength [µm]")
    ax_fwd.set_ylabel("Flux")
    ax_fwd.set_title("Fringed-data forward model")
    ax_fwd.legend(loc="upper right", frameon=False, fontsize=8)

    ax_planet = fig.add_subplot(gs[3, 1], sharex=ax_fwd)
    ax_planet.plot(wl_f, starlight_subtracted[finite], color="k", lw=lw, alpha=0.8, label="Data − starlight")
    ax_planet.plot(wl_f, planet_contribution[finite], color="royalblue", lw=1.1, label="Best-fit planet model")
    ax_planet.plot(
        wl_f,
        expected_planet_fringed[finite],
        color="tab:green",
        lw=0.9,
        ls="--",
        alpha=0.85,
        label="Injected planet x fringes",
    )
    
    residuals = planet_contribution[finite] - expected_planet_fringed[finite]
    rms = np.sqrt(np.mean(residuals**2))
    ax_planet.plot(wl_f, residuals, color="tab:purple", lw=0.8, alpha=0.75, label=f"Planet recovery residual (RMS={rms:.3e})")
    ax_planet.axhline(0.0, color="gray", ls=":", lw=0.8)
   
    ax_planet.set_xlabel("Wavelength [µm]")
    ax_planet.set_ylabel("Flux after star subtraction")
    ax_planet.set_title("Planet recovery after starlight subtraction")
    lines_l, labels_l = ax_planet.get_legend_handles_labels()
    ax_planet.legend(lines_l, labels_l, loc="upper left", frameon=False, fontsize=8)
    return fig


def main(detector: int = DEFAULT_DETECTOR) -> None:
    planet_wavelength, planet_flux = load_planet_spectrum(detector=detector)
    finite = np.isfinite(planet_flux)
    nrs = detector_label(detector)

    star_template = load_star_template(planet_wavelength)
    star_signal = star_template / PSF_FLUX_SUPPRESSION
    fringes = build_ifu_fringes(
        planet_wavelength,
        amplitude=FRINGE_AMPLITUDE,
        period_pix=FRINGE_PERIOD_PIX,
        sinc_scale=FRINGE_SINC_SCALE,
    )

    star_file = DATA_DIR / PHOENIX_H5.name.replace(".h5", f"_{nrs}.txt")
    np.savetxt(
        star_file,
        np.column_stack((planet_wavelength, star_template)),
        header=f"wavelength [um] flux [erg s^-1 cm^-2 nm^-1] ({nrs})",
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(planet_wavelength, planet_flux * 1e4, label="Planet spectrum x 10^4")
    ax.plot(planet_wavelength, star_template, label="Diluted host-star template")
    ax.set_xlabel("Wavelength [um]")
    ax.set_ylabel("Flux [erg s^-1 cm^-2 nm^-1]")
    ax.set_title(f"{nrs} (λ {'<' if detector == 1 else '≥'} {DETECTOR_SPLIT_UM} µm)")
    ax.legend()
    fig.tight_layout()
    fig_name = f"broadened_and_resampled_phoenix_spectrum_{nrs}.pdf"
    fig.savefig(fig_name, dpi=200, bbox_inches="tight")
    print(f"Saved {fig_name}")
    print(f"Using {nrs}: {planet_wavelength.size} pixels, "
          f"{planet_wavelength.min():.3f}–{planet_wavelength.max():.3f} µm")

    # -----------------------------------------------------------------------
    # 1) Star-only fringe recovery (validates spline forward model)
    # -----------------------------------------------------------------------
    star_fringed = star_signal * fringes
    _, forward_star, _, _, _ = fit_forward_model(star_fringed, star_template)
    fringe_residual = star_fringed - forward_star
    fringe_rms = np.sqrt(np.mean(fringe_residual**2))

    # -----------------------------------------------------------------------
    # 2) Star + companion + fringes, with planet in the linear model
    # -----------------------------------------------------------------------
    injected_companion = planet_flux * COMPANION_DEMO_SCALE
    signal = star_signal + injected_companion
    signal_fringed = signal * fringes
    planet_template = np.nan_to_num(planet_flux, nan=0.0)

    (
        _,
        forward_model,
        planet_amplitude,
        planet_contribution,
        starlight_contribution,
    ) = fit_forward_model(signal_fringed, star_template, planet_template)

    expected_companion = injected_companion * fringes
    model_residual = signal_fringed - forward_model
    companion_residual = planet_contribution[finite] - expected_companion[finite]
    companion_rms = np.sqrt(np.mean(companion_residual**2))
    expected_rms = np.sqrt(np.mean(expected_companion[finite] ** 2))

    print(f"Fringe fit RMS ({nrs}): {fringe_rms:.3e} ({100 * fringe_rms / np.std(star_fringed):.2f}% of star std)")
    print(f"Recovered planet amplitude: {planet_amplitude:.4f}")
    print(f"Injected companion scale: {COMPANION_DEMO_SCALE:.4f}")
    print(f"Planet contribution RMS: {np.sqrt(np.mean(planet_contribution[finite]**2)):.3e}")
    print(f"Planet model vs injected RMS: {companion_rms:.3e} ({companion_rms / expected_rms:.2%} of injected)")
    print(f"Full forward-model residual RMS: {np.sqrt(np.mean(model_residual**2)):.3e}")

    fig = plot_recovery_dashboard(
        planet_wavelength,
        nrs=nrs,
        detector=detector,
        star_signal=star_signal,
        injected_companion=injected_companion,
        fringes=fringes,
        star_fringed=star_fringed,
        forward_star=forward_star,
        signal=signal,
        signal_fringed=signal_fringed,
        forward_model=forward_model,
        starlight_contribution=starlight_contribution,
        planet_contribution=planet_contribution,
        planet_amplitude=planet_amplitude,
        finite=finite,
        n_knots=N_KNOTS,
    )
    fig.tight_layout()
    fig_name = f"high_contrast_fringe_recovery_{nrs}.pdf"
    fig.savefig(fig_name, dpi=200, bbox_inches="tight")
    print(f"Saved {fig_name}")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate IFU fringing and recover companion spectrum.")
    parser.add_argument(
        "--detector",
        type=int,
        default=DEFAULT_DETECTOR,
        choices=[1, 2],
        help="NIRSpec detector: 1=NRS1 (λ < 4.1 µm), 2=NRS2 (λ ≥ 4.1 µm)",
    )
    args = parser.parse_args()
    main(detector=args.detector)
