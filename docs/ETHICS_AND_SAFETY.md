# Ethics and safety boundary

Phone RF Locator is published for civilian search-and-rescue research. The repository is deliberately limited to anonymous, receive-only signal detection.

## Allowed scope

- Bench and field tests involving devices owned by the experimenter or used with explicit informed consent.
- Passive spectrum observation where permitted by local law.
- Energy, timing and bandwidth measurements that do not decode content or identifiers.
- Publication of synthetic data and privacy-safe aggregate measurements.
- Cooperative trials with a rescue organization and a documented test protocol.

## Out of scope

- Tracking non-consenting people or devices.
- Extracting IMSI, IMEI, MAC addresses, subscriber data, message content or other identifiers.
- Demodulating private communications.
- Cellular base-station emulation, IMSI catching, spoofing or protocol manipulation.
- Jamming or deliberate interference.
- Military targeting, surveillance or coercive use.
- Airborne tests without appropriate operator, airspace and payload authorization.

## Data minimization

Store only the frequency window, receiver settings, timestamp, receiver position when required, anonymized scenario label and derived event metrics. Do not publish precise personal locations or raw captures that may contain identifiable third-party traffic unless an appropriate review shows that publication is lawful and privacy-safe.

## Responsible development

Every experiment should state its jurisdiction, equipment, consent basis, safety controls and retention policy. Stop a test if unexpected transmissions, unsafe RF levels, unstable aircraft behavior or privacy concerns arise.

