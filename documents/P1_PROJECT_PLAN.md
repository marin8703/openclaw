# Hummingbird P1 Prototype — Master Build Plan

**Created:** 2026-02-26
**Owner:** Marin (Founder / Lead Engineer)
**Status:** Pre-build — CAD ~10 hours from completion, no components ordered
**Work Assumption:** ~3 hours/day available

---

## Executive Summary

This plan covers the full P1 prototype build — from completing the CAD model through to a flight-tested, validated prototype drone. The P1 must demonstrate autonomous flight, sensor integration, and communication — the foundational proof that the Hummingbird platform works.

**Key facts driving the plan:**
- **BOM cost:** ~$5,790/drone (NDAA-compliant, corrected 2026-03-11)
- **Dry weight (LW-PLA):** ~1,552g
- **Critical long-lead items:** Doodle Labs Mesh Rider (~$1,450, potential 2-4 week lead), ARK Jetson PAB Carrier ($700), ARK RTK GPS ($615)
- **Printing:** 4-piece body, LW-PLA, assembled with adhesive
- **Parallel track:** Tejash owns Nest (ground docking/charging system) — integration points identified below

**Timeline estimate:** ~160-200 total hours → **8-10 weeks at 3 hrs/day** from CAD completion to validated flight, assuming no major redesign loops. Component lead times may extend this by 1-3 weeks.

**Critical path:** CAD → Order long-lead components → Print → Assemble electronics → Flash firmware → Ground test → Flight test

---

## Table of Contents

