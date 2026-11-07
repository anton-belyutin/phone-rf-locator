from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv
import json

import numpy as np
from PIL import Image, ImageDraw


@dataclass(frozen=True)
class DetectionConfig:
    nfft: int = 2048
    hop: int = 512
    noise_percentile: float = 25.0
    smoothing_bins: int = 41
    min_excess_db: float = 7.0
    adaptive_sigma: float = 6.0
    min_frames: int = 3
    max_gap_frames: int = 2


@dataclass(frozen=True)
class Event:
    start_s: float
    end_s: float
    peak_s: float
    peak_frequency_hz: float
    peak_offset_hz: float
    peak_excess_db: float


@dataclass
class DetectionResult:
    events: list[Event]
    threshold_db: float
    frame_times_s: np.ndarray
    frequencies_hz: np.ndarray
    excess_db: np.ndarray
    frame_score_db: np.ndarray


def _validate_iq(iq: np.ndarray, config: DetectionConfig) -> np.ndarray:
    values = np.asarray(iq)
    if values.ndim != 1 or not np.iscomplexobj(values):
        raise ValueError("iq must be a one-dimensional complex array")
    if config.nfft < 64 or config.hop < 1 or config.hop > config.nfft:
        raise ValueError("Require nfft >= 64 and 1 <= hop <= nfft")
    if values.size < config.nfft:
        raise ValueError("The capture is shorter than one FFT frame")
    return values.astype(np.complex64, copy=False)


def _stft_power_db(iq: np.ndarray, config: DetectionConfig) -> np.ndarray:
    starts = np.arange(0, iq.size - config.nfft + 1, config.hop, dtype=np.int64)
    window = np.hanning(config.nfft).astype(np.float32)
    window_power = float(np.sum(window * window))
    output = np.empty((starts.size, config.nfft), dtype=np.float32)
    offsets = np.arange(config.nfft, dtype=np.int64)

    for batch_start in range(0, starts.size, 256):
        batch_starts = starts[batch_start : batch_start + 256]
        frames = iq[batch_starts[:, None] + offsets[None, :]] * window
        spectrum = np.fft.fftshift(np.fft.fft(frames, axis=1), axes=1)
        power = (np.abs(spectrum) ** 2) / max(window_power, 1e-20)
        output[batch_start : batch_start + batch_starts.size] = 10.0 * np.log10(
            power + 1e-20
        )
    return output


def _frequency_smooth(values: np.ndarray, bins: int) -> tuple[np.ndarray, int]:
    width = max(1, min(int(bins), values.shape[1]))
    if width % 2 == 0 and width > 1:
        width -= 1
    if width == 1:
        return values, 0
    prefix = np.concatenate(
        [np.zeros((values.shape[0], 1), dtype=np.float32), np.cumsum(values, axis=1)],
        axis=1,
    )
    smoothed = (prefix[:, width:] - prefix[:, :-width]) / float(width)
    return smoothed, width // 2


def _merge_active_frames(
    active: np.ndarray, min_frames: int, max_gap_frames: int
) -> list[tuple[int, int]]:
    hits = np.flatnonzero(active)
    if hits.size == 0:
        return []
    groups: list[tuple[int, int]] = []
    start = previous = int(hits[0])
    for hit in hits[1:]:
        current = int(hit)
        if current - previous - 1 > max_gap_frames:
            if previous - start + 1 >= min_frames:
                groups.append((start, previous))
            start = current
        previous = current
    if previous - start + 1 >= min_frames:
        groups.append((start, previous))
    return groups


