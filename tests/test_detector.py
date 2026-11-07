import unittest

import numpy as np

from rf_poc.detector import DetectionConfig, detect_bursts
from rf_poc.simulate import DEFAULT_BURSTS, simulate_iq


class DetectorTests(unittest.TestCase):
    def test_detects_all_synthetic_bursts_near_expected_times(self) -> None:
        iq, metadata = simulate_iq()
        result = detect_bursts(
            iq,
            metadata["sample_rate_hz"],
            metadata["center_frequency_hz"],
        )
        self.assertEqual(len(result.events), len(DEFAULT_BURSTS))
        for detected, expected in zip(result.events, DEFAULT_BURSTS):
            self.assertLessEqual(detected.start_s, expected.start_s + 0.006)
            self.assertGreaterEqual(detected.end_s, expected.end_s - 0.006)
            # A noise-like burst has no single carrier: its strongest FFT bin may
            # occur anywhere inside the simulated ~180 kHz occupied bandwidth.
            self.assertLess(abs(detected.peak_offset_hz - expected.offset_hz), 120_000.0)

    def test_rejects_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            detect_bursts(np.ones(4096), 1_000_000.0, 900_000_000.0)

    def test_short_noise_capture_has_no_long_event(self) -> None:
        rng = np.random.default_rng(4)
        noise = (
            rng.standard_normal(150_000) + 1j * rng.standard_normal(150_000)
        ).astype(np.complex64)
        result = detect_bursts(
            noise,
            1_000_000.0,
            900_000_000.0,
            DetectionConfig(min_frames=5, adaptive_sigma=7.0),
        )
        self.assertEqual(result.events, [])


if __name__ == "__main__":
    unittest.main()
