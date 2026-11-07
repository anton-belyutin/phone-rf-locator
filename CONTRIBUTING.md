# Contributing

This repository is an open handoff, not a claim that the concept already works. Contributions are most useful when they improve reproducibility or reduce uncertainty.

## Useful contributions

- independent synthetic or bench-test reproduction;
- receive-only capture support for documented SDR hardware;
- detector calibration and false-positive analysis;
- privacy-safe real-phone measurements;
- antenna and receiver-chain characterization;
- negative results with complete settings;
- corrections to technical, legal or aviation assumptions.

## Before opening a pull request

1. Keep all functionality receive-only.
2. Do not add traffic decoding, identifier extraction, base-station emulation, spoofing or jamming.
3. Run `python -m unittest discover -s tests -v`.
4. Document hardware, software versions and test conditions.
5. Use only owned or explicitly consented devices.
6. Remove secrets, personal locations and identifiable third-party captures.

For measurements, copy [the experiment report template](docs/EXPERIMENT_REPORT_TEMPLATE.md) into a new Markdown file and attach only data that is safe and lawful to publish.

## Discussion

When proposing a major change, explain which uncertainty it addresses and what result would falsify the hypothesis. A well-documented No-Go result is welcome.

