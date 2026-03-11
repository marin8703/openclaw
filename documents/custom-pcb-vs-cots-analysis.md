# Custom PCB Design vs COTS Module Integration for Hummingbird Drone Electronics

**Prepared for:** Hummingbird Technologies Executive Team  
**Date:** March 2026  
**Classification:** Internal — Business Sensitive

---

## Executive Summary

Hummingbird Technologies currently builds its ducted coaxial quad-rotor drone (~2.9kg AUW) using entirely off-the-shelf (COTS) modules — Pixhawk 6X flight controller, Jetson Orin Nano 8GB companion computer, 8× individual ESCs, GPS/RTK, radios, and associated peripherals — at an NDAA-compliant per-drone BOM of ~$5,900.

This analysis evaluates whether transitioning to custom PCB designs with discrete components could reduce cost, improve NDAA compliance posture, save weight, or provide other competitive advantages. **Our recommendation is a phased approach:** stay COTS for P1 prototyping, begin custom integration of ESCs and power management for P2 (small production at 50-100 units), and pursue a fully integrated avionics board only at GA volumes (500+ units/year) where the economics become compelling.

Key findings:
- **Cost crossover** at approximately **200-500 units** for a combined FC+ESC+power board
- **Potential per-unit savings** of $800-1,500 at volume (14-25% BOM reduction)
- **Weight savings** of 150-250g (5-9% of AUW) from eliminating redundant housings, connectors, and power regulators
- **NDAA story improves significantly** with custom boards using US/allied-sourced ICs and US/allied PCB fabrication
- **NRE investment** of $150K-350K depending on scope, with 12-18 month development timeline

---

## 1. Cost Comparison Framework

### 1.1 COTS Module Current Costs (Per Drone)

| Component | Module | Est. Cost |
|-----------|--------|-----------|
| Flight Controller | Holybro Pixhawk 6X (STM32H753, 3× IMU, 2× baro) | $237 |
| Companion Computer | Jetson Orin Nano 8GB (SOM + carrier board) | $299 |
| ESCs (×8) | Individual 50A ESCs (e.g., Holybro Tekko32 4-in-1, ×2) | $320-480 |
| GPS/RTK | u-blox ZED-F9P based module (e.g., Holybro H-RTK F9P) | $250-350 |
| ADS-B In | uAvionix pingRX | $250-350 |
| Remote ID | uAvionix pingID | $200-300 |
| Power Module | PM02D or equivalent | $30-50 |
| Radios (telemetry + RC) | SiK radio + RC receiver | $100-200 |
| Wiring harness, connectors | Custom harness | $50-100 |
| Other peripherals | Magnetometer, airspeed, etc. | $100-200 |
| **Subtotal electronics** | | **~$1,850-2,550** |
| Airframe, motors, props, battery, cameras | | **~$3,200-3,900** |
| **Total per-drone BOM** | | **~$5,700** |

### 1.2 NRE Costs for Custom Avionics PCBs

Based on industry benchmarks for comparable complexity (drone avionics, mixed-signal, power electronics):

| NRE Category | Estimated Cost | Notes |
|-------------|---------------|-------|
| **Hardware engineer (12-18 mo)** | $120K-200K | Full-time senior EE, or contract design house |
| **Schematic & PCB layout** | $30K-60K | If outsourced to a design firm (e.g., Titoma, AltiumLive partners) |
| **Prototype PCB fab (3-5 revs)** | $15K-40K | US fab (Sierra Circuits, Advanced Circuits): $2K-8K per rev for 6-8 layer boards |
| **Prototype assembly** | $10K-25K | Low-volume PCBA at $2K-5K per run |
| **Component procurement (protos)** | $5K-15K | Small qty IC purchases at 1× pricing |
| **Testing & certification** | $20K-50K | EMC, environmental, firmware validation |
| **Firmware adaptation** | $10K-30K | PX4/ArduPilot porting, driver development |
| **Total NRE** | **$150K-350K** | Scope-dependent |

