# Low-cost PoC equipment in Europe

> Price snapshot: 7 November 2026. The figures are planning ranges for European retail purchases, not quotations. VAT, shipping and local availability vary by country. USD values use the ECB reference rate for 6 November 2026: **EUR 1 = USD 1.1165**. A laptop and test phone are not included.

## Recommended kit

| Priority | Item | Minimum requirement | Approx. Europe price | Approx. USD |
|---|---|---|---:|---:|
| Required | SDR | Original `ADALM-PLUTO`, 325-3800 MHz, USB | €225-275 | $251-307 |
| Required | TX termination | SMA male, 50 ohm, frequency range covering at least DC-3.8 GHz | €4-6 | $4-7 |
| Required | Receive antenna | 50 ohm, SMA, suitable for the selected 700-2700 MHz windows | €5-15 | $6-17 |
| Required | SMA cables and adapters | Short 50-ohm RF assemblies with verified connector genders | €15-35 | $17-39 |
| Required | Shielded enclosure materials | Metal box, conductive tape and SMA bulkhead | €25-60 | $28-67 |
| Optional | 20-30 dB attenuator | SMA, 50 ohm, at least DC-3 GHz, for cabled calibration | €22-30 | $25-34 |
| As needed | Quality USB cable | Start with the supplied cable | €0-15 | $0-17 |

### Planning total

- **Practical original-ADALM-Pluto bench kit:** approximately **€320-420 / $357-469**, including a VAT and shipping allowance.
- **If the SDR is already available:** approximately **€50-120 / $56-134** for the remaining bench hardware.
- Compatible Pluto/Pluto+ boards can reduce the total, but they may differ in RF design, clock quality, firmware and software compatibility. Do not budget them as an original ADALM-Pluto without checking the exact revision.

## Current price references

### ADALM-Pluto

DigiKey Europe listed the original Analog Devices `ADALM-PLUTO` at about **€222-225 excluding VAT**, or roughly **€269-275 including country-dependent VAT**:

- https://www.digikey.be/en/products/detail/analog-devices-inc/ADALM-PLUTO/6624230
- https://www.digikey.it/it/products/detail/analog-devices-inc/ADALM-PLUTO/ADALM-PLUTO-ND/6624230

Mouser Europe showed a similar pre-VAT price, but its product page also warned that the item may be restricted to OEM/EMS and design-business customers in the EU and UK:

https://www.mouser.lu/en/ProductDetail/Analog-Devices/ADALM-PLUTO

### 50-ohm TX termination

The Amphenol RF `132360` SMA male 50-ohm termination was listed by DigiKey Germany at about **€4-5 including VAT**. Reichelt listed comparable SMA 50-ohm terminations at about **€5.70-5.75 including VAT**:

- https://www.digikey.de/en/products/detail/amphenol-rf/132360/1011928
- https://www.reichelt.de/de/de/shop/produkt/sma_abschlusswiderstand_50_ohm-280454

### Wideband receive antenna

The TE Connectivity Linx `ANT-5GWWS6-SMA`, covering 617 MHz to 6 GHz in multiple bands, was listed by DigiKey Germany at about **€4.50 before VAT / €5.30 with German VAT**:

https://www.digikey.de/en/products/detail/te-connectivity-linx/ANT-5GWWS6-SMA/16893432

### Optional attenuator

The Mini-Circuits `VAT-30A+` 30 dB, DC-6 GHz, 50-ohm attenuator was listed at about **€21.60 before VAT / €26.20 with Belgian VAT**:

https://www.digikey.be/fr/products/detail/mini-circuits/VAT-30A/19186461

### Exchange rate

The USD conversions use the European Central Bank reference rate published for 6 November 2026:

https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html

## Buy first

1. The SDR.
2. A proper 50-ohm termination for the unused TX port.
3. Only the SMA cables and adapters required by the chosen antenna.
4. Shielded-enclosure materials.
5. An additional antenna only if the supplied antennas do not cover the selected window or are impractical for the fixture.

## Do not buy yet

- Jetson, Raspberry Pi or another embedded computer; a laptop is sufficient for Stage 0.
- KrakenSDR or an expensive coherent array before useful phone transmissions are demonstrated.
- A generic wideband LNA; without band filtering it may reduce usable dynamic range.
- GNSS, IMU or airborne packaging before the bench Go/No-Go result.
- Any mount for DJI Avata 2; it is not the selected payload platform.
- Transmit amplifiers, interference generators or jammers.

## Receiving checklist

1. Verify the manufacturer part number and package contents.
2. Fit the 50-ohm load to TX.
3. Install the official driver and `libiio`.
4. Confirm USB detection.
5. Make a short receive-only capture with the supplied antenna.
6. Check for overheating and USB disconnects.
7. Do not run transmit code.

