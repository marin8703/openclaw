# Hummingbird P1 / HB-18 — Battery Energy Density Recalculation

## Methodology (Summary)

- **Baseline airframe:** HB-18 Primary with 1 kg payload, dry weight and propulsion model from `flight_model.py`.
- **Battery pack reference:** Fixed **1043 g, 6S (22.2 V)** pack, matching the doc-spec HB-18 battery weight.
- **Chemistries / energy densities:**
  - 230 Wh/kg — **old doc baseline** (Molicel-class custom 21700 pack)
  - 174 Wh/kg — **Upper-tier commercial LiPo** (note: actual CNHL 5000mAh 6S 70C is ~155 Wh/kg at 714g)
  - 160 Wh/kg — **Tier 1 (Conservative)** standard commercial LiPo
  - 190 Wh/kg — **Tier 2 (Optimistic)** best available drone-optimized packs
- For each Wh/kg, the script recomputes **battery Wh**, **usable Wh** (80% DoD × 0.95 sag), and **hover power** from first principles for a **fixed 1043 g pack**.
- **Hover times** come directly from the updated `PAYLOAD SENSITIVITY (HB-18 @ 1043g battery, varying Wh/kg)` section of `flight_model.py`.
- **Realistic flight time** = hover time × **0.65** (same real‑world factor used in the commercial LiPo script and docs).
- **Operational range** assumes forward **cruise speed = 12 m/s (43.2 km/h)** and uses:
  - `range_km = realistic_time_min × 0.72`  (because 12 m/s = 0.72 km/min)
- **Nest fleet analysis** assumes:
  - **1 kg payload**, 1043 g battery, 6S 22.2 V
  - **2C charge rate**, idealized full charge in **30 min**
  - **4 min transit/overhead** per cycle
  - 30 drones in the Nest
  - Drones airborne (steady state) = `30 × flight_real / (flight_real + 30 + 4)`
  - Charger power per drone from `P = 2C × Ah × 22.2 V`
  - 7 kW Nest power budget used to compute **max simultaneous chargers**.

All values below are rounded to **1 decimal place**.

---

## Table 1: Hover Time Comparison (minutes)

**Pure hover, no 0.65 derating.** Payload is **external payload mass** (battery is fixed at 1043 g in all cases).

| Payload | 230 Wh/kg (old) | 174 Wh/kg (upper-tier) | 160 Wh/kg (Tier 1) | 190 Wh/kg (Tier 2) |
|--------:|----------------:|-----------------:|-------------------:|-------------------:|
| 0 kg    | 63.3            | 47.9             | 44.0               | 52.3               |
| 1.0 kg  | 35.1            | 26.5             | 24.4               | 29.0               |
| 1.5 kg  | 27.9            | 21.1             | 19.4               | 23.1               |

(Values from updated `flight_model.py` payload sweeps at 1043 g battery for each Wh/kg.)

---

## Table 2: Realistic Flight Time (×0.65 factor)

Realistic flight time = hover time × 0.65 (wind, maneuvering, altitude hold, safety reserve).

| Payload | 230 Wh/kg (old) | 174 Wh/kg (upper-tier) | 160 Wh/kg (Tier 1) | 190 Wh/kg (Tier 2) |
|--------:|----------------:|-----------------:|-------------------:|-------------------:|
| 0 kg    | 41.1            | 31.1             | 28.6               | 35.0               |
| 1.0 kg  | 22.8            | 17.2             | 15.9               | 18.9               |
| 1.5 kg  | 18.1            | 13.7             | 12.6               | 15.0               |

---

## Table 3: Operational Range at Cruise (km)

Assumes forward cruise speed **12 m/s (43.2 km/h)** and uses realistic flight time from Table 2:

> `Range (km) = Realistic flight time (min) × 0.72`

| Payload | 230 Wh/kg (old) | 174 Wh/kg (upper-tier) | 160 Wh/kg (Tier 1) | 190 Wh/kg (Tier 2) |
|--------:|----------------:|-----------------:|-------------------:|-------------------:|
| 0 kg    | 29.6            | 22.4             | 20.6               | 25.2               |
| 1.0 kg  | 16.4            | 12.4             | 11.4               | 13.6               |
| 1.5 kg  | 13.0            | 9.9              | 9.1                | 10.8               |

---

## Table 4: Charging Analysis

Reference pack in all cases: **1043 g, 6S (22.2 V)**. Capacity and Ah are recomputed for each Wh/kg. Charge time is idealized for a full charge at the given C‑rate.