**Reference:** Titoma's NRE calculator estimates $35K-65K for working prototype NRE on embedded systems of similar complexity, with additional $30K+ for mass production NRE. Complex multi-board avionics systems with power electronics (ESC integration) push to the higher end.

### 1.3 Custom Board Per-Unit Cost Estimate

For an integrated FC + 8× ESC + power management board:

| Component | Unit Cost (qty 100) | Unit Cost (qty 500) |
|-----------|--------------------|--------------------|
| STM32H753VIT6 (MCU) | ~$14.50 | ~$12.00 |
| ICM-42688-P × 3 (IMU) | ~$5-7 ea = $15-21 | ~$4-5 ea = $12-15 |
| MS5611 × 2 (barometer) | ~$10 ea = $20 | ~$8 ea = $16 |
| Gate drivers + MOSFETs (8× ESC channels) | ~$40-60 | ~$30-45 |
| Power regulation (buck/boost, LDOs) | ~$10-15 | ~$8-12 |
| Passive components, connectors | ~$15-25 | ~$10-18 |
| PCB fabrication (6-8 layer, US/allied) | ~$25-40 | ~$12-20 |
| PCBA assembly | ~$30-50 | ~$15-25 |
| **Custom board total** | **~$170-245** | **~$115-165** |
| **COTS equivalent** (Pixhawk 6X + 8× ESC + power module) | **~$590-770** | **~$590-770** |
| **Per-unit savings** | **$350-600** | **$425-655** |

### 1.4 Crossover Analysis

```
Per-unit savings at volume: ~$500 average
NRE investment: ~$250K (mid-range)

Breakeven = NRE / per-unit savings = $250K / $500 = 500 units

With more aggressive integration (adding GPS, ADS-B, Remote ID):
Per-unit savings: ~$1,000-1,500
Breakeven = $350K / $1,250 = 280 units
```

**Volume crossover: Custom PCBs become cost-advantageous at approximately 200-500 cumulative units**, depending on integration scope. For a company planning to produce 100+ drones per year, the payback period is 2-3 years.

### 1.5 Industry Precedent

- **Auterion Skynode S**: A "chip-down" custom-designed all-in-one controller integrating FMUv6x flight controller + mission computer + ESC connections on a single board. This represents the industry direction for volume production — purpose-built integrated avionics replacing modular COTS stacks.
- **Skydio**: Designs all custom electronics in-house (fully integrated boards). This is standard practice for any drone company producing 1,000+ units/year. Blue UAS listed.
- **Teal Drones** (FLIR/Teledyne): Custom electronics, Blue UAS certified. In-house hardware design.
- **Shield AI (V-BAT, Nova 2)**: Custom avionics boards, Blue UAS listed.

**Pattern:** Every Blue UAS listed company of significant scale uses custom-designed PCBs rather than off-the-shelf Pixhawk modules.

---

## 2. Integration Opportunities

### 2.1 What CAN Be Integrated onto Custom PCBs

