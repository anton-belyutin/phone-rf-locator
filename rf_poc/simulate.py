from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class SimulatedBurst:
    start_s: float
    end_s: float
    offset_hz: float
    snr_db: float


DEFAULT_BURSTS = (
    SimulatedBurst(0.080, 0.125, -360_000.0, 15.0),
    SimulatedBurst(0.245, 0.292, 170_000.0, 12.0),
    SimulatedBurst(0.405, 0.462, 510_000.0, 17.0),
)


def _band_limited_noise(
    length: int, sample_rate_hz: float, bandwidth_hz: float, rng: np.random.Generator
) -> np.ndarray:
    """Create unit-RMS complex noise with a simple windowed-sinc low-pass FIR."""
    taps_count = 65
    cutoff = min(0.45, bandwidth_hz / sample_rate_hz)
    n = np.arange(taps_count, dtype=np.float64) - (taps_count - 1) / 2
    taps = 2 * cutoff * np.sinc(2 * cutoff * n) * np.hanning(taps_count)
    taps /= np.sum(taps)
    raw = (
        rng.standard_normal(length + taps_count - 1)
        + 1j * rng.standard_normal(length + taps_count - 1)
    ) / np.sqrt(2.0)
    filtered = np.convolve(raw, taps, mode="valid")
    rms = np.sqrt(np.mean(np.abs(filtered) ** 2))
    return filtered / max(rms, 1e-12)


def simulate_iq(
    sample_rate_hz: float = 2_400_000.0,
    center_frequency_hz: float = 900_000_000.0,
    duration_s: float = 0.55,
    seed: int = 20260912,
    bursts: tuple[SimulatedBurst, ...] = DEFAULT_BURSTS,
) -> tuple[np.ndarray, dict[str, float]]:
    """Generate noise plus wideband, noise-like RF bursts for an end-to-end test."""
    rng = np.random.default_rng(seed)
    samples = int(round(sample_rate_hz * duration_s))
    iq = (
        rng.standard_normal(samples) + 1j * rng.standard_normal(samples)
    ).astype(np.complex64) / np.sqrt(2.0)

    for burst in bursts:
        start = max(0, int(round(burst.start_s * sample_rate_hz)))
        end = min(samples, int(round(burst.end_s * sample_rate_hz)))
        if end <= start:
            continue
        length = end - start
        payload = _band_limited_noise(length, sample_rate_hz, 180_000.0, rng)
        t = np.arange(length, dtype=np.float64) / sample_rate_hz
        carrier = np.exp(2j * np.pi * burst.offset_hz * t)
        amplitude = 10.0 ** (burst.snr_db / 20.0)
        iq[start:end] += (amplitude * payload * carrier).astype(np.complex64)

    metadata = {
        "sample_rate_hz": float(sample_rate_hz),
        "center_frequency_hz": float(center_frequency_hz),
    }
    return iq, metadata


def save_simulation(path: str | Path, **kwargs: object) -> tuple[Path, tuple[SimulatedBurst, ...]]:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    iq, metadata = simulate_iq(**kwargs)
    np.savez_compressed(output, iq=iq, **metadata)
    return output, DEFAULT_BURSTS