| Config              | Charge Rate | Charge Time | Charger Power/Drone |
|---------------------|------------:|------------:|---------------------:|
| 230 Wh/kg (old)     | 2.0 C       | 30.0 min    | 480.0 W             |
| 174 Wh/kg (upper-tier)    | 2.0 C       | 30.0 min    | 362.0 W             |
| 160 Wh/kg (Tier 1)  | 2.0 C       | 30.0 min    | 333.0 W             |
| 190 Wh/kg (Tier 2)  | 2.0 C       | 30.0 min    | 398.0 W             |

Notes:
- Capacity for 1043 g pack at each chemistry:
  - 160 Wh/kg → 166.9 Wh → ~7.5 Ah
  - 174 Wh/kg → 181.5 Wh → ~8.2 Ah
  - 190 Wh/kg → 198.2 Wh → ~8.9 Ah
  - 230 Wh/kg → 239.9 Wh → ~10.8 Ah
- Charger power per drone is computed as `P ≈ 2C × Ah × 22.2 V` and rounded.

---

## Table 5: Nest Fleet Analysis (30‑Drone Nest)

Assumptions:
- Payload **1.0 kg** (nominal operations), 1043 g battery.
- **Realistic flight time** from Table 2 (1.0 kg row).
- **Charge rate:** 2C → **30 min** charge time.
- **Transit/overhead:** 4 min per cycle.
- **Drones airborne (steady state):**
  - `Airborne = 30 × flight_real / (flight_real + 30 + 4)`
- **Max simultaneous chargers @ 7 kW:** `floor(7000 W / P_charger_per_drone)`.

| Metric                                | 230 Wh/kg | 174 Wh/kg | 160 Wh/kg | 190 Wh/kg |
|---------------------------------------|----------:|----------:|----------:|----------:|
| Realistic flight time @ 1 kg (min)    | 22.8      | 17.2      | 15.9      | 18.9      |
| Cycle time (flight + 30 + 4) (min)    | 56.8      | 51.2      | 49.9      | 52.9      |
| Drones airborne (of 30, steady state) | 12.0      | 10.1      | 9.6       | 10.7      |
| Charger power per drone @ 2C (W)      | 480.0     | 362.0     | 333.0     | 398.0     |
| Max simultaneous chargers @ 7 kW      | 14        | 19        | 21        | 17        |

Interpretation:
- Moving from the old **230 Wh/kg** assumption down to **174 Wh/kg (upper-tier)** cuts per‑drone endurance and reduces steady‑state airborne drones by ~16% at the same charge/discharge assumptions. Note: the actual CNHL 5000mAh 6S 70C pack weighs **714g** (manufacturer spec), giving **~155 Wh/kg** — even lower than the 174 Wh/kg tier modeled here.
- **160 Wh/kg Tier 1** further reduces airborne count to **~9.6 of 30**, requiring either more aggressive charging (higher C‑rate), shorter missions, or additional Nests to maintain the same coverage footprint.
- **190 Wh/kg Tier 2** recovers a meaningful fraction of the lost endurance versus 230 Wh/kg while still being grounded in best‑in‑class off‑the‑shelf chemistry.

---

## Table 6: Delta Summary (vs 230 Wh/kg, 1.0 kg payload)

Percent differences are relative to the 230 Wh/kg baseline (positive = better than 230, negative = worse).

| Metric                                  | 160 vs 230 | 174 vs 230 | 190 vs 230 |
|-----------------------------------------|-----------:|-----------:|-----------:|
| Hover time @ 1 kg (min)                 | −30.5%     | −24.5%     | −17.4%     |
| Realistic time @ 1 kg (min)             | −30.3%     | −24.6%     | −17.1%     |
| Operational range @ 1 kg (km)           | −30.5%     | −24.4%     | −17.1%     |
| Drones airborne (Nest, 30 drones, 2C)   | −20.0%     | −15.8%     | −10.8%     |

---

These recalculated tables replace the optimistic 230 Wh/kg endurance figures with two realistic tiers (160 Wh/kg and 190 Wh/kg) plus an explicit 174 Wh/kg upper‑tier reference, tied directly to the updated `flight_model.py` first‑principles calculations. Note: the actual CNHL 5000mAh 6S 70C pack weighs **714g** ([manufacturer spec](https://chinahobbyline.com/products/cnhl-gplus-series-5000mah-22-2v-6s-70c-lipo-battery-with-xt90-plug)), yielding **~155 Wh/kg** — below the 160 Wh/kg Tier 1 assumption.

---

## Changelog

- **2026-03-11:** Corrected "CNHL-class" label from 174 Wh/kg to "upper-tier" since actual CNHL 5000mAh 6S 70C weighs 714g (not 640g), giving ~155 Wh/kg energy density. Added clarifying notes throughout.