| Subsystem | Current COTS | Custom Integration Approach | Complexity |
|-----------|-------------|---------------------------|------------|
| **Flight Controller** | Pixhawk 6X | STM32H753 + 3× ICM-42688-P/ICM-45686 + 2× MS5611 barometer + magnetometer | Medium — well-documented open hardware (Pixhawk FMUv6X schematics are public) |
| **ESCs (×8)** | 8× individual ESCs | 8× gate driver + MOSFET half-bridges on integrated board | Medium-High — thermal management critical, high-current traces |
| **GPS/RTK** | ZED-F9P module on carrier board | ZED-F9P module soldered directly (it's already an IC-level module) | Low — ZED-F9P is designed for board-level integration |
| **ADS-B In** | Standalone receiver | Integrated ADS-B receiver IC (e.g., uAvionix µADS-B chipset) | Medium |
| **Remote ID** | Standalone module | ESP32 or STM32 + BLE/WiFi radio on main board | Low-Medium |
| **Power Management** | Separate PM + PDB | Integrated voltage sensing, current sensing, power distribution, regulators | Medium |
| **Magnetometer** | External module | Integrated on PCB (e.g., Bosch BMM150, QMC5883L — but placement away from high-current traces critical) | Low, but layout-sensitive |

### 2.2 What CANNOT Be Easily Integrated

| Component | Reason |
|-----------|--------|
| **Jetson Orin Nano SOM** | Proprietary NVIDIA module with 260-pin SODIMM connector; must remain as plug-in SOM on carrier board. However, a *custom carrier board* for the Orin Nano is very feasible and can integrate other peripherals. |
| **Cameras** | Require specific optics, sensor modules, ribbon cables. Stay as separate modules. |
| **Motors** | Electromechanical — physically separate by definition. |
| **Battery cells** | Electrochemical — separate. BMS circuitry CAN be integrated onto avionics board. |
| **Antennas** | GPS, telemetry, RC antennas need specific placement. PCB-integrated antennas possible for some (BLE for Remote ID) but external antennas preferred for performance. |
| **Radio transceivers (long-range telemetry)** | Could be integrated but regulatory certification (FCC) complexity makes standalone modules preferable initially. |

### 2.3 Recommended Integration Architecture

**Phase 1 — "Avionics Core" Board:**
- STM32H753 flight controller
- 3× IMU (ICM-45686 or ICM-42688-P)
- 2× barometer (MS5611)
- Magnetometer
- 8× ESC channels (gate drivers + MOSFETs)
- Power distribution + current/voltage sensing
- Remote ID (integrated BLE/WiFi)
- Standard connectors for: GPS module, ADS-B, telemetry radio, RC receiver, Jetson carrier

**Phase 2 — "Full Integration" Board:**
- Everything from Phase 1 PLUS:
- ZED-F9P GPS/RTK receiver (soldered on-board)
- ADS-B In receiver
- Jetson Orin Nano carrier board functionality (SODIMM socket, CSI camera connectors, USB, Ethernet)

---

## 3. NDAA Compliance Implications

### 3.1 How Custom PCBs Improve the NDAA Story

Custom board design provides **significantly stronger NDAA compliance** because:

1. **Full BOM transparency** — You specify every component, know every manufacturer and country of origin
2. **No hidden Chinese sub-components** — COTS modules (especially from Holybro, a Shenzhen-headquartered company) may contain sub-components sourced from covered nations
3. **Controlled PCB fabrication** — You choose the fab house; COTS module PCBs are almost certainly fabricated in China
4. **Documentation for Blue UAS** — Custom design means you have complete chain-of-custody documentation that Blue UAS / Green UAS evaluation requires

### 3.2 Critical IC Sourcing — NDAA-Compliant Options

| IC Category | Recommended Part | Manufacturer | HQ / Fab | NDAA Status |
|-------------|-----------------|-------------|----------|-------------|
| **MCU** | STM32H753 | STMicroelectronics | Switzerland/France; fabs in France, Italy, Singapore | ✅ Allied nation |
| **IMU** | ICM-42688-P / ICM-45686 | TDK InvenSense | Japan (TDK); design in San Jose, CA | ✅ Allied nation |
| **Barometer** | MS5611-01BA03 | TE Connectivity | Switzerland; fabs in multiple allied nations | ✅ Allied nation |
| **GPS/RTK** | ZED-F9P | u-blox | Switzerland; design in CH, module assembly varies | ✅ Allied nation (verify assembly location) |
| **Magnetometer** | BMM150 | Bosch Sensortec | Germany | ✅ Allied nation |
| **MOSFET (ESC)** | Various (IRFZ44, BSC030N08, etc.) | Infineon, ON Semi, Texas Instruments | Germany, USA | ✅ Allied nation |
| **Gate Driver** | DRV8320 or similar | Texas Instruments | USA | ✅ US |
| **Voltage Regulator** | TPS series | Texas Instruments | USA | ✅ US |
| **BLE/WiFi (Remote ID)** | ESP32-C3 | Espressif | China (Shanghai) | ⚠️ **Risk** — use Nordic nRF52840 (Norway) or STM32WB instead |
| **ADS-B Receiver** | Various | uAvionix | USA | ✅ US |

**Key risk:** Many common WiFi/BLE chips (ESP32, Qualcomm QCA series) are designed or manufactured in China. For Remote ID, use Nordic Semiconductor (Norway) or Silicon Labs (USA) alternatives.

### 3.3 PCB Fabrication — Country of Origin

Per BotBlox's NDAA compliance guide, China accounts for ~52% of global PCB manufacture. NDAA-compliant alternatives:

| Fab House | Location | Capabilities | Prototype Pricing (6-layer, 10 pcs) | Volume Pricing |
|-----------|----------|-------------|-------------------------------------|----------------|
| **Sierra Circuits** | Sunnyvale, CA, USA | Proto to mid-volume, ITAR registered | ~$2,000-5,000 | Competitive for <1,000 pcs |
| **Advanced Circuits** | Aurora, CO, USA | Proto to production, ITAR registered | ~$1,500-4,000 | Mid-range |
| **TTM Technologies** | Multiple US sites | High-volume, defense-grade | Quote-based | Best for 1,000+ pcs |
| **Summit Interconnect** | Multiple US sites | Defense/aerospace focused | Quote-based | Defense pricing |
| **AT&S** | Austria | High-tech PCBs, HDI | Quote-based | Competitive EU pricing |
| **Unimicron** | Taiwan | High-volume | N/A | Very competitive (allied nation) |
| **JLCPCB / PCBWay** | China | Cheapest | $50-200 | ❌ **Not NDAA compliant** |

**Cost premium for US/allied fab:** Expect 3-10× cost vs. Chinese fabrication for prototypes; 2-4× for production volumes. For a 6-8 layer avionics board:
- Chinese fab: ~$2-5/board at qty 500
- US fab: ~$12-25/board at qty 500
- This adds ~$10-20/unit — negligible vs. total BOM

### 3.4 What Blue UAS Companies Do

Based on publicly available information:
- **Skydio** (X2, X10): Fully custom electronics, designed and largely assembled in USA. Blue UAS listed.
- **Shield AI** (Nova 2, V-BAT): Custom avionics. Blue UAS listed.
- **Teal Drones / FLIR**: Custom boards, assembled in USA. Blue UAS listed.
- **Altavian**: Custom electronics. Blue UAS listed.
- **Vantage Robotics**: Custom design. Blue UAS listed.

**Pattern is clear:** No Blue UAS company uses off-the-shelf Pixhawk with a Holybro label on it. Custom design with documented supply chain is the standard.

---

## 4. Weight and Form Factor Benefits

### 4.1 Weight Analysis

| Item | COTS Weight | Custom Integrated Weight | Savings |
|------|-------------|------------------------|---------|
| Pixhawk 6X (FC module + baseboard) | 54-104g | — | — |
| 8× individual ESCs (with housings, heatsinks) | 8 × 15-25g = 120-200g | — | — |
| Power module + PDB | 30-50g | — | — |
| GPS module (on carrier board with housing) | 40-60g | — | — |
| Wiring harness (COTS interconnects) | 50-100g | — | — |
| **COTS Total** | **~295-515g** | | |
| Custom integrated board (FC + 8× ESC + power + GPS) | — | ~120-200g | — |
| Reduced wiring (direct connections) | — | ~15-30g | — |
| **Custom Total** | | **~135-230g** | |
| **Weight Savings** | | | **~160-285g** |

**Estimated weight savings: 150-250g**, representing **5-9% of the 2.9kg AUW**. This translates directly to:
- ~1-3 minutes additional flight time (rough estimate, depends on power system)
- Alternatively, capacity for additional payload weight
- Better power-to-weight ratio and agility

### 4.2 Form Factor Impact

- **Volume reduction:** Eliminating 8 individual ESC housings + Pixhawk housing + power module housing saves approximately 200-400 cm³ of volume
- **Cassette form factor:** A single integrated board could be designed specifically for the cassette dimensions, eliminating wasted space from rectangular COTS module form factors that don't match the ducted airframe geometry
- **Thermal management:** Integrated design allows purpose-built heatsinking using the airframe/duct structure rather than individual ESC heatsinks
- **Vibration isolation:** Single board means single isolation mounting system vs. multiple isolated modules

---

## 5. Risks and Downsides

### 5.1 Development Timeline

| Milestone | Duration | Notes |
|-----------|----------|-------|
| Requirements & architecture | 4-6 weeks | |
| Schematic design | 6-10 weeks | Complex mixed-signal + power |
| PCB layout | 4-8 weeks | 6-8 layer, thermal analysis needed |
| Prototype fab + assembly | 3-6 weeks | US fab, 2-3 week turn typical |
| Bring-up & debug | 4-8 weeks | Expect issues on Rev 1 |
| Rev 2 design & fab | 6-10 weeks | Based on Rev 1 learnings |
| Rev 2 testing & validation | 4-6 weeks | |
| Firmware integration | 4-8 weeks | PX4/ArduPilot porting (ongoing) |
| **Total to flight-ready custom board** | **~9-15 months** | Assumes 2-3 board revisions |

**Risk:** This timeline can slip significantly if:
- ESC integration has thermal or EMC issues (high-current switching near sensitive IMUs)
- Supply chain delays on key ICs
- Firmware porting uncovers hardware bugs
- Regulatory testing reveals compliance issues

### 5.2 Hardware Iteration Speed

| Factor | COTS Advantage | Custom Advantage |
|--------|---------------|-----------------|
| Swapping a failed ESC | Minutes (unplug, plug new one) | Board-level repair or full board replacement |
| Trying a different IMU | Buy different FC module | Requires board redesign |
| Scaling motor count | Buy more ESCs | Requires new board revision |
| Field repair | Swap modules | More complex; carry spare boards |
| Testing different configs | Mix and match | Fixed configuration per board rev |

### 5.3 Certification & Testing Burden

- **EMC testing:** Custom boards need FCC Part 15 testing (~$5K-15K per revision)
- **Environmental testing:** Vibration, temperature, humidity — especially critical for flight-safety avionics
- **PX4/ArduPilot compatibility:** Must maintain compatibility with open-source autopilot firmware; may need upstream contributions
- **Quality assurance:** Need to establish incoming inspection, functional test fixtures, burn-in procedures

### 5.4 Supply Chain Risk

| Risk | COTS | Custom |
|------|------|--------|
| Single-source dependency | Multiple module vendors available | Single custom design; if board has issues, no fallback |
| IC availability | Module vendor manages | You manage; STM32 shortages during 2021-2023 were painful |
| Obsolescence | Module vendor handles redesign | You must redesign when ICs go EOL |
| Second source | Buy from different module brand | Must design in second-source compatible ICs |

**Mitigation:** Design with second-source ICs where possible (e.g., ICM-42688-P and BMI088 as IMU options; both are Pixhawk-standard). Keep COTS design as fallback during transition.

### 5.5 Expertise Requirements

- **Minimum:** 1 senior hardware engineer (analog/mixed-signal + power electronics experience) — $150K-200K/year fully loaded
- **Ideal:** Hardware engineer + PCB layout specialist + firmware engineer with PX4/ArduPilot experience
- **Alternative:** Contract design house (e.g., Titoma, Cardinal Peak, or specialized drone avionics consultancies) — $150K-300K project cost but no long-term staff commitment
- **Ongoing:** Need hardware engineering capacity for revisions, production support, supply chain management

---

## 6. Phased Approach Recommendation

### Phase 1 — P1 Prototype (Now → 6 months)
**Strategy: Stay 100% COTS**

| Action | Rationale |
|--------|-----------|
| Keep Pixhawk 6X + individual ESCs + COTS everything | Focus on flight dynamics, software, mission capability — not custom hardware |
| Document all component sources for NDAA | Build the compliance documentation now |
| Begin hardware engineer recruiting or design house RFP | Lead time on talent/contracts |
| Commission thermal and EMC analysis of current design | Understand integration challenges before committing |

**Cost:** $0 additional NRE  
**Risk:** None — maintains current development velocity

### Phase 2 — P2 Small Production (6-18 months, targeting 50-100 units)
**Strategy: Custom ESC + Power Board; COTS FC + GPS**

| Action | Rationale |
|--------|-----------|
| Design custom 8-in-1 ESC + power distribution board | **Highest cost/weight impact**: eliminates 8 ESC modules ($320-480) and PDB ($30-50); saves ~100-150g |
| Keep Pixhawk 6X as flight controller | Proven, low risk; PX4 firmware "just works" |
| Keep COTS GPS, ADS-B, Remote ID modules | Lower cost/weight impact; defer integration risk |
| Design custom Jetson Orin Nano carrier board | Tailored to cassette form factor; integrate power, USB, CSI connectors for your specific sensors |

**Estimated NRE:** $80K-150K (ESC board + carrier board)  
**Per-unit savings:** ~$200-400 (primarily ESC consolidation + custom carrier)  
**Weight savings:** ~80-150g  
**Breakeven:** ~300-500 units  

### Phase 3 — GA Volume (18-36 months, targeting 500+ units/year)
**Strategy: Fully Integrated Avionics Board**

| Action | Rationale |
|--------|-----------|
| Design integrated FC + ESC + GPS + Remote ID + power board | Maximum cost and weight reduction |
| Custom Jetson carrier board v2 with ADS-B integration | Further consolidation |
| US/allied-only PCB fabrication and assembly | Complete NDAA compliance story |
| Apply for Blue UAS / Green UAS certification | Requires documented supply chain — custom design enables this |

**Estimated NRE:** $150K-250K additional (on top of Phase 2)  
**Per-unit savings:** ~$800-1,500 vs. all-COTS  
**Weight savings:** ~200-300g  
**Breakeven:** ~200-350 cumulative additional units  

### Priority Ranking: What to Customize First

| Priority | Subsystem | Cost Impact | Weight Impact | NDAA Impact | Complexity |
|----------|-----------|-------------|---------------|-------------|------------|
| 1 | **8-in-1 ESC + PDB** | High ($350-500/unit) | High (100-150g) | Medium | Medium-High |
| 2 | **Jetson Orin Nano carrier board** | Medium ($50-100/unit) | Medium (30-50g) | Medium | Medium |
| 3 | **Flight controller (FC)** | Medium ($150-200/unit) | Medium (40-80g) | High | Medium |
| 4 | **GPS/RTK integration** | Low-Medium ($50-100/unit) | Low (20-30g) | Low | Low |
| 5 | **Remote ID integration** | Low ($150-250/unit) | Low (10-20g) | Medium | Low |
| 6 | **ADS-B integration** | Low ($100-200/unit) | Low (10-20g) | Low | Medium |

---

## 7. Financial Summary

### Scenario: 500 Units Over 3 Years

| | All COTS | Phased Custom (Recommended) | Full Custom from Start |
|---|---------|---------------------------|----------------------|
| NRE investment | $0 | $230K-400K (phased) | $300K-500K (upfront) |
| Per-unit BOM (electronics) | ~$2,350 | ~$1,400-1,800 (at maturity) | ~$1,100-1,500 |
| Total electronics cost (500 units) | $1,175,000 | $930K-1,100K | $850K-1,250K |
| **Net cost (incl. NRE)** | **$1,175,000** | **$1,160K-1,500K** | **$1,150K-1,750K** |
| Breakeven point | — | ~unit 300-400 | ~unit 250-400 |

**At 500 units, phased custom roughly breaks even with COTS.** The real advantages are:
1. **NDAA/Blue UAS eligibility** — may be *required* for government contracts
2. **Weight savings** improving product performance
3. **Competitive moat** — harder for competitors to replicate custom hardware
4. **Scalability** — cost curve improves dramatically beyond 500 units

### Scenario: 1,000+ Units

At 1,000 units, custom integration saves **$400K-700K** net of NRE vs. all-COTS. This is the compelling case.

---

## 8. Key Recommendations

1. **Do NOT delay P1 for custom hardware.** Fly with COTS. Iterate on flight dynamics and mission software.

2. **Start hiring/contracting a hardware engineer NOW.** Lead time on good embedded hardware talent is 3-6 months. Look for experience with: motor drive / ESC design, mixed-signal PCB layout, PX4/ArduPilot ecosystem.

3. **Custom 8-in-1 ESC board is the highest-impact first project.** Biggest cost savings, biggest weight savings, well-understood design space (FPV industry has mature 4-in-1 designs to reference).

4. **Custom Jetson Orin Nano carrier board is a quick win.** NVIDIA provides reference designs; many design houses offer carrier board design as a service. Tailoring this to the cassette form factor is straightforward.

5. **Pursue US/allied PCB fabrication from the start of custom work.** The cost premium (~$10-20/board) is negligible relative to BOM, and it's essential for the NDAA story. Sierra Circuits (Sunnyvale, CA) and Advanced Circuits (Aurora, CO) are proven for prototype-to-production drone avionics.

6. **Keep fallback to COTS.** Design custom boards with standard connectors where possible so you can revert to COTS modules during supply chain disruptions.

7. **Budget $250K-400K total NRE over 18-24 months** for the phased approach, with the goal of having a fully integrated avionics board ready for GA.

---

## Appendix A: Key Component Pricing Reference

*Prices from DigiKey/Mouser, March 2026. Qty 1 / qty 100 where available.*

| Component | Part Number | Qty 1 Price | Qty 100 Price | Manufacturer HQ |
|-----------|-------------|-------------|---------------|-----------------|
| MCU | STM32H753VIT6 | ~$14.50 | ~$12.00 | STMicro (CH/FR) |
| IMU | ICM-42688-P | ~$5-7 | ~$4-5 | TDK InvenSense (JP/US) |
| IMU (alt) | ICM-45686 | ~$5-6 | ~$4-5 | TDK InvenSense (JP/US) |
| Barometer | MS5611-01BA03 | ~$10 | ~$8 | TE Connectivity (CH) |
| GPS/RTK | ZED-F9P-04B | ~$199 | ~$130-175 | u-blox (CH) |
| Magnetometer | BMM150 | ~$2-3 | ~$1.50-2 | Bosch (DE) |
| BLE SoC | nRF52840 | ~$4-6 | ~$3-4 | Nordic Semi (NO) |
| Gate Driver | DRV8320HRTAT | ~$3-4 | ~$2-3 | Texas Instruments (US) |
| MOSFET (ESC) | BSC030N08NS5 | ~$1.50-2 | ~$1-1.50 | Infineon (DE) |
| Orin Nano 8GB | 900-13767-0030-000 | ~$299 | ~$249-299 | NVIDIA (US) |

## Appendix B: Sources

- Holybro Pixhawk 6X product page: https://holybro.com/products/pixhawk-6x
- Auterion Skynode S: https://auterion.com/product/skynode-s/
- BotBlox NDAA Compliance Guide: https://botblox.io/blog/designing-ndaa-and-executive-order-13981-compliant-drone-components-a-short-guide/
- PX4 Pixhawk 6X Documentation: https://docs.px4.io/main/en/flight_controller/pixhawk6x
- Titoma NRE Calculator: https://titoma.com/nre/
- PCBSync Drone PCB Design Guide: https://pcbsync.com/drone-pcb-design/
- Sierra Circuits PCB Fabrication: https://www.protoexpress.com/
- DigiKey component pricing: https://www.digikey.com
- NDAA Compliant Drone Information: https://advexure.com/pages/ndaa-compliant-blue-uas-drones
- Blue UAS Cleared List: https://www.diu.mil/blue-uas

---

## Changelog

- **2026-03-11:** Corrected Jetson Orin Nano 8GB SOM price from $499 to **$299** ([NVIDIA MSRP](https://www.cnx-software.com/2022/09/21/199-nvidia-jetson-orin-nano-system-on-module-delivers-up-to-40-tops/)). Corrected ZED-F9P-04B price from $100-130 to **$199** ([DigiKey](https://www.digikey.com/en/products/detail/u-blox/ZED-F9P-04B/15761778)). Corrected Appendix A Orin Nano price from $399-499 to $299. Clarified Tekko32 as 4-in-1 ESC board (not individual ESC). Updated electronics subtotal and per-drone BOM accordingly.