1. [Phase 0: CAD Finalization & Print Prep](#phase-0)
2. [Phase 1: Component Sourcing](#phase-1)
3. [Phase 2: 3D Printing & Mechanical Assembly](#phase-2)
4. [Phase 3: Electronics Assembly & Wiring](#phase-3)
5. [Phase 4: Software & Firmware Setup](#phase-4)
6. [Phase 5: System Integration](#phase-5)
7. [Phase 6: Ground Testing & Validation](#phase-6)
8. [Phase 7: Flight Testing & DV](#phase-7)
9. [Phase 8: Iterative Debug & Optimization](#phase-8)
10. [Tejash / Nest Integration Points](#nest-integration)
11. [Dependency Map](#dependency-map)
12. [Risk Register](#risk-register)
13. [Key Milestones](#milestones)
14. [Full Hour Estimate Summary](#hour-summary)

---

<a name="phase-0"></a>
## Phase 0: CAD Finalization & Print Prep

**Status:** In progress — ~10 hours remaining
**Goal:** Production-ready STL files for all 4 body pieces, with verified mount points for every component

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 0.1 | Complete unified body CAD — remaining structural features | 4 | — | ✅ Yes |
| 0.2 | Design payload bay internals — mount points for FC (ARKV6X on PAB carrier), Jetson PAB carrier board, ESC boards (2× ARK 4IN1), battery bay (dual 3750mAh holders) | 3 | 0.1 | ✅ Yes |
| 0.3 | Add sensor mount features — RealSense D435i (front), LightWare SF20/C (front), FLIR Lepton (down/forward), 3× RPi Camera Module 3 (rear/down/up), ARK Flow (bottom) | 2 | 0.1 | ✅ Yes |
| 0.4 | Radio/antenna mount points — Doodle Labs (25g), RFD900x (14.5g), Sierra Wireless M.2 (on PAB carrier), XBee 900HP, antenna routing channels | 1.5 | 0.1 | ✅ Yes |
| 0.5 | Verify 4-piece split geometry — seam locations avoiding structural stress points, alignment features (pins/keys), adhesive surfaces | 1 | 0.1-0.4 | ✅ Yes |
| 0.6 | Export STL files — orient for printing, add support annotations, verify manifold/watertight | 1 | 0.5 | ✅ Yes |
| 0.7 | Create print settings profile — LW-PLA temperatures, fan, layer height, infill for structural vs lightweight zones | 0.5 | — | |
| 0.8 | Document critical dimensions — motor-to-motor spacing, duct inner diameter, mounting hole patterns for all components | 1 | 0.1-0.4 | |

**Phase 0 Total: ~14 hours (~5 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **Payload bay internal layout is the remaining unknown** — needs component datasheets for exact mounting hole patterns (ARK Jetson PAB: 80g, ARK 4IN1 ESC: 30.5mm mounting pattern)
- ⚠️ **Print orientation matters** — duct walls and motor mounts are structural; layer lines must align with load paths
- The 4-piece split must be designed so adhesive joints are NOT in high-stress areas (especially motor mount arms)
- ARK Jetson PAB Carrier integrates FC carrier + Jetson carrier + 4× CSI — this is the central board; design around it

---

<a name="phase-1"></a>
## Phase 1: Component Sourcing (NDAA BOM)

**Start:** Immediately (overlap with Phase 0 — order long-lead items ASAP)
**Goal:** All components in hand, verified against datasheets

### NDAA-Compliant BOM — Ordering Priority

#### Tier 1: Long-Lead / Critical Path (Order NOW)

| # | Component | Vendor | Est. Cost | Lead Time Est. | Notes |
|---|-----------|--------|-----------|---------------|-------|
| 1.1 | Doodle Labs Mini OEM Mesh Rider (2.4 GHz) | UAX Technologies / Doodle Labs | $1,450 | 2-4 weeks | Primary mesh radio. **Single most expensive component.** Verify availability before ordering. |
| 1.2 | ARK Jetson PAB Carrier Board | ARK Electronics | $700 | 1-3 weeks | Central integration board. Standalone price (bundle $1,100 − ARKV6X $400). Confirm stock on arkelectron.com |
| 1.3 | NVIDIA Jetson Orin Nano 8GB SOM | NVIDIA / distributor | $249 | 1-2 weeks | Verify compatibility with ARK PAB carrier |
| 1.4 | ARK RTK GPS (u-blox F9P) | ARK Electronics | $615 | 1-3 weeks | DroneCAN interface. Blue UAS listed. |
| 1.5 | ARKV6X Flight Controller | ARK Electronics | $400 | 1-2 weeks | Mounts on ARK PAB carrier via PAB connector |
| 1.6 | Sierra Wireless EM9291 (LTE/5G) | Sierra Wireless / distributor | ~$250 | 2-4 weeks | M.2 form factor. NDAA (Canada). Verify M.2 key type matches PAB carrier. |

#### Tier 2: Standard Availability (Order within first week)

| # | Component | Vendor | Est. Cost | Lead Time Est. | Notes |
|---|-----------|--------|-----------|---------------|-------|
| 1.7 | ARK 4IN1 ESC ×2 | ARK Electronics | $437 (2× $218.50) | 1-2 weeks | 50A cont, AM32 firmware, 30.5mm mount |
| 1.8 | T-Motor F60 Pro IV 2207.5 ×8 | RaceDayQuads | $328 (8× ~$41) | 3-5 days | ⚠️ Non-NDAA — no domestic alternative |
| 1.9 | RFDesign RFD900x-US | RFDesign / distributor | ~$118 | 1-2 weeks | 900 MHz backup telemetry |
| 1.10 | Digi XBee 900HP ×1 | Digi / distributor | ~$40 | 3-5 days | Approach/hold mesh radio |
| 1.11 | ARK Flow | ARK Electronics | $250 | 1-2 weeks | Optical flow + downward ToF rangefinder |
| 1.12 | LightWare SF20/C | LightWare / distributor | $279 | 1-3 weeks | Forward LiDAR, 100m range, 7.5g |
| 1.13 | Intel RealSense D435i | Intel / distributor | ~$350 | 3-5 days | Stereo depth + IMU. Widely available. |

#### Tier 3: Easy / Off-the-Shelf

| # | Component | Vendor | Est. Cost | Lead Time Est. | Notes |
|---|-----------|--------|-----------|---------------|-------|
| 1.14 | RPi Camera Module 3 ×3 | Various | ~$75 (3× $25) | 2-3 days | Sony IMX708, CSI to ARK PAB |
| 1.15 | FLIR Lepton 3.5 + breakout | GroupGets / SparkFun | ~$209 | 3-5 days | Thermal camera |
| 1.16 | Gemfan 5130 Triblade props ×4 sets | RaceDayQuads | ~$16 (4× $4) | 2-3 days | Plus spares |
| 1.17 | Battery: CNHL 6S 3750mAh class ×2 | CNHL / Amazon | ~$120 (2× ~$60) | 3-5 days | ⚠️ Non-NDAA. Verify capacity/size matches bay design. |
| 1.18 | Wiring harness materials — 14-16 AWG silicone wire, XT60 connectors, JST-GH connectors, Ethernet cable, heat shrink | Various | ~$50 | 2-3 days | |
| 1.19 | LW-PLA filament (1-2 kg) | ColorFabb / eSUN | ~$40 | 2-3 days | For frame printing |
| 1.20 | Fasteners — M3 brass heat-set inserts, M3 screws, nylon standoffs, vibration dampeners | Various | ~$30 | 2-3 days | |
| 1.21 | Adhesive — 2-part epoxy or cyanoacrylate for body piece bonding | Various | ~$15 | Immediate | |
| 1.22 | Miscellaneous — zip ties, double-sided tape, Kapton tape, antenna pigtails (SMA/U.FL) | Various | ~$25 | 2-3 days | |

### Sourcing Tasks

| # | Task | Hours | Dependencies |
|---|------|-------|-------------|
| 1.A | Verify stock availability for all Tier 1 items (check websites, email vendors) | 2 | — |
| 1.B | Place Tier 1 orders | 1.5 | 1.A |
| 1.C | Place Tier 2 orders | 1 | — |
| 1.D | Place Tier 3 orders (Amazon/hobby shops) | 0.5 | — |
| 1.E | Create receiving checklist — verify each component against datasheet on arrival | 0.5 | — |
| 1.F | Inspect and test-fit critical components on arrival (connectors, M.2, CSI, mounting holes) | 2 | Components arrive |

**Phase 1 Total: ~7.5 hours hands-on + 1-4 weeks shipping wait**
**Estimated BOM Total: ~$5,790** (single drone, NDAA-compliant; ARK Jetson PAB corrected to $700)

### Risks & Notes
- ⚠️ **Doodle Labs lead time is the #1 schedule risk** — if 4+ weeks, it delays comms integration. Mitigation: proceed with all other integration; Doodle Labs is not needed for basic flight testing.
- ⚠️ **Sierra Wireless EM9291 availability uncertain** — may need to source from specialized distributor. Fallback: skip LTE for P1 initial flights (mesh + 900 MHz sufficient for ground testing).
- ⚠️ **ARK Jetson PAB Carrier is relatively new** — confirm stock and shipping timeline directly with ARK Electronics
- 💡 **Order 2× of cheap consumables** (props, connectors, wire) — you WILL break things
- 💡 **Battery sizing:** Confirm CNHL 3750mAh 6S physical dimensions fit the designed battery bay BEFORE ordering in bulk. Buy 1 first for test fit.

---

<a name="phase-2"></a>
## Phase 2: 3D Printing & Mechanical Assembly

**Start:** After Phase 0 complete (STLs ready)
**Goal:** Fully assembled structural airframe with all mounts verified

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 2.1 | Print piece 1 of 4 — largest piece (estimate longest print) | 0.5 setup + ~8-16 hrs unattended print | 0.6 | ✅ Yes |
| 2.2 | Print piece 2 of 4 | 0.5 + print time | 0.6 | ✅ Yes |
| 2.3 | Print piece 3 of 4 | 0.5 + print time | 0.6 | ✅ Yes |
| 2.4 | Print piece 4 of 4 | 0.5 + print time | 0.6 | ✅ Yes |
| 2.5 | Post-processing — remove supports, sand mating surfaces, clean mounting holes | 2 | 2.1-2.4 | ✅ Yes |
| 2.6 | Dry-fit 4 pieces together — check alignment, gaps, structural feel | 1 | 2.5 | ✅ Yes |
| 2.7 | Install brass heat-set inserts in all mounting points | 1.5 | 2.5 | |
| 2.8 | Bond 4 pieces — apply adhesive, clamp/fixture, cure time | 1 active + cure time | 2.6 | ✅ Yes |
| 2.9 | Test-fit motors in duct mounts (all 8) — check alignment, shaft clearance | 1 | 2.8, motors arrive | ✅ Yes |
| 2.10 | Test-fit all electronics in payload bay — ARK PAB carrier, ESCs, battery trays | 1.5 | 2.8, components arrive | ✅ Yes |
| 2.11 | Identify and fix fit issues — re-drill holes, shim gaps, re-print pieces if needed | 2-4 | 2.9-2.10 | |
| 2.12 | Verify weight — weigh assembled frame vs CAD prediction | 0.5 | 2.8 | |

**Phase 2 Total: ~12-16 hours hands-on + ~24-48 hrs print time (runs overnight/during day)**
**Calendar time: ~5-7 days** (prints can run while doing other work)

### Risks & Notes
- ⚠️ **LW-PLA is tricky to print** — requires precise temperature control for foaming effect. Do a test cube first to dial in settings.
- ⚠️ **Structural weakness at bonded seams** — test a bonded sample piece under load before committing to full assembly
- ⚠️ **Motor mount accuracy is critical** — misaligned motors = vibration = bad IMU data = uncontrollable drone. Plan for tolerance checks.
- 💡 **Print spare motor mounts** if they're separate pieces — these will be high-stress and may crack
- 💡 **Duct wall thickness matters** — too thin and they'll flex; too thick adds weight. Aim for 1.5-2mm walls with internal ribs.

---

<a name="phase-3"></a>
## Phase 3: Electronics Assembly & Wiring

**Start:** After Phase 2 frame is assembled AND components have arrived
**Goal:** All electronics mounted, wired, and passing continuity/power-on checks

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 3.1 | **Plan wiring harness** — draw complete wiring diagram showing every connection (PAB carrier pinout, ESC signal/power, motor phases, GPS DroneCAN, sensors, radios, power distribution) | 3 | Component datasheets | ✅ Yes |
| 3.2 | **Mount ARK Jetson PAB Carrier** — vibration dampeners, standoffs, verify thermal clearance for Jetson heatsink | 1 | 2.10 | ✅ Yes |
| 3.3 | **Install Jetson Orin Nano SOM** onto PAB carrier — seat properly, verify M.2 slots | 0.5 | 3.2 | ✅ Yes |
| 3.4 | **Mount ARKV6X FC** onto PAB carrier's PAB connector | 0.5 | 3.2 | ✅ Yes |
| 3.5 | **Mount 2× ARK 4IN1 ESCs** — 30.5mm pattern, secure with vibration dampening | 1 | 2.10 | ✅ Yes |
| 3.6 | **Install motors (8×)** — mount in ducts, route phase wires to ESCs, verify rotation direction | 2 | 2.9 | ✅ Yes |
| 3.7 | **Wire ESCs to motors** — solder motor phase wires (3 per motor × 8 motors = 24 connections), verify motor-to-ESC mapping | 3 | 3.5, 3.6 | ✅ Yes |
| 3.8 | **Wire ESC signal cables** to PAB carrier / ARKV6X — DShot signal lines for all 8 motor outputs | 1 | 3.4, 3.5 | ✅ Yes |
| 3.9 | **Power distribution** — main battery leads (XT60) → power distribution → ESCs + BEC for 5V/12V rails → PAB carrier power input | 2 | 3.5 | ✅ Yes |
| 3.10 | **Mount and wire ARK RTK GPS** — DroneCAN bus to ARKV6X, verify antenna placement (top, unobstructed) | 1 | 2.10 | |
| 3.11 | **Mount and wire ARK Flow** — DroneCAN bus, mount bottom of frame with clear downward view | 0.5 | 2.10 | |
| 3.12 | **Mount and wire LightWare SF20/C** — serial/I2C to ARKV6X, mount forward-facing | 0.5 | 2.10 | |
| 3.13 | **Mount Intel RealSense D435i** — USB 3.0 to Jetson PAB carrier, mount between front ducts | 0.5 | 3.3 | |
| 3.14 | **Mount 3× RPi Camera Module 3** — CSI ribbon cables to PAB carrier (4× CSI ports available), route cleanly | 1 | 3.3 | |
| 3.15 | **Mount FLIR Lepton 3.5** — SPI/I2C to Jetson, mount with clear FOV | 0.5 | 3.3 | |
| 3.16 | **Install Doodle Labs Mesh Rider** — Ethernet/USB to Jetson, antenna placement (2.4 GHz — needs clear LOS) | 1 | Components arrive | |
| 3.17 | **Install Sierra Wireless EM9291** — M.2 slot on PAB carrier, SIM card, antenna pigtails | 0.5 | Components arrive | |
| 3.18 | **Install RFD900x-US** — UART to ARKV6X, antenna routing | 0.5 | Components arrive | |
| 3.19 | **Install XBee 900HP** — UART to Jetson → relay to ARKV6X, antenna routing | 0.5 | Components arrive | |
| 3.20 | **Dual battery bay wiring** — parallel connection harness, balance leads, charge contact interface wiring | 1.5 | 2.10, 3.9 | |
| 3.21 | **Cable management** — tie down all wires, ensure no interference with props, secure connectors | 1 | All above | |
| 3.22 | **Continuity check** — verify every connection with multimeter, check for shorts on power bus | 1 | All above | ✅ Yes |
| 3.23 | **First power-on (NO PROPS)** — apply battery power, verify all boards light up, no smoke test, check voltage rails | 1 | 3.22 | ✅ Yes |

**Phase 3 Total: ~24-26 hours (~8-9 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **The ARK Jetson PAB Carrier is the integration nexus** — get familiar with its pinout/documentation before starting wiring. It combines FC carrier + Jetson carrier + CSI ports + M.2 slots. One mistake here cascades everywhere.
- ⚠️ **Motor mapping to ESC channels must match ArduPilot's expected motor order** — document which motor is connected to which ESC output. Coaxial config needs custom motor mixing; wrong mapping = flip on liftoff.
- ⚠️ **Soldering 24 motor-to-ESC connections is tedious and error-prone** — take breaks, double-check each one. Cold solder joints cause intermittent failures that are brutal to debug in flight.
- ⚠️ **Dual battery parallel wiring** — must prevent reverse-feeding between packs if one fails. Use anti-backfeed diodes or rely on battery BMS.
- 💡 **Label everything** — motor numbers, ESC channels, wire colors. Your future debugging self will thank you.
- 💡 **Take photos at every stage** — useful for debugging AND documentation

---

<a name="phase-4"></a>
## Phase 4: Software & Firmware Setup

**Start:** Can begin in parallel with Phase 3 (on bench with just PAB carrier + Jetson)
**Goal:** ArduPilot configured for coaxial quad, Jetson booted with ROS 2, all sensors recognized

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 4.1 | **Flash ArduPilot onto ARKV6X** — latest stable that supports ARKV6X, configure for Copter firmware | 1 | 3.4 (FC mounted) | ✅ Yes |
| 4.2 | **Configure coaxial quad motor mixing** — custom 8-motor mapping (4 ducts × 2 coaxial per duct). This is NOT a standard ArduPilot frame type — requires custom motor output mapping. | 3 | 4.1 | ✅ Yes |
| 4.3 | **Configure ARKV6X parameters** — accelerometer/gyro calibration, barometer, DroneCAN bus for GPS/Flow, serial port assignments for radios (RFD900x, XBee) | 2 | 4.1, 3.10-3.12 connected | ✅ Yes |
| 4.4 | **Flash Jetson Orin Nano** — JetPack SDK (latest), Ubuntu, verify CUDA/TensorRT | 2 | 3.3 | ✅ Yes |
| 4.5 | **Install ROS 2** on Jetson — Humble or newer, verify install | 1 | 4.4 | |
| 4.6 | **Configure MAVLink bridge** — MAVROS or custom MAVLink router on Jetson, UDP link to ARKV6X via Ethernet | 2 | 4.4, 4.1 | ✅ Yes |
| 4.7 | **Verify sensor feeds on Jetson** — RealSense D435i (depth + RGB), RPi cameras (CSI), FLIR Lepton (thermal) | 2 | 4.4, 3.13-3.15 | |
| 4.8 | **Configure RTK GPS** — verify DroneCAN to ARKV6X, check satellite lock, position accuracy (no RTK corrections yet — standalone mode) | 1 | 3.10, 4.3 | |
| 4.9 | **Configure ARK Flow** — optical flow + ToF rangefinder via DroneCAN, verify altitude hold data | 1 | 3.11, 4.3 | |
| 4.10 | **Configure LightWare SF20/C** — serial/I2C rangefinder on ARKV6X, verify distance readings | 0.5 | 3.12, 4.3 | |
| 4.11 | **Radio configuration — RFD900x** — MAVLink telemetry, pair with ground station radio, verify bidirectional link | 1 | 3.18 | |
| 4.12 | **Radio configuration — Doodle Labs** — mesh setup, Jetson network interface, verify throughput | 1.5 | 3.16, 4.4 | |
| 4.13 | **Radio configuration — XBee 900HP** — P2P/P2MP mode, UART pass-through | 1 | 3.19 | |
| 4.14 | **Ground station setup** — Mission Planner or QGroundControl on laptop, connect via RFD900x telemetry, verify full telemetry display | 1 | 4.11 | ✅ Yes |
| 4.15 | **Configure safety parameters** — geofence, RTL altitude, battery failsafe thresholds, motor interlock, arming checks | 1 | 4.1-4.3 | ✅ Yes |
| 4.16 | **PID initial values** — set conservative starting PIDs for coaxial quad (likely need custom tuning — start with Arducopter defaults scaled for frame size/weight) | 1 | 4.2 | ✅ Yes |
| 4.17 | **Create parameter backup file** — export all ArduPilot params, save to repo | 0.5 | All above | |

**Phase 4 Total: ~22-24 hours (~7-8 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **Coaxial quad motor mixing is the #1 firmware risk.** ArduPilot supports coaxial via custom motor matrix, but 4-duct coaxial (8 motors) is non-standard. Need to carefully define the SERVO_FUNCTION and MOT_FRAME_TYPE parameters. Test motor spin direction and mapping on the bench (Phase 6) before any flight.
- ⚠️ **PID tuning for a coaxial ducted frame will NOT match standard quad values.** Ducted props have different thrust response curves. Expect multiple tuning iterations.
- ⚠️ **ARK Jetson PAB Carrier documentation may be limited** — it's a relatively new product. Budget time for figuring out pinouts/interfaces.
- 💡 **Start Phase 4 tasks 4.1-4.6 as soon as PAB carrier + FC + Jetson are mounted** — don't wait for all sensors. Firmware work is on the critical path.
- 💡 **ArduPilot coaxial resources:** Check ArduPilot wiki for "Dual Motor Tailsitter" or "OctoQuad Coax" frame types — closest analogs.

---

<a name="phase-5"></a>
## Phase 5: System Integration

**Start:** After Phases 3-4 complete
**Goal:** Fully assembled drone with all subsystems communicating and passing pre-flight checks

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 5.1 | **Full system power-on** — all electronics, all sensors, all radios powered simultaneously. Check power budget (measure total current draw with all systems active, no motors) | 1 | Phases 3 + 4 | ✅ Yes |
| 5.2 | **End-to-end telemetry check** — verify GCS receives full telemetry: attitude, GPS position, battery voltage/current, rangefinder, optical flow, radio RSSI | 1 | 5.1 | ✅ Yes |
| 5.3 | **Camera feed verification** — RealSense depth stream, RPi camera feeds (3×), FLIR thermal, all streaming to Jetson simultaneously | 1 | 5.1, 4.7 | |
| 5.4 | **Communication multi-link test** — verify simultaneous operation of Doodle Labs mesh, RFD900x telemetry, XBee, and LTE (if SIM active) without interference | 1.5 | 5.1, 4.11-4.13 | |
| 5.5 | **Weigh complete aircraft** — all components, batteries, props. Compare to design targets. Calculate actual T/W ratio. | 0.5 | Props installed | ✅ Yes |
| 5.6 | **CG (center of gravity) check** — balance on finger/rod test, adjust component positions or add ballast if significantly off-center | 1 | 5.5 | ✅ Yes |
| 5.7 | **Vibration isolation check** — tap test with IMU data logging, verify accelerometer noise is within ArduPilot acceptable ranges | 0.5 | 5.1 | |
| 5.8 | **Install propellers** — verify correct rotation direction per duct (CW/CCW pairs for coaxial), check for prop clearance in ducts | 1 | 5.5, 5.6 | ✅ Yes |
| 5.9 | **Pre-flight checklist creation** — document every check needed before each flight (battery voltage, prop security, GPS lock, telemetry link, safety switch, etc.) | 1 | All above | |

**Phase 5 Total: ~8-9 hours (~3 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **Total system current draw** — all radios + Jetson + sensors could push 3-4A on the 5V rail alone. Verify BEC capacity handles peak draw with margin.
- ⚠️ **RF interference between 4 radio systems** — 2.4 GHz (Doodle Labs), 900 MHz (RFD900x + XBee), LTE (various bands), plus GPS L1/L2. Antenna placement and shielding matter. Test for GPS degradation when radios transmit.
- ⚠️ **CG is critical for flight stability** — a heavy nose or tail will fight the FC. Battery position is your primary CG adjustment.

---

<a name="phase-6"></a>
## Phase 6: Ground Testing & Validation

**Start:** After Phase 5 integration complete
**Goal:** Confirm all systems work correctly without leaving the ground; validate motor control before flight

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 6.1 | **Motor spin test (no props)** — arm in test mode, spin each motor individually, verify direction, ESC response, no vibration/grinding | 1 | 5.1, 4.2 | ✅ Yes |
| 6.2 | **Motor spin test (with props, restrained)** — strap drone to workbench or test stand, spin all motors at low throttle, verify no prop strikes in ducts, check thrust direction | 1.5 | 5.8, 6.1 | ✅ Yes |
| 6.3 | **Motor order/direction verification** — use ArduPilot motor test in GCS, spin each motor individually and confirm it matches expected position in motor mixing matrix | 1 | 6.1, 4.2 | ✅ Yes |
| 6.4 | **Full-throttle thrust test (restrained)** — ramp to max throttle on test stand, measure total thrust with scale, compare to predicted 6,720g effective thrust | 1 | 6.2, test stand needed | |
| 6.5 | **Accelerometer calibration** — full 6-position accel cal with ArduPilot | 0.5 | 5.1 | ✅ Yes |
| 6.6 | **Compass calibration** — if using ARK RTK GPS magnetometer (outdoor, away from metal) | 0.5 | Outdoor access | |
| 6.7 | **Radio range test** — walk RFD900x ground station to 100m, 500m, check telemetry link quality. Repeat with Doodle Labs. | 1 | 4.11, 4.12 | |
| 6.8 | **GPS lock test** — outdoor stationary test, verify satellite count, HDOP, position accuracy (standalone + RTK if base station available) | 1 | 4.8 | |
| 6.9 | **Battery endurance bench test** — run all electronics (no motors) for 30+ min, log battery voltage curve, verify no brownouts or thermal issues | 1 | 5.1 | |
| 6.10 | **Tethered hover test (indoor or calm outdoor)** — 3-5 ft tether, attempt hover at low altitude, verify stability, check for oscillations or yaw spin | 2 | 6.1-6.5 | ✅ Yes |
| 6.11 | **Log review** — download ArduPilot logs from tethered hover, analyze IMU data, motor outputs, PID response, identify obvious tuning issues | 1.5 | 6.10 | ✅ Yes |

**Phase 6 Total: ~12-13 hours (~4-5 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **Tethered hover is the most important ground test.** If the drone can't hover stably on a tether, DO NOT attempt free flight. Common issues: wrong motor direction, wrong motor order, bad PID, CG off.
- ⚠️ **Coaxial prop clearance in ducts** — if props are too close to duct walls, efficiency drops and vibration increases. Need ~2-3mm tip clearance minimum.
- ⚠️ **Test stand for thrust measurement** — you may need to build/buy a simple thrust stand. Even a kitchen scale + frame works for rough measurement.
- 💡 **Log everything.** ArduPilot .bin logs are your primary debugging tool. Set LOG_BITMASK to capture everything during testing.
- 💡 **Film the tethered hover** — video is invaluable for diagnosing flight issues (oscillation, yaw, drift direction)

---

<a name="phase-7"></a>
## Phase 7: Flight Testing & Design Verification

**Start:** After successful tethered hover (Phase 6.10)
**Goal:** Free flight, PID tuning, endurance measurement, sensor verification in flight

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 7.1 | **First free hover** — calm conditions, 3-5 ft altitude, manual stabilize mode, 30s-1min, land | 2 | 6.10 pass, 6.11 log clean | ✅ Yes |
| 7.2 | **PID tuning — rate PIDs** — iterative flights with log analysis. Adjust pitch/roll/yaw rate P, I, D. Expect 3-5 flights minimum. | 4 | 7.1 | ✅ Yes |
| 7.3 | **PID tuning — stabilize / attitude PIDs** — once rate PIDs are solid, tune angle hold | 2 | 7.2 | ✅ Yes |
| 7.4 | **Position hold test** — switch to Loiter or PosHold mode, verify GPS+optical flow hold position within ~1m | 1.5 | 7.3, 4.8, 4.9 | ✅ Yes |
| 7.5 | **Altitude hold test** — verify barometer + rangefinder altitude hold stability | 1 | 7.3 | |
| 7.6 | **Auto mission test** — simple waypoint mission (takeoff → fly to point → RTL), verify autonomous flight | 1.5 | 7.4 | ✅ Yes |
| 7.7 | **Endurance flight** — hover at representative payload weight, time to battery warning/land, compare to predictions (~27-32 min expected with dual battery) | 1.5 | 7.3 | ✅ Yes |
| 7.8 | **Failsafe tests** — trigger battery failsafe (let voltage drop), trigger GCS loss (turn off radio), verify RTL behavior | 1.5 | 7.6 | |
| 7.9 | **Sensor validation in flight** — verify all cameras stream, RealSense depth works, GPS accuracy in motion, optical flow tracks, LiDAR reads correctly | 2 | 7.4 | |
| 7.10 | **Multi-radio test in flight** — verify telemetry via all links simultaneously during flight | 1 | 7.4 | |
| 7.11 | **Max wind test** — fly in 10-15 mph wind, assess stability and controllability | 1 | 7.3 | |
| 7.12 | **Noise measurement** — measure decibels at various distances (5m, 10m, 20m), compare to duct efficiency expectations | 0.5 | 7.1 | |
| 7.13 | **Document flight test results** — performance summary, flight logs, video, issues found, comparison to design targets | 2 | All above | |

**Phase 7 Total: ~22-24 hours (~7-8 days at 3 hrs/day)**

### Risks & Notes
- ⚠️ **First free hover is the highest-risk moment.** Have kill switch ready. Fly over soft ground (grass). No spectators near the flight area. Keep first flight short (30s-1min).
- ⚠️ **PID tuning for coaxial ducted frame is uncharted territory.** No ArduPilot PID presets exist for this configuration. Budget extra time. Consider using ArduPilot's autotune mode after initial manual tune gets it roughly stable.
- ⚠️ **Have spare props on hand.** Crash damage during tuning is almost guaranteed. Budget 4-8 extra sets.
- ⚠️ **Battery monitor calibration** — verify voltage and current sensor readings match multimeter measurements. Wrong battery readings = wrong failsafe = potential crash or LiPo damage.
- 💡 **Fly early morning or evening** — calmest wind conditions
- 💡 **Each flight: fresh charged battery, pre-flight checklist, GCS connected, video recording**

---

<a name="phase-8"></a>
## Phase 8: Iterative Debug & Optimization

**Start:** Ongoing from first flight test
**Goal:** Resolve all issues, optimize performance, document lessons learned

### Tasks

| # | Task | Hours | Dependencies | Critical Path? |
|---|------|-------|-------------|----------------|
| 8.1 | **Structural repairs** — fix cracks, reinforce weak points found during testing (LW-PLA is brittle under impact) | 2-6 | Flight test results | |
| 8.2 | **Reprint components** — if motor mounts, ducts, or structural features need redesign based on real-world loads | 4-10 | 8.1, requires CAD revision | |
| 8.3 | **ESC/motor troubleshooting** — desync issues, overheating, timing adjustments | 2-4 | Flight logs | |
| 8.4 | **Vibration reduction** — add dampeners, rebalance props, tighten loose components, move heavy items | 1-3 | IMU log analysis | |
| 8.5 | **Communication debugging** — RF interference resolution, antenna repositioning, range optimization | 2-4 | Radio test results | |
| 8.6 | **PID refinement** — continued tuning after hardware fixes change flight dynamics | 2-4 | 8.1-8.4 | |
| 8.7 | **Weight optimization** — identify and eliminate unnecessary weight based on actual build | 1-2 | Build complete | |
| 8.8 | **Document all changes** — update P1 design doc, wiring diagrams, parameter files | 2-3 | All changes | |

**Phase 8 Total: ~16-36 hours (variable — depends on issues found)**

### Risks & Notes
- This phase is inherently unpredictable. Budget 20-30% of total project time for it.
- ⚠️ **A hard crash may require complete rebuild of structural components** — have spare LW-PLA filament on hand
- 💡 **Keep a running issue log** — track every anomaly, even minor ones. Patterns emerge.
- 💡 **Version your ArduPilot parameter files** — every change, save a snapshot. Makes rollback easy.

---

<a name="nest-integration"></a>
## Tejash / Nest Integration Points

Tejash (CTO) owns the Nest ground system in parallel. These are the points where drone and Nest must interface.

### Drone-Side Requirements (Marin's Responsibility)

| Integration Point | What Marin Must Deliver | When Needed |
|---|---|---|
| **Docking surface geometry** | Exact 3D model of drone bottom with permanent magnet positions, docking surface flatness, alignment features | Phase 0 (CAD) — share with Tejash |
| **Charging contacts** | Pogo pin / contact pad locations, voltage/current specs (22.2V nominal, 3C charge = ~11A per pack × 2 packs), pin count (8+) | Phase 0 (CAD) + Phase 3 (wiring) |
| **Drone dimensions & weight** | Cassette envelope: 600 × 300 × 270-300mm, actual weight (target ~3.2 kg AUW) | Phase 5 (after weighing) |
| **900 MHz radio interface** | XBee 900HP endpoint config, RFD900x config, MAVLink message set for capture mode | Phase 4 (firmware) |
| **IR LED pattern** | LED positions, blink encoding for drone ID and heading, electrical specs | Phase 3 (if implementing for P1) |
| **ArduPilot capture mode** | MAVLink command sequence for Ground Manager to assume flight authority via 900 MHz | Phase 4 (firmware) |

### Nest-Side Requirements (Tejash's Responsibility) 🏗️

| Integration Point | What Tejash Must Deliver | When Needed |
|---|---|---|
| **Cassette slot design** | Mechanical slot that accepts 600×300×300mm drone, with charging contacts aligned to drone contact pads | After Marin provides docking surface geometry |
| **Electromagnet end effector** | Specs: attraction force, activation/deactivation timing, self-centering range (~2" per design) | P1 capture testing |
| **Robotic arm specs** | 6-DOF arm reach (3.5-4ft), load capacity (≥3.5 kg for drone + safety margin), positioning accuracy | P1 capture testing |
| **Ground-side 900 MHz** | 2× XBee 900HP coordinators + 1× SiK radio (per architecture), Ground Manager software to orchestrate approach → capture handoff | P1 capture testing |
| **Vehicle-side IR camera** | Camera + tracking software for IR LED acquisition at ~5-6 ft range | P1 capture testing |
| **Charging power supply** | 15 kW system (per updated analysis), parallel charging for dual battery packs at 3C, thermal monitoring | P1 charging testing |
| **Ground Manager software (ROS 2)** | Launch sequence, capture sequence, arm control, charging management, power distribution | P1 system integration |
| **RTK base station** | Vehicle-mounted RTK base broadcasting corrections (for cm-level drone positioning) | P1 RTK flight testing |

### Integration Milestones (Joint)

| Milestone | Target | Description |
|---|---|---|
| **IM-1: Interface Spec Freeze** | End of Phase 0 | Marin shares docking geometry, charging contact locations, cassette envelope. Tejash confirms Nest slot design compatible. |
| **IM-2: Drone Flight Demo** | End of Phase 7 | Marin demonstrates stable flight, position hold, autonomous waypoint mission. Proves drone half works. |
| **IM-3: Capture Comm Test** | Phase 4/6 | Test 900 MHz link: Ground Manager sends MAVLink commands to drone, drone responds. No physical capture yet — just comms. |
| **IM-4: Stationary Capture Attempt** | Post Phase 7 + Tejash arm ready | First attempt at arm-guided capture of hovering drone. Most complex integration milestone. |
| **IM-5: Charge Cycle Test** | Post IM-4 | Drone captured → inserted in slot → charging initiates → charging completes → drone removed for re-launch. |
| **IM-6: Full Cycle Demo** | Post IM-5 | Launch → fly mission → return → capture → charge → re-launch. The P1 complete cycle. |

### Communication with Tejash
- Weekly sync recommended (continue Thursday calls)
- Share CAD files / interface specs as soon as Phase 0 completes
- Tejash needs drone dimensions ASAP to design cassette slots

---

<a name="dependency-map"></a>
## Dependency Map

```
Phase 0 (CAD) ──────────┬──────────────────────> Phase 2 (Print & Assembly)
                         │                              │
                         │                              ▼
Phase 1 (Sourcing) ──┬──┼──────────────────────> Phase 3 (Electronics)
   [Start ASAP]      │  │                              │
                      │  │                              ▼
                      │  │  ┌───────────────────> Phase 4 (Firmware)
                      │  │  │  [Can partially        │
                      │  │  │   overlap Phase 3]      │
                      │  │  │                         ▼
                      │  │  │                   Phase 5 (Integration)
                      │  │  │                         │
                      │  │  │                         ▼
                      │  │  │                   Phase 6 (Ground Test)
                      │  │  │                         │
                      │  │  │                         ▼
                      │  │  │                   Phase 7 (Flight Test)
                      │  │  │                         │
                      │  └──┼─────────────────> Phase 8 (Debug)
                      │     │                    [Iterative loop]
                      │     │
Tejash: Nest ─────────┼─────┼──> IM-1 ──> IM-3 ──> IM-4 ──> IM-5 ──> IM-6
  [Parallel track]    │     │
                      └─────┘
```

### Critical Path (Longest Sequential Chain)
```
CAD Finalize (14h) → Print/Assemble (14h) → Electronics (25h) → Firmware (23h*) → Integration (9h) → Ground Test (13h) → Flight Test (23h)
                                                                    * Partially overlaps with Electronics

Total Critical Path: ~105-120 hours ≈ 35-40 working days ≈ 7-8 weeks at 3 hrs/day
```

**Calendar critical path driver: Component shipping** — if Tier 1 items take 3-4 weeks, they may gate Phase 3 start even if printing is done sooner.

---

<a name="risk-register"></a>
## Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R1 | **Coaxial quad PID tuning proves extremely difficult** | Medium-High | High — can't fly | Research ArduPilot forums/Discord, consider contracting tuning help, use autotune mode, have patience for 10+ tuning flights |
| R2 | **Doodle Labs Mesh Rider out of stock / long lead** | Medium | Medium — delays comms | Order immediately; fly initial tests without it (use RFD900x only for telemetry) |
| R3 | **ARK Jetson PAB Carrier documentation gaps** | Medium | Medium — delays wiring | Contact ARK Electronics support directly, check their Discord/community |
| R4 | **LW-PLA frame too weak / cracks on hard landing** | Medium | Medium — delays testing | Print spare parts, reinforce high-stress areas with CF-PETG inserts, fly over soft surfaces |
| R5 | **Motor mount misalignment causes vibration** | Low-Medium | High — bad IMU data | Precision check during assembly, use vibration dampeners on FC, reprint mounts if needed |
| R6 | **Actual weight exceeds design target** | Medium | Medium — reduced endurance/T/W | Weigh as-built at Phase 5; remove non-essential sensors for initial flights if overweight |
| R7 | **Battery energy density lower than expected** | Already mitigated | Low | Using corrected 160/190 Wh/kg in all calculations |
| R8 | **ESC desync with coaxial setup** | Low-Medium | High — crash | Use DShot protocol, verify ESC timing, test at low throttle first, carry spare ESCs |
| R9 | **RF interference between 4 radio systems** | Medium | Medium — degraded comms/GPS | Careful antenna placement, ground plane isolation, test incrementally |
| R10 | **Hard crash destroys prototype** | Low-Medium | Very High — weeks to rebuild | Tethered testing first, conservative flying, spare parts on hand, fly low over grass |

---

<a name="milestones"></a>
## Key Milestones

| # | Milestone | Target Date* | Success Criteria |
|---|-----------|-------------|------------------|
| M1 | **CAD Complete** | Week 1 | All STLs exported, print-ready, mount points verified |
| M2 | **Components Ordered** | Week 1 | All BOM items ordered, tracking numbers received |
| M3 | **Frame Printed & Assembled** | Week 2-3 | 4 pieces bonded, all mounts verified with test-fit |
| M4 | **Electronics Installed** | Week 4-5 | All boards mounted, wired, passing continuity check |
| M5 | **First Power-On** | Week 5 | All systems boot, no magic smoke, telemetry to GCS |
| M6 | **Firmware Configured** | Week 5-6 | ArduPilot + Jetson configured, sensors reporting to GCS |
| M7 | **Tethered Hover** | Week 6-7 | Stable hover on tether, clean IMU logs |
| M8 | **First Free Flight** | Week 7 | 30s+ stable free hover |
| M9 | **Position Hold Achieved** | Week 7-8 | GPS/optical flow position hold within 1m |
| M10 | **Autonomous Mission** | Week 8-9 | Waypoint mission + RTL completed successfully |
| M11 | **Endurance Validated** | Week 9 | Measured flight time within 15% of prediction |
| M12 | **P1 Drone Validated** | Week 9-10 | All DV criteria met, documented, ready for Nest integration |

*Weeks counted from today, assuming ~3 hrs/day. Adjusted for component lead times.

---

<a name="hour-summary"></a>
## Full Hour Estimate Summary

| Phase | Description | Estimated Hours | Calendar Days (~3h/day) |
|-------|-------------|-----------------|------------------------|
| 0 | CAD Finalization & Print Prep | 14 | 5 |
| 1 | Component Sourcing | 7.5 + shipping wait | 3 + 1-4 wks wait |
| 2 | 3D Printing & Mechanical Assembly | 12-16 | 5-7 (incl. print time) |
| 3 | Electronics Assembly & Wiring | 24-26 | 8-9 |
| 4 | Software & Firmware Setup | 22-24 | 7-8 |
| 5 | System Integration | 8-9 | 3 |
| 6 | Ground Testing & Validation | 12-13 | 4-5 |
| 7 | Flight Testing & DV | 22-24 | 7-8 |
| 8 | Iterative Debug & Optimization | 16-36 | 5-12 |
| | **TOTAL** | **138-173 hours** | **47-57 working days** |

**Realistic timeline with buffer: 9-12 weeks from today** (includes component shipping, unexpected issues, weather delays for outdoor testing)

---

## Immediate Next Actions (This Week)

1. **TODAY:** Check stock availability for Tier 1 components (Doodle Labs, ARK PAB, ARK RTK GPS, ARKV6X) — these drive the schedule
2. **TODAY/TOMORROW:** Place Tier 1 orders for anything in stock
3. **Continue:** CAD finalization — 10 hours remaining
4. **Before ordering batteries:** Confirm CNHL 3750mAh 6S physical dimensions fit CAD battery bay design
5. **Share with Tejash (Thursday call):** Drone cassette envelope (600×300×300mm), docking surface concept, charging contact requirements. Request his timeline for arm + cassette prototype.

---

*This plan is a living document. Update as you complete phases and discover new information. The reality of building always deviates from the plan — that's expected. The plan's value is in the sequence, dependencies, and risk awareness, not the exact hours.*