def detect_bursts(
    iq: np.ndarray,
    sample_rate_hz: float,
    center_frequency_hz: float,
    config: DetectionConfig | None = None,
) -> DetectionResult:
    cfg = config or DetectionConfig()
    values = _validate_iq(iq, cfg)
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")

    power_db = _stft_power_db(values, cfg)
    noise_floor = np.percentile(power_db, cfg.noise_percentile, axis=0)
    excess_db = power_db - noise_floor[None, :]
    smoothed, edge = _frequency_smooth(excess_db, cfg.smoothing_bins)
    score = np.max(smoothed, axis=1)
    median = float(np.median(score))
    mad_sigma = 1.4826 * float(np.median(np.abs(score - median)))
    threshold = max(cfg.min_excess_db, median + cfg.adaptive_sigma * max(mad_sigma, 0.15))
    active = score >= threshold

    frame_times = (np.arange(power_db.shape[0]) * cfg.hop + cfg.nfft / 2) / sample_rate_hz
    full_frequencies = center_frequency_hz + np.fft.fftshift(
        np.fft.fftfreq(cfg.nfft, d=1.0 / sample_rate_hz)
    )
    frequencies = full_frequencies[edge : cfg.nfft - edge] if edge else full_frequencies

    events: list[Event] = []
    for start_frame, end_frame in _merge_active_frames(
        active, cfg.min_frames, cfg.max_gap_frames
    ):
        local = smoothed[start_frame : end_frame + 1]
        local_peak = int(np.argmax(local))
        time_index, frequency_index = np.unravel_index(local_peak, local.shape)
        peak_frame = start_frame + int(time_index)
        peak_frequency = float(frequencies[frequency_index])
        events.append(
            Event(
                start_s=max(0.0, start_frame * cfg.hop / sample_rate_hz),
                end_s=(end_frame * cfg.hop + cfg.nfft) / sample_rate_hz,
                peak_s=float(frame_times[peak_frame]),
                peak_frequency_hz=peak_frequency,
                peak_offset_hz=peak_frequency - center_frequency_hz,
                peak_excess_db=float(local[time_index, frequency_index]),
            )
        )

    return DetectionResult(
        events=events,
        threshold_db=float(threshold),
        frame_times_s=frame_times,
        frequencies_hz=full_frequencies,
        excess_db=excess_db,
        frame_score_db=score,
    )


def save_events(
    result: DetectionResult,
    output_dir: str | Path,
    sample_rate_hz: float,
    center_frequency_hz: float,
) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "events.json"
    csv_path = directory / "events.csv"
    payload = {
        "sample_rate_hz": sample_rate_hz,
        "center_frequency_hz": center_frequency_hz,
        "threshold_db": result.threshold_db,
        "event_count": len(result.events),
        "events": [asdict(event) for event in result.events],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(Event(0, 0, 0, 0, 0, 0)).keys()))
        writer.writeheader()
        writer.writerows(asdict(event) for event in result.events)
    return json_path, csv_path


def save_spectrogram(
    result: DetectionResult,
    path: str | Path,
    center_frequency_hz: float,
) -> Path:
    """Save a dependency-light diagnostic spectrogram using Pillow."""
    clipped = np.clip((result.excess_db + 2.0) / 20.0, 0.0, 1.0)
    low = np.stack(
        [8 + 10 * clipped, 18 + 180 * clipped, 45 + 180 * clipped], axis=-1
    )
    high_mask = clipped > 0.65
    high = (clipped - 0.65) / 0.35
    low[..., 0] = np.where(high_mask, 18 + 237 * high, low[..., 0])
    low[..., 1] = np.where(high_mask, 198 + 57 * high, low[..., 1])
    low[..., 2] = np.where(high_mask, 225 - 205 * high, low[..., 2])
    rgb = np.clip(low, 0, 255).astype(np.uint8).transpose(1, 0, 2)[::-1]

    plot_width, plot_height = 1200, 620
    left, top, right, bottom = 92, 35, 25, 65
    plot = Image.fromarray(rgb, mode="RGB").resize(
        (plot_width, plot_height), Image.Resampling.BILINEAR
    )
    canvas = Image.new("RGB", (left + plot_width + right, top + plot_height + bottom), "white")
    canvas.paste(plot, (left, top))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((left, top, left + plot_width, top + plot_height), outline="black", width=1)

    duration = float(result.frame_times_s[-1]) if result.frame_times_s.size else 1.0
    for event in result.events:
        x = left + int(plot_width * event.peak_s / max(duration, 1e-12))
        draw.line((x, top, x, top + plot_height), fill=(255, 70, 60), width=2)

    low_mhz = result.frequencies_hz[0] / 1e6
    high_mhz = result.frequencies_hz[-1] / 1e6
    draw.text((left, 8), f"RF burst detector | center {center_frequency_hz / 1e6:.3f} MHz", fill="black")
    draw.text((left, top + plot_height + 12), "0 s", fill="black")
    draw.text((left + plot_width - 75, top + plot_height + 12), f"{duration:.3f} s", fill="black")
    draw.text((8, top), f"{high_mhz:.3f} MHz", fill="black")
    draw.text((8, top + plot_height - 12), f"{low_mhz:.3f} MHz", fill="black")
    draw.text((left + 410, top + plot_height + 38), "time | red = detected event", fill="black")

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    return output
