# GNSS Antenna Research for Septentrio Mosaic-G5 P3H (ARK G5 RTK Heading GPS)

**Date:** 2026-03-04  
**Purpose:** Select TWO multi-band GNSS antennas for dual-antenna GPS heading on a drone  
**Receiver:** Septentrio Mosaic-G5 P3H (quad-band single antenna / triple-band dual antenna mode)

---

## Receiver Context

The **Mosaic-G5 P3H** supports:
- **Single antenna mode:** Quad-band (L1/L2/L5/L-band)
- **Dual antenna mode (heading):** Triple-band (L1/L2/L5) — each antenna input uses 3 bands
- **Constellations:** GPS, GLONASS, Galileo, BeiDou, QZSS, SBAS
- **Connector:** SMA (on the ARK G5 board)

**Key requirement:** Antennas must support **L1 + L2 + L5** minimum for full dual-antenna heading performance.

---

## ARK G5 RTK Heading GPS — Included Antennas

The ARK G5 RTK Heading GPS ($820–$975 from [ARK Electronics](https://arkelectron.com/product/ark-g5-rtk-heading-gps/)) includes **"Full-Frequency Helical GPS Antennas"**.

Based on the GNSS.store listing (ELT0762) for the same Mosaic-G5 P3H module with helical antennas:
- **Type:** All-band compact helical antennas with integrated LNA
- **Weight:** ~34g each (per antenna + module combined = 34g total per GNSS.store ultraLight listing)
- **Gain:** 28 dB typ.
- **Axial ratio:** 3 dB max
- **These are likely the same or similar** to the helical antennas sold by ArduSimple/Holybro/GNSS.store — generic Chinese-made multi-band helical antennas (e.g., Holybro HANT-X622A or HANT-X623A equivalents)

⚠️ **NDAA concern:** The included helical antennas are very likely manufactured in China. If NDAA compliance is required for the entire system, replacement antennas from NDAA-compliant manufacturers should be sourced.

---

## Group A: Ultra-Light / Ultra-Small (Weight-Critical Drone Use)

### 1. Tallysman HC885EXF — Dual-Band Helical + L-Band
| Spec | Value |
|------|-------|
| **Bands** | L1/L5: GPS/QZSS-L1/L5, GLONASS-G1/G3, Galileo-E1/E5a/E5b, BeiDou-B1/B2/B2a, NavIC-L5 + L-Band |
| **Weight** | **8g** (embedded OEM version, no housing) |
| **Type** | Active helical, embedded |
| **NDAA** | ✅ **Manufactured in Ottawa, Canada** (Calian/Tallysman) |
| **Price** | ⚠️ Cannot verify retail price — contact Tallysman/Calian directly. Embedded OEM part, likely $100–200 range |
| **Purchase** | [Tallysman Product Page](https://www.tallysman.com/product/hc885exf-dual-band-helical-antenna-l-band/) |
| **Notes** | ⚠️ L1/L5 only (no L2). May not provide optimal performance for heading in dual-antenna L1/L2/L5 mode. Best for L1/L5 receivers. Embedded form factor requires integration. |

### 2. SparkFun SPK-6E — Tri-Band Helical
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5: GPS, GLONASS, Galileo, BeiDou |
| **Weight** | **18.1g** |
| **Dimensions** | ~15mm dia × ~65mm tall (helical, SMA male) |
| **Type** | Passive helical |
| **NDAA** | ⚠️ **Unknown manufacturer / likely China-made OEM.** SparkFun is US company but antenna origin unclear. |
| **Price** | **$119.95** ([SparkFun GPS-23847](https://www.sparkfun.com/gnss-multi-band-l1-l2-l5-helical-antenna-sma.html)) |
| **Purchase** | [SparkFun GPS-23847](https://www.sparkfun.com/gnss-multi-band-l1-l2-l5-helical-antenna-sma.html) |
| **Notes** | Passive antenna — no LNA. Excellent weight. Phase center at 37.5mm. Likely identical to common Chinese helical antennas. NDAA status uncertain. |

### 3. Maxtena M8HCT-A-SMA — Tri-Band Active Helical
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5: GPS, GLONASS, Galileo, BeiDou |
| **Weight** | **25g** |
| **Dimensions** | ~22mm dia × ~72mm tall (helical with SMA) |
| **Type** | Active quadrifilar helix, integrated LNA |
| **NDAA** | ✅ **Manufactured in USA** (Maxtena Inc., Rockville, MD) |
| **Price** | **~$370** (Newark/Farnell: $370.31 ea qty 1) |
| **Purchase** | [DigiKey](https://www.digikey.com/en/products/detail/maxtena-inc/M8HCT-A-SMA-100-00124-01/21816436) · [Newark](https://www.newark.com/maxtena/m8hct-a-sma/gnss-antenna-1-559-1-606ghz-0/dp/84AH0181) |
| **Notes** | IP67, ground plane independent, MIL-STD-810G rated. Premium USA-made antenna. Excellent for NDAA-compliant builds. Low axial ratio, low phase center variation. |

### 4. ArduSimple Compact Helical Tripleband + L-Band (IP67)
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5 + L-Band: GPS, GLONASS, Galileo, BeiDou |
| **Weight** | **21g** |
| **Dimensions** | Compact helical, SMA male |
| **Type** | Active helical |
| **NDAA** | ⚠️ **Likely NOT compliant** — probable Chinese OEM antenna (alternative to Holybro HANT-X623A) |
| **Price** | **€128 (~$139 USD)** |
| **Purchase** | [ArduSimple](https://www.ardusimple.com/product/compact-helical-gnss-tripleband-l-band-antenna-ip67/) |
| **Notes** | Compatible with Septentrio Mosaic. Great weight and price but NDAA status is a concern. ArduSimple is a European company but antenna origin is likely Chinese. |

### 5. ArduSimple Lightweight Helical Tripleband + L-Band (IP67)
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5 + L-Band: GPS, GLONASS, Galileo, BeiDou |
| **Weight** | **<35g** |
| **Dimensions** | Helical, SMA male |
| **Type** | Active helical |
| **NDAA** | ⚠️ **Likely NOT compliant** — probable Chinese OEM (alternative to Holybro HANT-X622A) |
| **Price** | **€146 (~$159 USD)** |
| **Purchase** | [ArduSimple](https://www.ardusimple.com/product/lightweight-helical-tripleband-l-band-antenna-ip67/) |
| **Notes** | Same concerns as above. Slightly heavier than compact version. |

---

## Group B: Best Value / Larger (Still Drone-Suitable)

### 1. Maxtena M9HCT-A-SMA — Tri-Band + L-Band Active Helical
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5 + L-Band: GPS, GLONASS, Galileo, BeiDou + L-Band correction services |
| **Weight** | ~30–35g (estimated, similar form factor to M8HCT) |
| **Dimensions** | ~22mm dia × ~80mm tall (helical with SMA) |
| **Type** | Active quadrifilar helix, integrated LNA |
| **NDAA** | ✅ **Manufactured in USA** (Maxtena Inc.) |
| **Price** | **~$370–450** (estimated similar to M8HCT; check DigiKey) |
| **Purchase** | [DigiKey](https://www.digikey.com/en/products/detail/maxtena-inc/M9HCT-A-SMA-100-00174-01/21816541) · [Maxtena](https://www.maxtena.com/Products/Antennas-Solutions/GNSS-antennas/Helical-GNSS-Antennas/Triple-bands-GNSS-Antennas/M9HCT-A-SMA) |
| **Notes** | Adds L-Band over M8HCT. O-ring sealed, IP67. Same Helicore® technology. Best option if you want L-Band PPP corrections. |

### 2. Maxtena M10HCT-A-SMA — All-Band Active Helical
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5 + L-Band: Full GPS, Galileo, GLONASS, BeiDou coverage (1164–1300 MHz, 1539–1610 MHz) |
| **Weight** | ~40–50g (estimated, low-profile design) |
| **Dimensions** | Low-profile RHCP helix |
| **Type** | Active, ground plane independent |
| **NDAA** | ✅ **Manufactured in USA** (Maxtena Inc.) |
| **Price** | ⚠️ Cannot verify price — likely $400–600 range. Contact Maxtena directly. |
| **Purchase** | [Maxtena](https://www.maxtena.com/Product/ViewDetail/262) · [Innovelec](https://innovelec.co.uk/products/maxtena-m10hct-a-sma-l1-l2-l5-active-gnss-antenna/) |
| **Notes** | Widest band coverage in Maxtena lineup. Designed for military/defense applications. Best match for G5's quad-band capability. |

### 3. Tallysman TW7972 — Triple-Band Patch + L-Band (Sold by Septentrio)
| Spec | Value |
|------|-------|
| **Bands** | L1/L2/L5 + L-Band: GPS/QZSS-L1/L2/L5, GLONASS-G1/G2/G3, Galileo-E1/E5a/E5b, BeiDou-B1/B2b/B2a + SBAS + L-Band |
| **Weight** | ~80g (with magnetic mount housing, IP67) |
| **Dimensions** | ~60mm dia × 20mm tall (dome/puck) |
| **Type** | Active patch, Accutenna® technology |
| **NDAA** | ✅ **Manufactured in Ottawa, Canada** (Calian/Tallysman) |
| **Price** | **~$250–350** (estimated; sold through DigiKey, Septentrio shop, NavtechGPS — contact for quote) |
| **Purchase** | [DigiKey 33-7972-07](https://www.digikey.com/en/products/detail/tallysman-wireless-inc/33-7972-07/9959589) · [Septentrio](https://www.septentrio.com/en/products/gps-gnss-antennas/tw7972) · [NavtechGPS](https://www.navtechgps.com/tw7972_triple_band_gnss_antenna/) |
| **Notes** | **Septentrio's recommended antenna.** Superior multipath rejection, excellent axial ratio, tight phase center variation. Magnetic mount (can be removed for drone mounting). This is the gold standard pairing for Septentrio receivers. |

### 4. Tallysman HC882 — Dual-Band Helical + L-Band
| Spec | Value |
|------|-------|
| **Bands** | L1/L2 + L-Band: GPS/QZSS-L1/L2, GLONASS-G1/G2, Galileo-E1/E5b, BeiDou-B1/B2 + L-Band |
| **Weight** | **37–42g** |
| **Dimensions** | Helical, ~22mm dia × ~85mm tall |
| **Type** | Active helical |
| **NDAA** | ✅ **Manufactured in Ottawa, Canada** (Calian/Tallysman) |
| **Price** | **~$150–250** (DigiKey, contact for exact pricing) |
| **Purchase** | [DigiKey 33-HC882-28](https://www.digikey.com/en/products/detail/tallysman-wireless-inc/33-HC882-28/10473741) |
| **Notes** | ⚠️ **L1/L2 only — NO L5.** This works but doesn't fully utilize the G5's triple-band heading capability. Good budget NDAA option if L5 isn't critical. |

### 5. Tallysman HC885XF — Dual-Band (L1/L5) Helical + L-Band
| Spec | Value |
|------|-------|
| **Bands** | L1/L5: GPS/QZSS-L1/L5, GLONASS-G1/G3, Galileo-E1/E5a/E5b, BeiDou-B1/B2/B2a, NavIC-L5 + L-Band |
| **Weight** | **42g** (housed version) |
| **Dimensions** | Helical with housing |
| **Type** | Active helical |
| **NDAA** | ✅ **Manufactured in Ottawa, Canada** (Calian/Tallysman) |
| **Price** | ⚠️ Cannot verify retail price — contact Tallysman/DigiKey |
| **Purchase** | [Tallysman](https://www.tallysman.com/product/hc885xf-dual-band-helical-antenna-l-band/) |
| **Notes** | ⚠️ **L1/L5 only — NO L2.** Modern L1/L5 design. Similar caveat as HC882 — doesn't cover all three bands the G5 uses in heading mode. |

---

## Recommendations

### 🏆 Best NDAA-Compliant Ultra-Light Option
**Maxtena M8HCT-A-SMA** (×2)
- 25g each, L1/L2/L5, USA-made, IP67
- **Cost: ~$740 for pair** (from Newark/DigiKey)
- Only true L1/L2/L5 + NDAA + ultra-light option available

### 🏆 Best NDAA-Compliant Performance Option
**Tallysman TW7972** (×2)
- ~80g each, L1/L2/L5 + L-Band, Canada-made
- **Cost: ~$500–700 for pair** (estimated)
- Septentrio's own recommended antenna — guaranteed compatibility
- Heavier, but best RF performance (superior multipath rejection)

### 🏆 Best Budget Option (NDAA May Be Compromised)
**ArduSimple Compact Helical Tripleband** (×2)
- 21g each, L1/L2/L5 + L-Band
- **Cost: ~€256 (~$278) for pair**
- Likely Chinese-made, not NDAA compliant
- Best weight and price if NDAA isn't strict

### ⚡ My Top Pick
If NDAA is a hard requirement: **Maxtena M8HCT-A-SMA × 2**. At 25g each with full L1/L2/L5, they're the lightest NDAA-compliant triple-band active antennas available. Made in USA. The ~$740 pair price is steep but there's no lighter NDAA alternative with full tri-band coverage.

If you can accept ~80g/antenna for better performance: **Tallysman TW7972 × 2**. These are what Septentrio recommends and sells alongside their receivers. Guaranteed compatibility, best signal quality.

---

## Important Notes

1. **Mosaic-G5 P3H in dual-antenna heading mode uses L1/L2/L5** (triple-band). Both antennas should cover all three bands for optimal heading accuracy.

2. **SMA connector** — ensure antennas have SMA-male (plugs into SMA-female on the ARK board) or appropriate adapter.

3. **Baseline distance** — for heading, the two antennas should be mounted as far apart as possible (typically 30–100cm). Longer baseline = better heading accuracy.

4. **Ground plane** — helical antennas are generally ground-plane independent (good for drone mounting). Patch antennas (TW7972) benefit from a ground plane but work without one.

5. **Active vs Passive** — the Mosaic-G5 P3H can supply DC bias for active antennas through the SMA connector. Active antennas (with LNA) are recommended for best performance.

---

## Price Verification Summary

| Antenna | Price Verified? | Source |
|---------|----------------|--------|
| Maxtena M8HCT-A-SMA | ✅ $370.31 ea | Newark Canada |
| SparkFun SPK-6E | ✅ $119.95 | SparkFun.com |
| ArduSimple Compact Helical TB | ✅ €128 | ArduSimple.com |
| ArduSimple Lightweight Helical TB | ✅ €146 | ArduSimple.com |
| ArduSimple Lightweight Helical MB (L1/L2) | ✅ €99 | ArduSimple.com |
| Tallysman TW7972 | ❌ Contact for quote | DigiKey/NavtechGPS |
| Tallysman HC882 | ❌ Contact for quote | DigiKey |
| Tallysman HC885EXF/XF | ❌ Contact for quote | Tallysman |
| Maxtena M9HCT-A-SMA | ❌ Estimated ~$370–450 | DigiKey |
| Maxtena M10HCT-A-SMA | ❌ Contact Maxtena | Maxtena |

---

## Changelog

- **2026-03-11:** Corrected SparkFun SPK-6E price from "$90.95–$119.95" to **$119.95** (only the $119.95 price confirmed on SparkFun.com).
