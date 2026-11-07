# Experiment report template

Use one report per measurement session. Leave unknown values blank rather than guessing.

## Metadata

- Date and local time:
- Country / test location type:
- Experimenter:
- Consent basis for every tested device:
- SDR model and serial alias:
- SDR firmware / driver / capture software:
- Antenna model and orientation:
- Cable, filter, attenuator and LNA chain:
- Laptop / operating system:
- Phone model and modem family:
- SIM / operator state:
- Shielded enclosure or test geometry:

## Receiver settings

| Run | Center frequency | Sample rate | Analog bandwidth | Gain mode/value | Duration | Notes |
|---|---:|---:|---:|---:|---:|---|
| 1 | | | | | | |

## Scenario matrix

Repeat each scenario at least ten times where practical.

| Scenario | Phone state | Screen | Cellular | Wi-Fi | Bluetooth | Expected control |
|---|---|---|---|---|---|---|
| Empty setup | absent | - | - | - | - | noise baseline |
| Powered off | off | off | off | off | off | no phone transmission |
| Boot | booting | varies | varies | varies | varies | activity possible |
| Normal service | idle | off | registered | defined | defined | reference |
| No service | idle | off | not registered | defined | defined | critical scenario |

## Results

| Scenario | Repeats | Runs with events | False events | Median excess over noise | Longest silence | Notes |
|---|---:|---:|---:|---:|---:|---|
| | | | | | | |

Attach detector configuration, event CSV/JSON, plots and checksums for any shared capture files.

## Conclusion

- Go / No-Go / Inconclusive:
- Predefined criterion used:
- Alternative explanations:
- What must be repeated independently:
- Safety or privacy observations:

