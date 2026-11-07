from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

import numpy as np

from .detector import DetectionConfig, detect_bursts, save_events, save_spectrogram
from .simulate import save_simulation


def _load_capture(path: Path) -> tuple[np.ndarray, float, float]:
    with np.load(path) as data:
        required = {"iq", "sample_rate_hz", "center_frequency_hz"}
        missing = required.difference(data.files)
        if missing:
            raise ValueError(f"Missing NPZ fields: {', '.join(sorted(missing))}")
        return (
            np.asarray(data["iq"]),
            float(np.asarray(data["sample_rate_hz"])),
            float(np.asarray(data["center_frequency_hz"])),
        )


def _detect(input_path: Path, output_dir: Path, args: argparse.Namespace) -> int:
    iq, sample_rate_hz, center_frequency_hz = _load_capture(input_path)
    config = DetectionConfig(
        nfft=args.nfft,
        hop=args.hop,
        smoothing_bins=args.smoothing_bins,
        min_excess_db=args.min_excess_db,
    )
    result = detect_bursts(iq, sample_rate_hz, center_frequency_hz, config)
    json_path, csv_path = save_events(
        result, output_dir, sample_rate_hz, center_frequency_hz
    )
    image_path = save_spectrogram(
        result, output_dir / "spectrogram.png", center_frequency_hz
    )
    print(f"Detected {len(result.events)} event(s); threshold={result.threshold_db:.2f} dB")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print(f"PNG:  {image_path}")
    for index, event in enumerate(result.events, start=1):
        print(
            f"  {index}: {event.start_s:.6f}-{event.end_s:.6f} s, "
            f"peak offset={event.peak_offset_hz / 1e3:+.1f} kHz, "
            f"excess={event.peak_excess_db:.1f} dB"
        )
    return 0


def _add_detector_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--nfft", type=int, default=2048)
    parser.add_argument("--hop", type=int, default=512)
    parser.add_argument("--smoothing-bins", type=int, default=41)
    parser.add_argument("--min-excess-db", type=float, default=7.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Receive-only RF burst PoC")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="write a synthetic I/Q capture")
    simulate.add_argument("output", type=Path)
    simulate.add_argument("--sample-rate", type=float, default=2_400_000.0)
    simulate.add_argument("--center-frequency", type=float, default=900_000_000.0)
    simulate.add_argument("--duration", type=float, default=0.55)

    detect = subparsers.add_parser("detect", help="detect bursts in an NPZ capture")
    detect.add_argument("input", type=Path)
    detect.add_argument("--output-dir", type=Path, required=True)
    _add_detector_options(detect)

    demo = subparsers.add_parser("demo", help="run simulation and detection")
    demo.add_argument("output_dir", type=Path)
    _add_detector_options(demo)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "simulate":
        path, bursts = save_simulation(
            args.output,
            sample_rate_hz=args.sample_rate,
            center_frequency_hz=args.center_frequency,
            duration_s=args.duration,
        )
        print(f"Saved {path} with {len(bursts)} synthetic bursts")
        return 0

    if args.command == "detect":
        return _detect(args.input, args.output_dir, args)

    with tempfile.TemporaryDirectory(prefix="rf-poc-") as temporary:
        capture = Path(temporary) / "synthetic.npz"
        save_simulation(capture)
        status = _detect(capture, args.output_dir, args)
        shutil.copy2(capture, args.output_dir / "synthetic_iq.npz")
        return status


if __name__ == "__main__":
    raise SystemExit(main())
