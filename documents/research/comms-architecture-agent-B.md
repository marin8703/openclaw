# Hummingbird Swarm Communications Architecture

**Version:** 1.0  
**Date:** 2026-03-04  
**Author:** Agent B  
**Classification:** Internal Engineering Document

---

## Table of Contents

1. [Physical/Hardware Layer](#1-physicalhardware-layer)
2. [Transport Abstraction Layer](#2-transport-abstraction-layer)
3. [Swarm Protocol](#3-swarm-protocol)
4. [Network Architecture](#4-network-architecture)
5. [Resilience & Degradation](#5-resilience--degradation)
6. [Cloud & Integration Layer](#6-cloud--integration-layer)
7. [Future-Proofing](#7-future-proofing)

---

## 1. Physical/Hardware Layer

### 1.1 Radio Interfaces

#### Primary Mesh: Doodle Labs Mesh Rider Mini-OEM 2.4 GHz (RM-2450-12M3)

| Parameter | Value |
|-----------|-------|
| Frequency | 2400–2482 MHz (ISM band) |
| Modulation | COFDM, BPSK to 64-QAM adaptive |
| Channel BW | 3/5/10/20 MHz software-selectable |
| Throughput | 80 Mbps @ 20 MHz BW, 40 Mbps @ 10 MHz, 20 Mbps @ 5 MHz |
| MIMO | 2×2 MIMO |
| Range | >10 km LOS (field-tested >100 km with directional antennas) |
| TX Power | Up to +30 dBm (1W) ATPC |
| Encryption | AES-128 (full throughput) / AES-256 (12 Mbps max) — FIPS 140-3 optional |
| Interfaces | Ethernet, USB, UART |
| Mesh | Self-forming/self-healing MANET |
| Weight | 36.5 g (mini-OEM module) |
| Temp Range | -40°C to +85°C (MIL-spec) |
| Cost | ~$1,450 |
| Antenna | 2× RP-SMA, external dipole or patch |

**Source:** [Doodle Labs Tech Library](https://techlibrary.doodlelabs.com/doodle-labs-mini-oem-mesh-rider-radio-24002482-mhz)

**Role:** Primary data link for all swarm communications — telemetry, commands, video, inter-drone mesh. The built-in MANET routing handles multi-hop automatically. URLLC channel carries C2, while optimized video channel handles streaming.

#### Backup Long-Range: RFD900x 900 MHz

| Parameter | Value |
|-----------|-------|
| Frequency | 902–928 MHz (USA ISM) |
| Modulation | FHSS (frequency hopping spread spectrum) |
| Data Rate | Up to 500 kbps air rate (64 kbps default) |
| TX Power | 1W (+30 dBm), adjustable in 1 dB steps |
| Sensitivity | -121 dBm at low rates |
| Range | >40 km LOS (80 km demonstrated) |
| Interface | UART (TTL 3.3V), 6× GPIO |
| Antenna | 2× RP-SMA (diversity switching) |
| Weight | 14.5 g |
| Size | 30×57×12.8 mm |
| Power | 5V, 800 mA peak |
| Temp Range | -40°C to +85°C |
| Cost | ~$118 |

**Source:** [SpektreWorks RFD900x](https://spektreworks.com/product/rfd-900x-modem/), [RFD900x Datasheet](https://files.rfdesign.com.au/Files/documents/RFD900x%20DataSheet%20V1.1.pdf)

**Role:** Emergency backbone. When 2.4 GHz mesh fails (jamming, interference, range), the 900 MHz link maintains essential C2 telemetry. Low bandwidth but extreme range and penetration. Used for:
- Heartbeat/status (compressed telemetry at 10 Hz)
- Emergency commands (RTB, abort, regroup)
- Flight leader aggregated status relay
- MAVLink pass-through to PX4 flight controller

#### Cellular Backhaul: Sierra Wireless EM9291

| Parameter | Value |
|-----------|-------|
| Technology | 5G NR Sub-6 GHz + LTE Cat 20 fallback |
| DL Speed | Up to 3.5 Gbps (5G) |
| UL Speed | Up to 900 Mbps (5G) |
| Interface | M.2 (B-Key), USB 3.1, PCIe Gen3 |
| GNSS | Integrated (GPS, GLONASS, BeiDou, Galileo) |
| Bands | All major NA 5G NR and LTE bands |
| SIM | Nano-SIM or eSIM |
| Cost | ~$250 |

**Source:** [Sierra Wireless EM9291](https://www.sierrawireless.com/iot-modules/5g-modules/em9291/)

**Role:** Cloud backhaul for video offload, mission data upload, remote operator access. Also serves as **mesh bridge** — a drone with cellular coverage can relay data from mesh-only drones to the cloud. Not relied on for real-time C2 (latency too variable).

### 1.2 IR Transceivers

#### Precision Landing & Docking

| Component | Specification |
|-----------|--------------|
| Emitters | 4× 940nm IR LEDs on Nest docking pads, pulsed at 38 kHz carrier |
| Receivers | 2× TSOP38238 IR receivers on drone belly (forward/aft) |
| Range | 0.5–5 m effective |
| Data Rate | 2400 baud (IrDA SIR-compatible) |
| Protocol | Custom pulse-position modulation encoding pad ID + alignment vector |
| Interface | GPIO on FPGA (CrossLink-NX handles demodulation in fabric) |

Each Nest docking pad emits a unique 8-bit pad ID at 10 Hz. The drone's belly-mounted IR receivers triangulate position relative to pad center. The FPGA computes lateral offset and rotation at 100 Hz, feeding corrections to the PX4 precision landing controller via uORB `landing_target_pose`.

#### Close-Range Drone-to-Drone ID

| Component | Specification |
|-----------|--------------|
| Transceiver | 2× VISHAY TFBS4711 (850nm, IrDA compliant) on lateral faces |
| Range | 0–2 m |
| Data Rate | 115.2 kbps |
| Purpose | Visual-line identity verification at close range |

When drones are within 2 m (formation flight, docking queue), they exchange encrypted identity beacons via IR. This provides a side-channel authentication that's immune to RF spoofing — a drone claiming to be ID 7 on radio must also respond correctly on IR when physically proximate.

### 1.3 LED Signaling System

Each drone has a programmable LED array: **4× high-brightness RGB LEDs** (one per arm tip) + **1× bottom-facing status ring** (8× addressable WS2812B LEDs).

#### Arm LEDs — External Signaling

| Pattern | Color | Meaning |
|---------|-------|---------|
| Solid | Green | Nominal flight, on mission |
| Solid | Blue | Hovering/loitering |
| Solid | Red | Emergency / low battery |
| Solid | White | Landing/docking |
| Slow pulse (1 Hz) | Yellow | Awaiting command / standby |
| Fast pulse (4 Hz) | Red | Critical failure, will auto-land |
| Alternating Red/Blue | — | Public safety identification (first responder mode) |
| Chase pattern | Cyan | Flight leader indicator |
| Solid | Purple | Charging on Nest |
| Off | — | Stealth mode / powered down |

#### Bottom Status Ring — Ground-Facing

| Pattern | Meaning |
|---------|---------|
| Rotating white | Boot sequence |
| Solid green ring | GPS lock, ready for takeoff |
| Pulsing orange segments | Sensor calibration in progress |
| Solid red ring | No-fly / geofence violation |
| Directional arrow (white) | Indicates heading to ground observers |

#### ROS2 Interface

```
Topic: /hb/led/command
Message: hummingbird_msgs/msg/LEDCommand
  uint8 target          # 0=all, 1-4=arm, 5=ring
  uint8 r, g, b         # color
  uint8 pattern         # enum: SOLID, PULSE_SLOW, PULSE_FAST, CHASE, ALTERNATE, OFF
  float32 brightness    # 0.0–1.0
```

LEDs are driven by the FPGA via SPI to WS2812B driver, keeping LED timing off the Jetson's real-time path.

### 1.4 Internal Bus Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    JETSON ORIN NX (Main Compute)                 │
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │ ROS2    │  │ Comms   │  │ Mission  │  │ Video Pipeline   │ │
│  │ Runtime │  │ Manager │  │ Executor │  │ (GStreamer+HW enc)│ │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └────────┬──────────┘ │
│       │            │            │                   │            │
│  ═══ Iceoryx Zero-Copy Shared Memory ══════════════════════════ │
│       │            │            │                   │            │
├───────┼────────────┼────────────┼───────────────────┼────────────┤
│       │            │            │                   │            │
│  ┌────┴────┐  ┌────┴────┐  ┌───┴────┐         ┌───┴─────┐     │
│  │Ethernet │  │ USB 3.1 │  │ UART   │         │ PCIe    │     │
│  │(GbE)    │  │         │  │(ttyS*) │         │ Gen3    │     │
│  └────┬────┘  └────┬────┘  └───┬────┘         └───┬─────┘     │
│       │            │            │                   │            │
└───────┼────────────┼────────────┼───────────────────┼────────────┘
        │            │            │                   │
   ┌────┴────┐  ┌────┴─────┐ ┌───┴──────┐      ┌────┴──────┐
   │Doodle   │  │CrossLink │ │ ARKV6X   │      │EM9291     │
   │Labs     │  │NX FPGA   │ │ FC       │      │5G Module  │
   │Mesh     │  │          │ │(PX4)     │      │           │
   │Rider    │  │Sensors   │ │          │      │           │
   │         │  │IR, LEDs  │ │CAN bus   │      │           │
   └─────────┘  └──────────┘ └────┬─────┘      └───────────┘
                                   │
                              ┌────┴────┐
                              │RFD900x  │
                              │(UART)   │
                              └─────────┘
```

**Connection Details:**

| Link | Interface | Speed | Purpose |
|------|-----------|-------|---------|
| Jetson ↔ Doodle Labs | GbE (Ethernet) | 1 Gbps | Primary mesh data path |
| Jetson ↔ CrossLink-NX FPGA | USB 3.1 + SPI | 5 Gbps / 50 MHz | Sensor data, IR control, LED control |
| Jetson ↔ ARKV6X FC | UART (TELEM1, /dev/ttyS6) | 921600 baud | MAVLink, flight commands |
| Jetson ↔ EM9291 | PCIe Gen3 x1 | ~1 Gbps | Cellular data |
| ARKV6X ↔ RFD900x | UART (TELEM2, /dev/ttyS4) | 57600 baud | Backup telemetry link |
| FPGA ↔ IR transceivers | GPIO/SPI | N/A | IR modulation/demodulation |
| FPGA ↔ LEDs | SPI | 800 kHz | WS2812B protocol |
| ARKV6X ↔ ESCs | DroneCAN (CAN bus) | 1 Mbps | Motor control |

### 1.5 Nest Ground Station Hardware

The Nest is both a physical docking/charging station and the strategic compute hub.

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Doodle Labs Mesh Rider OEM 2.4 GHz (×2) | Same radio, higher-gain antennas (8 dBi sector) | Swarm mesh base station, spatial diversity |
| RFD900x (×2) | Diversity pair | Emergency C2 backbone |
| Sierra Wireless EM9291 | With external MIMO antenna | Primary cloud backhaul |
| Ethernet switch | Managed, 16-port GbE | Internal wiring |
| Edge compute | NVIDIA Jetson AGX Orin (64GB) | Mission planning, video aggregation, AI |
| IR emitter arrays | 30× pad assemblies (per Section 1.2) | Precision landing guidance |
| UPS | 2000 Wh LiFePO4 | 4+ hours autonomous operation |
| GPS/RTK base | u-blox F9P with survey-in | RTK corrections for swarm |
| Cellular router | Cradlepoint or Sierra RV55 (backup) | Redundant cloud link |

**Antenna Placement — Nest:**
- 2× Doodle Labs sector antennas mounted on telescoping mast (3–5 m AGL), 120° sectors, together covering 240° (third sector optional)
- RFD900x antennas: vertically polarized dipoles, mast-mounted, diversity spacing ≥λ/2 (16 cm)
- Cellular: external MIMO panel antenna, mast-mounted

### 1.6 Antenna Placement on Drone Airframe

For a quadrotor with ~500mm wheelbase:

- **Doodle Labs (2.4 GHz):** 2× PCB patch antennas embedded in upper fuselage shell, oriented upward at 30° cant for hemispherical coverage above horizon. Separation ≥6 cm (λ/2 at 2.45 GHz) for MIMO decorrelation. Placement avoids carbon fiber shadowing by using fiberglass antenna windows.
- **RFD900x (900 MHz):** 1× quarter-wave whip (8.2 cm) on landing gear strut, vertically polarized, ground plane provided by FC/battery tray. Second diversity antenna: wire antenna routed along opposite strut.
- **EM9291 (Cellular):** 2× embedded flex PCB antennas (MIMO) in lower fuselage shell, oriented downward/lateral for ground-tower coverage.
- **IR:** Belly-mounted, clear line of sight downward through transparent window in bottom shell.

**RF Isolation Considerations:**
- Minimum 10 cm separation between 2.4 GHz and 900 MHz antennas
- Cellular antennas on opposite side of fuselage from mesh antennas
- FPGA clock harmonics filtered with EMI shielding on FPGA module
- Carbon fiber frame acts as partial ground plane — all antenna designs account for this

---

## 2. Transport Abstraction Layer

### 2.1 Unified Transport Interface

All radio links implement a common `ITransport` interface, making the swarm protocol completely transport-agnostic.

```cpp
// File: hb_comms/include/hb_comms/transport/itransport.hpp

namespace hb::comms {

enum class TransportId : uint8_t {
    MESH_2G4 = 0,   // Doodle Labs 2.4GHz
    LTE_5G   = 1,   // Sierra Wireless EM9291
    RF900    = 2,    // RFD900x
    IR       = 3,    // IR transceiver
};

enum class QoS : uint8_t {
    BEST_EFFORT    = 0,  // Fire and forget
    RELIABLE       = 1,  // ACK required, retransmit
    REALTIME       = 2,  // Low latency, drop if stale
    CRITICAL       = 3,  // Reliable + highest priority
};

struct LinkMetrics {
    float rssi_dbm;          // Received signal strength
    float snr_db;            // Signal-to-noise ratio
    float packet_loss_pct;   // Rolling 10s window
    uint32_t latency_us;     // Round-trip time
    uint32_t bandwidth_bps;  // Available throughput
    uint32_t jitter_us;      // Latency variance
    uint8_t hop_count;       // Mesh hops to destination
    float link_score;        // Composite 0.0–1.0
};

class ITransport {
public:
    virtual ~ITransport() = default;

    // Send raw bytes to a destination (drone ID or broadcast)
    virtual bool send(uint16_t dest_id, 
                      std::span<const uint8_t> payload,
                      QoS qos) = 0;

    // Register receive callback
    virtual void on_receive(
        std::function<void(uint16_t src_id, 
                           std::span<const uint8_t> payload)> cb) = 0;

    // Link quality
    virtual LinkMetrics get_metrics(uint16_t dest_id = 0) const = 0;
    virtual bool is_available() const = 0;
    virtual TransportId id() const = 0;

    // Bandwidth reservation for video streams
    virtual bool reserve_bandwidth(uint32_t bps) = 0;
    virtual void release_bandwidth(uint32_t reservation_id) = 0;
};

} // namespace hb::comms
```

### 2.2 Link Quality Scoring

Each transport continuously computes a composite link score:

```
link_score = w_rssi * normalize(rssi, -100, -30)
           + w_snr  * normalize(snr, 0, 40)
           + w_loss * (1.0 - packet_loss_pct / 100.0)
           + w_lat  * normalize(1.0 / latency_ms, 0, 1)
           + w_bw   * normalize(bandwidth_bps, 0, max_bw)
```

**Default weights:**

| Weight | Value | Rationale |
|--------|-------|-----------|
| w_rssi | 0.15 | Basic signal presence |
| w_snr | 0.20 | Quality indicator |
| w_loss | 0.30 | Most impactful for reliability |
| w_lat | 0.20 | Critical for C2 |
| w_bw | 0.15 | Important for video but not C2 |

Score is recomputed every 500 ms per link. Published on:
```
Topic: /hb/comms/link_quality
Message: hummingbird_msgs/msg/LinkQuality
  uint8 transport_id
  float32 link_score
  float32 rssi_dbm
  float32 snr_db
  float32 packet_loss_pct
  uint32 latency_us
  uint32 bandwidth_bps
```

### 2.3 Automatic Failover Logic

**Priority Stack (highest to lowest):**

1. **Doodle Labs 2.4 GHz Mesh** — Primary for all traffic
2. **Sierra Wireless LTE/5G** — Video offload and cloud backhaul
3. **RFD900x 900 MHz** — Emergency C2 only

**Failover Rules:**

```python
# Pseudocode for transport selection
def select_transport(msg_type, dest_id):
    transports = get_available_transports(dest_id)
    
    if msg_type in [EMERGENCY, HEARTBEAT, RTB]:
        # Critical messages go on ALL available transports simultaneously
        return transports  
    
    if msg_type == VIDEO_STREAM:
        # Video only on high-bandwidth links
        candidates = [t for t in transports if t.bandwidth_bps > 1_000_000]
        if not candidates:
            return DROP  # Don't send video on constrained links
        return best_by_score(candidates)
    
    if msg_type in [TELEMETRY, COMMAND, MISSION_UPDATE]:
        # C2 traffic: prefer mesh, failover to cellular, then 900
        mesh = get_transport(MESH_2G4)
        if mesh and mesh.link_score > 0.3:
            return mesh
        lte = get_transport(LTE_5G)
        if lte and lte.link_score > 0.2:
            return lte
        rf900 = get_transport(RF900)
        if rf900 and rf900.link_score > 0.1:
            return rf900
        return None  # All links dead — enter autonomous mode
```

**Failover Timing:**
- Link declared degraded: score < 0.3 for >2 seconds
- Link declared failed: score < 0.1 for >1 second, or no packets received for >3 seconds
- Failover execution: <100 ms (pre-computed backup routes)
- Recovery: link must sustain score > 0.4 for >5 seconds before re-promotion

### 2.4 Bandwidth Allocation & QoS

**Per-drone bandwidth budget on 2.4 GHz mesh (20 MHz channel, 80 Mbps aggregate):**

With 30 drones sharing the mesh, effective per-node throughput with TDMA-like contention:

| Traffic Class | Priority | Per-Drone Allocation | Total (30 drones) |
|---------------|----------|---------------------|-------------------|
| C2 Commands (down) | CRITICAL | 5 kbps | 150 kbps |
| Telemetry (up) | REALTIME | 20 kbps @ 10 Hz | 600 kbps |
| Heartbeat/Status | RELIABLE | 2 kbps @ 1 Hz | 60 kbps |
| Video (up, when active) | BEST_EFFORT | 2 Mbps (H.265) | 6 Mbps (3 active streams) |
| Sensor data (up) | BEST_EFFORT | 50 kbps | 1.5 Mbps |
| Mission updates | RELIABLE | 10 kbps (burst) | 300 kbps |
| Flight leader aggregation | RELIABLE | 100 kbps | 500 kbps (5 leaders) |
| **Total** | | | **~9.1 Mbps** |

This leaves ~70 Mbps headroom for burst video, mesh overhead, retransmissions, and multi-hop relay. The Doodle Labs URLLC channel ensures C2 traffic is never starved.

**QoS Implementation:**
The Doodle Labs Mesh Rider natively supports QoS via its URLLC channel. We map:
- `CRITICAL` / `REALTIME` → URLLC channel (guaranteed <10 ms latency)
- `RELIABLE` → Standard channel with ACK
- `BEST_EFFORT` → Standard channel, no ACK

### 2.5 Video Streaming Architecture

```
Camera (MIPI CSI) → Jetson HW Encoder (NVENC, H.265)
    → RTP/UDP stream → Comms Manager
        ├─ If mesh bandwidth available: → Doodle Labs optimized video channel
        ├─ If cellular available: → LTE direct to cloud (preferred for 4K)
        └─ If constrained: → Reduce resolution (1080p→720p→480p→MJPEG keyframes)
```

**Video Pipeline ROS2 Node:**
```
Node: /hb/video/streamer
Subscribes: /hb/camera/raw (sensor_msgs/msg/Image)
Publishes: /hb/video/compressed (sensor_msgs/msg/CompressedImage)
Parameters:
  - resolution: [1920, 1080]  # adaptive
  - bitrate: 2000000           # adaptive, bps
  - fps: 30                    # adaptive
  - codec: "h265"
```

**Adaptive Bitrate Control:**
The comms manager monitors available bandwidth and adjusts video encoding parameters every 2 seconds:

| Available BW | Resolution | Bitrate | FPS |
|-------------|-----------|---------|-----|
| >5 Mbps | 1080p | 4 Mbps | 30 |
| 2–5 Mbps | 720p | 2 Mbps | 30 |
| 1–2 Mbps | 480p | 1 Mbps | 15 |
| 0.5–1 Mbps | 480p | 500 kbps | 10 |
| <500 kbps | Keyframes only | 100 kbps | 1 |

### 2.6 Latency Budgets

| Path | Transport | Target Latency | Max Acceptable |
|------|-----------|---------------|----------------|
| Nest → Drone C2 command | 2.4 GHz mesh | 5 ms | 50 ms |
| Drone → Nest telemetry | 2.4 GHz mesh | 10 ms | 100 ms |
| Drone → Drone (same mesh) | 2.4 GHz mesh, 1-hop | 3 ms | 20 ms |
| Drone → Cloud (video) | LTE/5G | 30 ms | 200 ms |
| Drone → Nest (900 MHz) | RFD900x | 50 ms | 500 ms |
| Nest → Cloud | LTE/fiber | 20 ms | 100 ms |
| Obstacle avoidance loop | Internal (Jetson) | 0.5 ms | 5 ms |
| Flight controller commands | UART to PX4 | 1 ms | 10 ms |

---

## 3. Swarm Protocol — HiveLink Binary Protocol

### 3.1 Message Header Format

All HiveLink messages share a common 24-byte header:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    MAGIC (0x48 0x42)          | VER |  FLAGS  | MSG_TYPE      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         SOURCE_ID             |       DEST_ID                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       SEQUENCE_NUMBER                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       TIMESTAMP_US                            |
|                       (64-bit microseconds since epoch)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         PAYLOAD_LEN           |    TTL   |    HOP_COUNT      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Total header: 24 bytes
```

**Field Details:**

| Field | Bits | Description |
|-------|------|-------------|
| MAGIC | 16 | `0x4842` ("HB") — sync marker |
| VER | 3 | Protocol version (0–7), current = 1 |
| FLAGS | 5 | Bit 0: encrypted, Bit 1: compressed, Bit 2: ACK requested, Bit 3: fragment, Bit 4: reserved |
| MSG_TYPE | 8 | Message type enum (see catalog) |
| SOURCE_ID | 16 | Sender drone ID (0x0000 = Nest, 0x0001–0x00FF = drones, 0xFFFF = broadcast) |
| DEST_ID | 16 | Destination (0xFFFF = broadcast, 0xFFFE = multicast to flight group) |
| SEQUENCE_NUMBER | 32 | Per-source monotonic counter, wraps |
| TIMESTAMP_US | 64 | Microseconds since Unix epoch (GPS-synced) |
| PAYLOAD_LEN | 16 | Payload length in bytes (max 65535) |
| TTL | 8 | Time-to-live for multi-hop (max 15 for 30-drone swarm) |
| HOP_COUNT | 8 | Incremented each relay hop |

**After header, if FLAGS.encrypted is set:**

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     AES-256-GCM NONCE (12 bytes)              |
|                                                               |
|                                               +-+-+-+-+-+-+-+-+
|                                               |               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+               |
|                     ENCRYPTED PAYLOAD (variable)              |
|                          ...                                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     GCM AUTH TAG (16 bytes)                    |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Total overhead per encrypted message: 24 (header) + 12 (nonce) + 16 (tag) = **52 bytes**.

### 3.2 Complete Message Catalog

#### Category 0x0_: System & Lifecycle

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0x01 | `HEARTBEAT` | Any→Any | BEST_EFFORT | drone_id(2), state(1), battery_pct(1), gps_fix(1), timestamp(8) — 13 bytes |
| 0x02 | `IDENTIFY` | Drone→Any | RELIABLE | drone_id(2), hw_version(2), sw_version(4), capabilities_bitmask(4), public_key_hash(32) — 44 bytes |
| 0x03 | `AUTH_CHALLENGE` | Nest→Drone | RELIABLE | challenge_nonce(32) |
| 0x04 | `AUTH_RESPONSE` | Drone→Nest | RELIABLE | signed_nonce(64), certificate_chain_hash(32) |
| 0x05 | `REBOOT` | Nest→Drone | CRITICAL | reboot_delay_ms(4), flags(1) |
| 0x06 | `SHUTDOWN` | Nest→Drone | CRITICAL | shutdown_delay_ms(4) |
| 0x07 | `TIME_SYNC` | Nest→Broadcast | BEST_EFFORT | gps_timestamp_us(8), nest_seq(4) |
| 0x08 | `FIRMWARE_INFO` | Drone→Nest | RELIABLE | component(1), version(4), hash(32) |

#### Category 0x1_: Telemetry

| ID | Name | Direction | Rate | Payload |
|----|------|-----------|------|---------|
| 0x10 | `TELEM_FULL` | Drone→Nest | 10 Hz | lat(4), lon(4), alt_m(4), vx/vy/vz(12), heading(2), roll/pitch/yaw(6), battery_v(2), battery_pct(1), gps_sats(1), gps_hdop(2), airspeed(2), cpu_temp(1), rssi_mesh(1), rssi_900(1) — 42 bytes |
| 0x11 | `TELEM_COMPACT` | Drone→FL | 20 Hz | lat(4), lon(4), alt(2), heading(2), speed(2), battery(1), state(1) — 16 bytes |
| 0x12 | `TELEM_EMERGENCY` | Drone→Broadcast | 5 Hz | lat(4), lon(4), alt(2), failure_code(2), battery(1) — 13 bytes |
| 0x13 | `SENSOR_STATUS` | Drone→Nest | 1 Hz | imu_health(1), gps_health(1), camera_health(1), lidar_health(1), thermal_health(1), mesh_health(1), lte_health(1), rf900_health(1) — 8 bytes |
| 0x14 | `TELEM_AGGREGATED` | FL→Nest | 2 Hz | group_id(1), drone_count(1), drone_entries[](drone_id(2), lat(4), lon(4), alt(2), battery(1), state(1)) — 2 + 14×N bytes |

#### Category 0x2_: Commands & Mission

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0x20 | `GOTO_WAYPOINT` | Nest/FL→Drone | CRITICAL | lat(4), lon(4), alt(4), speed(2), heading(2), loiter_time_s(2) — 18 bytes |
| 0x21 | `GOTO_RELATIVE` | FL→Drone | CRITICAL | dx(4), dy(4), dz(4), speed(2) — 14 bytes |
| 0x22 | `SET_VELOCITY` | FL→Drone | REALTIME | vx(4), vy(4), vz(4), yaw_rate(4) — 16 bytes |
| 0x23 | `RTB` | Any→Drone | CRITICAL | urgency(1), nest_lat(4), nest_lon(4) — 9 bytes |
| 0x24 | `HOLD_POSITION` | Any→Drone | CRITICAL | duration_s(4) |
| 0x25 | `LAND` | Any→Drone | CRITICAL | lat(4), lon(4), immediate(1) — 9 bytes |
| 0x26 | `MISSION_UPLOAD` | Nest→Drone | RELIABLE | mission_id(4), waypoint_count(2), waypoints[](...) — variable |
| 0x27 | `MISSION_ACK` | Drone→Nest | RELIABLE | mission_id(4), status(1) |
| 0x28 | `GEOFENCE_UPDATE` | Nest→Broadcast | RELIABLE | fence_id(2), polygon_points[](...) — variable |
| 0x29 | `ABORT_MISSION` | Any→Drone | CRITICAL | reason_code(2) |
| 0x2A | `TASK_ASSIGN` | Nest→Drone | RELIABLE | task_type(1), task_id(4), params[](...) — variable |
| 0x2B | `TASK_STATUS` | Drone→Nest | RELIABLE | task_id(4), status(1), progress_pct(1), result_data[](...) |

#### Category 0x3_: Swarm Coordination

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0x30 | `FL_ELECTION_BID` | Drone→Group | RELIABLE | drone_id(2), fitness_score(4), group_id(1) — 7 bytes |
| 0x31 | `FL_ELECTED` | FL→Group | RELIABLE | leader_id(2), group_id(1), term_id(4) — 7 bytes |
| 0x32 | `FL_HEARTBEAT` | FL→Group | REALTIME | leader_id(2), group_members[](2×N), term_id(4) — variable |
| 0x33 | `GROUP_JOIN` | Drone→FL | RELIABLE | drone_id(2), capabilities(4) |
| 0x34 | `GROUP_LEAVE` | Drone→FL | RELIABLE | drone_id(2), reason(1) |
| 0x35 | `FORMATION_SET` | FL→Group | RELIABLE | formation_type(1), spacing_m(2), offsets[](dx(2), dy(2), dz(2) per drone) |
| 0x36 | `COLLISION_ALERT` | Drone→Nearby | REALTIME | drone_id(2), threat_bearing(2), threat_range_m(2), threat_velocity(2) — 8 bytes |
| 0x37 | `DECONFLICT` | FL→Drones | REALTIME | drone_a(2), drone_b(2), action_a(1), action_b(1), alt_separation_m(2) |
| 0x38 | `SWARM_STATE` | Nest→Broadcast | RELIABLE | swarm_mode(1), active_drones(1), formation(1), mission_phase(1) |

#### Category 0x4_: Detection & Payload

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0x40 | `DETECTION_EVENT` | Drone→Nest/FL | RELIABLE | detection_type(1), confidence(1), lat(4), lon(4), alt(2), bearing(2), classification(2), thumbnail_len(2), thumbnail[](...) |
| 0x41 | `TRACK_UPDATE` | Drone→Nest | RELIABLE | track_id(4), lat(4), lon(4), velocity(4), heading(2), class(2), confidence(1) — 21 bytes |
| 0x42 | `VIDEO_STREAM_CTRL` | Nest→Drone | RELIABLE | action(1: start/stop/params), stream_id(2), resolution(1), fps(1), bitrate(4) |
| 0x43 | `SENSOR_COMMAND` | Nest→Drone | RELIABLE | sensor_type(1), command(1), params[](...) |
| 0x44 | `THERMAL_ALERT` | Drone→Nest | CRITICAL | lat(4), lon(4), temp_max_c(2), area_m2(4), confidence(1) — 15 bytes |

#### Category 0x5_: Network Management

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0x50 | `LINK_REPORT` | Drone→Nest | RELIABLE | per-link metrics (see LinkMetrics struct) × num_transports |
| 0x51 | `ROUTE_UPDATE` | Any→Mesh | BEST_EFFORT | dest_id(2), next_hop(2), metric(2), hop_count(1) |
| 0x52 | `BANDWIDTH_REQUEST` | Drone→FL/Nest | RELIABLE | requested_bps(4), duration_s(2), priority(1) |
| 0x53 | `BANDWIDTH_GRANT` | FL/Nest→Drone | RELIABLE | granted_bps(4), slot_start(4), duration_s(2) |
| 0x54 | `CHANNEL_SWITCH` | Nest→Broadcast | CRITICAL | new_channel(1), switch_time_us(8) |
| 0x55 | `MESH_BRIDGE_ANNOUNCE` | Drone→Broadcast | RELIABLE | drone_id(2), has_lte(1), lte_quality(1) — for LTE relay election |

#### Category 0xF_: Emergency

| ID | Name | Direction | Reliability | Payload |
|----|------|-----------|-------------|---------|
| 0xF0 | `EMERGENCY_BEACON` | Drone→Broadcast | CRITICAL | drone_id(2), emergency_type(1), lat(4), lon(4), alt(2), battery_remaining_s(2) — 15 bytes |
| 0xF1 | `LOST_LINK_NOTIFY` | FL→Nest | CRITICAL | lost_drone_id(2), last_known_lat(4), last_known_lon(4), last_known_alt(2), last_contact_s(2) — 14 bytes |
| 0xF2 | `EMERGENCY_LAND_ALL` | Nest→Broadcast | CRITICAL | reason(1) |
| 0xF3 | `AIRSPACE_ALERT` | Nest→Broadcast | CRITICAL | alert_type(1), lat(4), lon(4), radius_m(4), altitude_floor(2), altitude_ceil(2) — 17 bytes |

### 3.3 Encryption Scheme

**Algorithm:** AES-256-GCM (Galois/Counter Mode)

**Key Hierarchy:**

```
Master Key (256-bit)
  ├── Swarm Session Key (derived via HKDF-SHA256, rotated every 1 hour)
  │     ├── Per-drone Traffic Key (derived with drone_id as context)
  │     └── Broadcast Key (shared, for multicast/broadcast)
  └── OTA Update Key (separate, offline provisioned)
```

**Key Distribution:**
1. Each drone has a unique Ed25519 keypair burned into secure element during manufacturing
2. Nest holds all drone public keys (provisioned via secure USB during fleet setup)
3. On boot, drone authenticates to Nest via challenge-response (msgs 0x03/0x04)
4. Nest derives session key, encrypts with drone's public key, sends via ECDH key exchange
5. Session key rotated every 3600 seconds via `KEY_ROTATE` message (piggybacked on heartbeat)

**Nonce Construction:**
```
nonce[0:3]  = source_id (2 bytes) + dest_id (2 bytes) — truncated to 4 bytes
nonce[4:7]  = sequence_number (4 bytes)
nonce[8:11] = session_key_epoch (4 bytes, seconds since key derivation)
```

This ensures nonce uniqueness per source, per key epoch. Nonce reuse is impossible as long as sequence numbers don't wrap within a key epoch (4 billion messages per drone per hour — safe).

**GCM Additional Authenticated Data (AAD):**
The unencrypted header (24 bytes) is used as AAD, ensuring header integrity without encrypting it (headers need to be readable for routing).

### 3.4 Authentication

**Boot Authentication Flow:**

```
Drone                                  Nest
  │                                      │
  │──── IDENTIFY (public key hash) ────→│
  │                                      │ Lookup drone in provisioned fleet DB
  │←─── AUTH_CHALLENGE (nonce) ─────────│
  │                                      │
  │ Sign nonce with Ed25519 private key  │
  │──── AUTH_RESPONSE (signature) ──────→│
  │                                      │ Verify signature with stored public key
  │←─── SESSION_KEY (encrypted) ────────│ ECDH-derived, encrypted to drone's pubkey
  │                                      │
  │  Authenticated. Join swarm mesh.     │
```

**Runtime Authentication:**
- Every message is authenticated via AES-256-GCM tag (16 bytes)
- Spoofed messages fail GCM verification and are silently dropped
- Replay protection: sequence numbers tracked per source; out-of-window messages rejected (window = 64 messages)
- IR side-channel provides physical proximity verification (Section 1.2)

### 3.5 Reliability Levels & ACKs

| Level | Behavior | Use Case |
|-------|----------|----------|
| BEST_EFFORT | Fire and forget, no ACK | Heartbeats, telemetry |
| RELIABLE | ACK required, 3 retransmits at 100/200/400 ms | Commands, mission data |
| REALTIME | No ACK, but timestamped; receiver drops if >50 ms stale | Velocity commands, collision alerts |
| CRITICAL | ACK required, unlimited retransmits across all available transports, 50 ms interval | Emergency, RTB, abort |

**ACK Message (implicit, not in catalog):**
```
Header with MSG_TYPE = 0xFF (ACK)
Payload: acked_sequence_number(4), status(1: OK/NACK/BUSY)
```

### 3.6 Addressing & Multicast

| Address | Meaning |
|---------|---------|
| 0x0000 | Nest |
| 0x0001–0x00FF | Individual drones (max 255) |
| 0xFE00–0xFEFF | Flight groups (group_id in low byte) |
| 0xFF00 | All flight leaders |
| 0xFFFF | Global broadcast |

**Multicast groups** are managed by the flight leader. When a drone joins a group (msg 0x33), it subscribes to the group's multicast address. The Doodle Labs mesh handles multicast natively at Layer 2.

### 3.7 Flight Leader Election Algorithm

**Fitness Function:**

```cpp
float compute_fitness(const DroneState& s) {
    float f = 0.0f;
    
    // Battery: 0–1.0, weighted heavily (dead leader = bad)
    f += 0.25f * std::min(s.battery_pct / 80.0f, 1.0f);
    
    // Mesh signal quality: average RSSI to group members, normalized
    f += 0.20f * normalize(s.avg_group_rssi, -90.0f, -30.0f);
    
    // Compute load: prefer drones with headroom
    f += 0.15f * (1.0f - s.cpu_load_pct / 100.0f);
    
    // Sensor health: fraction of sensors operational
    f += 0.15f * s.sensor_health_ratio;
    
    // Centrality: geometric median distance to group members (closer = better relay)
    f += 0.15f * normalize(1.0f / s.avg_distance_to_group_m, 0.0f, 0.01f);
    
    // Stability: time in current position without major maneuvers
    f += 0.05f * std::min(s.hover_stability_s / 60.0f, 1.0f);
    
    // Tiebreaker: lower drone_id wins (deterministic)
    f += 0.05f * (1.0f - s.drone_id / 255.0f);
    
    return f;
}
```

**Election Protocol (Raft-inspired, simplified):**

1. **Trigger:** Election starts when:
   - No FL heartbeat received for 3 seconds (FL failure)
   - Nest commands group split/merge
   - Current FL's fitness drops below 0.3

2. **Bidding Phase (500 ms):**
   - All group members compute fitness and broadcast `FL_ELECTION_BID`
   - Bids include term_id (incremented from previous term)

3. **Resolution (immediate after 500 ms):**
   - Each drone independently determines winner = highest fitness score in received bids
   - Deterministic: same inputs → same winner (no voting needed)
   - Winner broadcasts `FL_ELECTED` with new term_id

4. **Confirmation (200 ms):**
   - Group members who agree send `GROUP_JOIN` to new FL
   - If <50% of group confirms within 200 ms, re-election triggered

5. **Steady State:**
   - FL sends `FL_HEARTBEAT` every 500 ms
   - Members re-evaluate fitness every 30 seconds; if any member's fitness exceeds FL by >0.15 for >60 seconds, graceful leadership transfer

**Consistency guarantee:** Since fitness is computed deterministically from observable state, and all members see the same bids, all honest nodes converge on the same leader without explicit voting rounds.

---

## 4. Network Architecture

### 4.1 Mesh Topology

The Doodle Labs Mesh Rider operates as a Layer 2 MANET (Mobile Ad-hoc Network) with these characteristics:

```
                    ☁ Cloud
                    │ (LTE)
                    │
              ┌─────┴─────┐
              │   NEST     │ ← 2× Doodle Labs (sector antennas)
              │ (Gateway)  │ ← 2× RFD900x
              └─────┬──────┘ ← 1× LTE
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───┴───┐  ┌────┴───┐  ┌───┴───┐
    │ FL-A  │  │ FL-B   │  │ FL-C  │    ← Flight Leaders
    │Group 1│  │Group 2 │  │Group 3│
    └───┬───┘  └───┬────┘  └───┬───┘
     ┌──┼──┐    ┌──┼──┐    ┌──┼──┐
     │  │  │    │  │  │    │  │  │
     D  D  D    D  D  D    D  D  D      ← Individual Drones
     1  2  3    4  5  6    7  8  9
                │
               (multi-hop relay if D5 is out of Nest range)
```

**Doodle Labs Configuration:**
- Mode: Mesh (self-forming/self-healing)
- Channel BW: 10 MHz (balance of throughput and range; 40 Mbps usable)
- Channel: Auto-selected at boot via spectrum scan, avoiding WiFi interference
- ATPC: Enabled (saves power, reduces interference)
- Encryption: AES-128 at radio layer (our protocol adds AES-256-GCM on top)
- IP scheme: 10.42.0.0/16 (10.42.0.1 = Nest, 10.42.1.x = drones)

### 4.2 Multi-Hop Routing

The Doodle Labs mesh handles routing internally using a proprietary optimized OLSR variant. Key parameters:

- **Max hops:** 8 (configurable; with 10 km per hop, supports 80 km operational radius)
- **Route convergence:** <2 seconds for topology changes
- **Throughput per hop:** Degrades ~40% per hop (40 Mbps → 24 → 14 → 8 Mbps)

**Application-level routing awareness:**
The `hb_comms` module queries Doodle Labs management API for route metrics and exposes them:

```
Topic: /hb/comms/mesh/routes
Message: hummingbird_msgs/msg/MeshRouteTable
  RouteEntry[] routes
    uint16 dest_id
    uint16 next_hop
    uint8 hop_count
    float32 metric
    uint32 throughput_bps
```

### 4.3 LTE Mesh Bridge

When one or more drones have cellular connectivity, they can bridge mesh traffic to the cloud/Nest:

**Bridge Election:**
1. Drones with LTE signal broadcast `MESH_BRIDGE_ANNOUNCE` (msg 0x55) every 10 seconds
2. Nest selects the drone with best LTE quality as primary bridge
3. Other LTE-equipped drones remain standby bridges

**Bridge Data Flow:**
```
Drone (no LTE) → Mesh → Bridge Drone (has LTE) → LTE → Cloud → Nest
```

**What routes through LTE bridge:**
- Video streams (high bandwidth, latency tolerant)
- Mission data uploads
- Non-real-time telemetry aggregation

**What does NOT route through LTE bridge:**
- Real-time C2 commands (latency too variable)
- Emergency messages (use direct mesh or 900 MHz)

### 4.4 900 MHz Emergency Backbone

The RFD900x radios form a separate, independent communication layer:

**Configuration:**
- Air data rate: 64 kbps (default, best range/reliability)
- Networking mode: Multipoint SiK firmware
- Nest as base station, drones as remotes
- FHSS across 902–928 MHz (50 channels)

**Data Budget on 900 MHz (64 kbps shared):**

| Traffic | Per Drone | Protocol | Budget |
|---------|-----------|----------|--------|
| Compressed heartbeat | 13 bytes × 1 Hz | HiveLink | 104 bps |
| Emergency telemetry | 42 bytes × 0.5 Hz | HiveLink | 168 bps |
| Commands (inbound) | 18 bytes × 0.2 Hz | HiveLink | 29 bps |
| **Per-drone total** | | | **~301 bps** |
| **30 drones total** | | | **~9 kbps** |

This leaves 55 kbps headroom (86%) for retransmissions and burst traffic. The 900 MHz link is intentionally ultra-lean.

**Time-Division Scheme:**
With multipoint SiK, the base station polls each drone in round-robin. With 30 drones at 64 kbps, each drone gets a ~33 ms slot every 1 second — sufficient for heartbeat exchange.

### 4.5 Aggregate Bandwidth Budget

**Uplink (Drone → Nest), 30 drones, 2.4 GHz mesh at 10 MHz BW:**

| Traffic | Per Drone | × 30 | Notes |
|---------|-----------|------|-------|
| Full telemetry (10 Hz) | 42B × 10 × 8 = 3.4 kbps | 101 kbps | Always-on |
| Compact telemetry to FL (20 Hz) | 16B × 20 × 8 = 2.6 kbps | 77 kbps | Intra-group only |
| Sensor status (1 Hz) | 64 bps | 1.9 kbps | |
| Heartbeat (1 Hz) | 104 bps | 3.1 kbps | |
| Detection events (burst) | ~500 bytes avg | 120 kbps | Assume 1/s across swarm |
| Video (3 active streams) | 2 Mbps each | 6 Mbps | Only 3 drones stream simultaneously |
| Protocol overhead (headers, encryption, ACKs) | ~20% | ~1.3 Mbps | |
| **Total uplink** | | **~7.8 Mbps** | |

**Downlink (Nest → Drones):**

| Traffic | Total | Notes |
|---------|-------|-------|
| Commands | ~50 kbps | Burst |
| Mission updates | ~200 kbps | Burst |
| Geofence updates | ~10 kbps | Rare |
| Time sync | ~5 kbps | Broadcast |
| Video stream control | ~2 kbps | |
| **Total downlink** | **~270 kbps** | |

**Capacity margin on 10 MHz channel (40 Mbps usable):**
- Total traffic: ~8.1 Mbps
- **Utilization: ~20%** — substantial headroom for multi-hop relay overhead, retransmissions, and burst video from additional drones

### 4.6 Nest as Central Router/Aggregator

The Nest runs a dedicated networking stack:

```
ROS2 Node: /hb/nest/comms_gateway
  - Bridges all three radio networks
  - Aggregates telemetry from all drones
  - Routes commands to appropriate transport
  - Manages video stream assignments
  - Runs flight leader election oversight

ROS2 Node: /hb/nest/mesh_manager
  - Monitors Doodle Labs mesh health
  - Triggers channel switches if interference detected
  - Manages mesh bridge assignments

ROS2 Node: /hb/nest/cloud_bridge
  - Serializes swarm state for cloud upload
  - Handles cloud commands → HiveLink translation
  - Manages OTA update distribution
```

**Internal Nest Network:**
```
┌────────────────────────────────────────────┐
│              Jetson AGX Orin               │
│                                            │
│  eth0 ─── Managed Switch ─── DoodleLabs×2 │
│  eth1 ─── Managed Switch ─── LTE Router   │
│  ttyUSB0 ── RFD900x #1                    │
│  ttyUSB1 ── RFD900x #2                    │
│  eth2 ─── (optional) Wired LAN            │
│                                            │
│  VLAN 10: Mesh traffic                     │
│  VLAN 20: Cloud/LTE                        │
│  VLAN 30: Management                       │
└────────────────────────────────────────────┘
```

---

## 5. Resilience & Degradation

### 5.1 Degradation Levels

| Level | Condition | Active Links | Behavior |
|-------|-----------|-------------|----------|
| **GREEN** | All systems nominal | Mesh + LTE + 900 | Full operations, video streaming |
| **YELLOW** | One link degraded | 2 of 3 links | Reduce video bitrate, increase heartbeat rate |
| **ORANGE** | Only one link active | Mesh OR LTE OR 900 | Essential C2 only, no video, FL aggregation |
| **RED** | All radio links lost | None | Fully autonomous, execute last known mission or RTB |
| **BLACK** | GPS also lost | None + no GPS | Inertial-only, immediate controlled landing |

### 5.2 Comms Priority During Degradation

When bandwidth contracts, traffic is shed in this order (last shed = highest priority):

1. ~~Video streams~~ (first to drop)
2. ~~Sensor data uploads~~
3. ~~Full telemetry~~ (switch to compact)
4. ~~Detection thumbnails~~ (send metadata only)
5. ~~Non-critical commands~~
6. Heartbeats (compress further)
7. Emergency beacons (NEVER shed)
8. Flight controller C2 (NEVER shed)

### 5.3 Autonomous Operation Without Radio

When a drone enters **RED** (all comms lost):

```
T+0s:   All links scored < 0.1
T+3s:   Officially enter COMMS_LOST state
        - LED: fast red pulse
        - Continue current waypoint mission
        - Store all telemetry/detections locally (SD card)
        - Broadcast EMERGENCY_BEACON on all radios every 5s (hoping for recovery)
        
T+30s:  If still no contact:
        - Attempt LTE on all available bands
        - RFD900x: switch to lowest data rate (4kbps) for max range
        - Climb 50m for better radio horizon (if altitude permits)
        
T+120s: If still no contact and mission not complete:
        - Abort mission, begin RTB to last known Nest position
        - Navigate via onboard GPS + stored map
        
T+300s: If RTB not progressing (obstacles, wind, battery):
        - Select safe landing zone from onboard terrain data
        - Execute autonomous landing
        - Continue broadcasting beacon at 1 Hz until battery critical
        
Battery < 15%:
        - Immediate landing at current position
        - Activate IR beacon for ground recovery
```

### 5.4 Swarm Fragmentation Handling

When the mesh network partitions:

**Detection:** A flight leader detects fragmentation when:
- Drones in its group become unreachable (no heartbeat for 5s)
- Nest becomes unreachable

**Response:**

```
Fragment A (has Nest contact):
  - Nest-connected FL continues operations
  - Marks lost drones as COMMS_LOST
  - Broadcasts on 900 MHz for fragment B drones

Fragment B (no Nest contact):
  - Highest-fitness drone in fragment becomes Acting FL
  - Acting FL takes over group coordination
  - Fragment operates autonomously on last mission parameters
  - Continuously attempts reconnection (mesh scan + 900 MHz)
  - If LTE available, establishes cloud-mediated Nest connection
  
Reconnection:
  - When fragments detect each other (mesh or 900 MHz):
    1. Acting FL sends IDENTIFY to Nest-connected FL
    2. Nest-connected FL relays to Nest
    3. Nest sends updated mission parameters
    4. Swarm re-merges, groups re-formed
    5. New FL election triggered for merged group
```

### 5.5 Reconnection/Rejoin Protocol

When a previously lost drone regains contact:

```
Lost Drone                              Nest/FL
    │                                      │
    │── IDENTIFY + AUTH_CHALLENGE ─────────→│
    │                                      │ Verify identity
    │←── AUTH_RESPONSE + NEW_SESSION_KEY ──│
    │                                      │
    │── TELEM_FULL (current state) ───────→│
    │── STORED_DATA_MANIFEST ─────────────→│ "I have 5 min of unsent data"
    │                                      │
    │←── MISSION_UPDATE (current mission) ─│
    │←── GROUP_ASSIGN (rejoin group) ──────│
    │                                      │
    │── STORED_DATA_UPLOAD ───────────────→│ Background upload of cached data
    │                                      │
    │   Normal operations resume           │
```

### 5.6 Emergency Broadcast Patterns

| Scenario | Radio | Pattern | Content |
|----------|-------|---------|---------|
| Drone critical failure | All (simultaneous) | 5 Hz burst, 3 seconds | EMERGENCY_BEACON |
| Swarm-wide abort | Nest → all | Broadcast, 10× repeated, 100ms interval | EMERGENCY_LAND_ALL |
| Airspace intrusion | Nest → all | Broadcast, 5× repeated | AIRSPACE_ALERT |
| Lost drone | FL → 900 MHz | 1 Hz continuous | LOST_LINK_NOTIFY |
| Battery critical | Drone → all | 2 Hz, continuous until landed | TELEM_EMERGENCY |

---

## 6. Cloud & Integration Layer

### 6.1 Nest ↔ Cloud Architecture

```
┌────────┐         ┌──────────────┐         ┌──────────────────┐
│  NEST  │◄──LTE──►│   CLOUD GW   │◄──────►│  HUMMINGBIRD     │
│        │         │  (Regional)  │         │  CLOUD PLATFORM  │
│        │◄─Fiber─►│              │         │                  │
│        │(if avl) │  - MQTT      │         │  - Fleet Mgmt    │
└────────┘         │  - WebSocket │         │  - Mission Plan  │
                   │  - gRPC      │         │  - Analytics     │
                   └──────────────┘         │  - Video Storage │
                                            │  - ML Training   │
                                            └──────────────────┘
```

**Protocol Stack:**
- **Telemetry uplink:** MQTT 5.0 over TLS 1.3 (lightweight, pub-sub, QoS levels)
  - Topic structure: `hb/{swarm_id}/drone/{drone_id}/telemetry`
  - Aggregate topic: `hb/{swarm_id}/state` (2 Hz full swarm snapshot)
- **Commands downlink:** gRPC bidirectional stream (low latency, typed)
- **Video:** RTSP → WebRTC gateway for browser-based viewing
- **Bulk data:** HTTPS PUT to object storage (S3-compatible)

**MQTT Topics:**

```
hb/{swarm_id}/drone/{id}/telemetry     # Per-drone telemetry
hb/{swarm_id}/drone/{id}/status        # Health/state
hb/{swarm_id}/drone/{id}/detection     # Detection events
hb/{swarm_id}/state                    # Aggregated swarm state
hb/{swarm_id}/commands                 # Inbound commands
hb/{swarm_id}/alerts                   # Emergency alerts
hb/{swarm_id}/ota/status               # OTA update progress
```

**Bandwidth to Cloud:**
- Telemetry: ~50 kbps (30 drones, compressed JSON/Protobuf)
- Video (3 streams): 6 Mbps
- Detections: ~100 kbps burst
- Total sustained: ~7 Mbps uplink — well within LTE/5G capability

### 6.2 CAD/911 Dispatch Integration

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│ 911 PSAP /   │    │  HUMMINGBIRD    │    │    NEST      │
│ CAD System   │◄──►│  CLOUD API      │◄──►│ (Edge)       │
│              │    │                 │    │              │
│ - Incident   │    │ - REST API      │    │ - Auto-      │
│   create     │    │ - Webhooks      │    │   dispatch   │
│ - Unit       │    │ - NENA i3       │    │ - Live feed  │
│   dispatch   │    │   compatible    │    │   to CAD     │
│ - Status     │    │                 │    │              │
│   updates    │    │                 │    │              │
└──────────────┘    └─────────────────┘    └──────────────┘
```

**Integration Data Flows:**

1. **Incident → Drone Dispatch:**
   - CAD creates incident with location, type, priority
   - Cloud API receives via webhook or NENA i3 standard
   - Mission planner generates optimal drone assignment
   - Mission pushed to Nest → dispatched drones

2. **Drone → CAD Status:**
   - Drone en route / on scene / RTB status
   - ETA updates (GPS-based, wind-corrected)
   - Live video feed URL injected into CAD incident record

3. **Detection → CAD Alert:**
   - Thermal signature detected (fire)
   - Person detected (search and rescue)
   - Alert pushed to CAD with GPS coords, confidence, thumbnail

**Standards Compliance:**
- NENA i3 for 911 integration
- CAP (Common Alerting Protocol) for alerts
- NIMS/ICS compatible status reporting

### 6.3 Remote Operator Access

```
Operator Browser
    │
    ├── WebRTC ──── Live video (sub-second latency)
    ├── WebSocket ── Real-time telemetry + map overlay
    ├── gRPC-Web ─── Command & control (authenticated)
    └── HTTPS ────── Mission planning UI, historical data
```

**Authentication:**
- OAuth 2.0 + RBAC (role-based access control)
- Roles: Observer (view only), Operator (commands), Admin (config/OTA)
- MFA required for Operator and Admin
- All sessions TLS 1.3 encrypted

**Latency (remote operator):**
- Video: ~200–500 ms (WebRTC via cloud relay)
- Telemetry: ~100–300 ms
- Commands: ~100–300 ms (too slow for direct piloting — supervisory only)

### 6.4 Data Logging & Replay

**On-Drone Logging:**
- All HiveLink messages logged to onboard SD card (ROS2 bag format via `rosbag2`)
- Circular buffer: last 2 hours at full fidelity
- Compressed: ZSTD compression, ~10:1 ratio
- Storage: 256 GB microSD → ~500 hours of flight data

**Nest Logging:**
- Full swarm message archive (all HiveLink traffic)
- Video recording (H.265, all active streams)
- Storage: 2 TB NVMe → ~100 hours of full swarm recording

**Cloud Archival:**
- Telemetry: 90-day hot storage, then cold (S3 Glacier)
- Video: 30-day hot, then cold
- Detections/alerts: permanent hot storage
- Mission logs: permanent

**Replay System:**
```
ROS2 Node: /hb/replay/player
  - Replays rosbag2 files with time-accurate playback
  - Can feed into visualization (Foxglove) or analysis pipelines
  - Supports variable speed (0.1×–10×)
  - Enables post-incident review and ML training data extraction
```

### 6.5 Over-the-Air Updates

**OTA Architecture:**

```
Developer → CI/CD → Cloud OTA Server → Nest → Drones
```

**Update Targets:**
| Component | Update Mechanism | Size | Downtime |
|-----------|-----------------|------|----------|
| Jetson firmware/OS | A/B partition swap | ~2 GB | Reboot (30s) |
| ROS2 application | Container image (podman) | ~500 MB | Service restart (5s) |
| PX4 firmware | MAVLink FTP via UART | ~2 MB | FC reboot (10s) |
| FPGA bitstream | Jetson → USB → FPGA flash | ~5 MB | FPGA reconfig (2s) |
| Doodle Labs firmware | Doodle Labs management API | ~20 MB | Radio reboot (15s) |
| Swarm protocol params | HiveLink CONFIG message | ~1 KB | Immediate |

**Update Process:**
1. Cloud pushes update manifest to Nest (SHA-256 hashes, signatures)
2. Nest downloads update payload, verifies signature (Ed25519)
3. Nest pre-distributes to all drones during docking (GbE, ~2 Gbps)
4. Operator triggers rolling update: drones update one-by-one, maintaining 80% swarm availability
5. Each drone: download → verify → apply to inactive partition → test boot → confirm → switch
6. Rollback: if test boot fails, revert to previous partition automatically

---

## 7. Future-Proofing

### 7.1 Plugin Architecture for New Radios

The `ITransport` interface (Section 2.1) is the plugin boundary. Adding a new radio requires:

```
hb_comms/
├── include/hb_comms/transport/
│   ├── itransport.hpp          # Interface (stable)
│   ├── mesh_2g4_transport.hpp  # Doodle Labs implementation
│   ├── lte_transport.hpp       # Sierra Wireless implementation
│   ├── rf900_transport.hpp     # RFD900x implementation
│   ├── ir_transport.hpp        # IR implementation
│   └── <new_radio>_transport.hpp  # New radio: implement ITransport
├── src/
│   ├── transport_manager.cpp   # Manages all transports, failover logic
│   └── <new_radio>_transport.cpp
├── config/
│   └── transport_config.yaml   # Runtime config: priorities, weights, enable/disable
└── plugins/                    # Dynamically loaded .so files
    └── lib<new_radio>_transport.so
```

**Plugin Loading:**
Transports are loaded as shared libraries at startup. `transport_config.yaml` specifies which plugins to load and their priority ordering. No recompilation needed to add/remove radios.

### 7.2 Self-Expanding Mesh

**Concept:** Drones autonomously position themselves to extend mesh coverage.

**Relay Drone Role:**
When a mission requires drones beyond mesh range of Nest:
1. Nest identifies coverage gap
2. Assigns one drone as "relay" — positions at midpoint
3. Relay drone orbits at altitude for best RF propagation
4. Multiple relay drones can chain for extreme range (tested concept with Doodle Labs >100 km)

```
ROS2 Node: /hb/mesh/topology_optimizer
  - Monitors mesh connectivity graph
  - Identifies single-point-of-failure nodes
  - Recommends relay drone placement
  - Can autonomously reposition drones for coverage (with Nest approval)
```

### 7.3 AI-Driven Radio Resource Management

**Phase 1 (Current):** Rule-based transport selection (Section 2.3)

**Phase 2 (Future):** Reinforcement learning agent for radio resource management:

```
State:  [per-link metrics × N_transports × N_drones,
         traffic queue depths,
         mission priority levels,
         interference spectrum scan]

Action: [transport selection per flow,
         channel bandwidth adjustment,
         TX power adjustment,
         video bitrate targets]

Reward: minimize(latency_critical_msgs) + 
        maximize(video_throughput) +
        minimize(packet_loss) +
        minimize(power_consumption)
```

**Training:** Offline using logged swarm data, then online fine-tuning with conservative exploration bounds.

**Deployment:** ONNX model on Jetson Orin NX (TensorRT acceleration), inference <1 ms.

### 7.4 Spectrum-Aware Operation

**Current:** Doodle Labs built-in spectrum scanner selects cleanest channel at boot.

**Future Enhancement:**

```
ROS2 Node: /hb/spectrum/monitor
  - Continuous background spectrum scan (Doodle Labs API)
  - Detect interference patterns (WiFi, other drones, jamming)
  - Trigger dynamic channel switch (msg 0x54) when current channel degraded
  - Report spectrum occupancy to cloud for fleet-wide planning
  
ROS2 Node: /hb/spectrum/jammer_detector  
  - ML classifier for intentional jamming vs incidental interference
  - If jamming detected: alert operator, switch bands, activate 900 MHz backbone
  - Log jamming events with direction-finding (RSSI gradient across swarm)
```

**Multi-Band Upgrade Path:**
The Doodle Labs product line includes dual-band radios (900 MHz + 2.4 GHz in one module, model RM-1700-22M3). Future hardware revision could replace the separate Doodle Labs + RFD900x with a single dual-band Doodle Labs radio, gaining:
- Simultaneous 900 MHz mesh (not just point-to-point like RFD900x)
- Software-controlled band switching
- Reduced weight and cost

**Source:** [Doodle Labs Dual-Band](https://techlibrary.doodlelabs.com/mini-oem-dual-band-mesh-rider-radio-915-mhz-and-2450-mhz-ism-bands)

---

## Appendix A: ROS2 Node & Topic Summary

### Nodes

| Node | Location | Purpose |
|------|----------|---------|
| `/hb/comms/transport_manager` | Drone | Manages all radio transports, failover |
| `/hb/comms/hivelink` | Drone | HiveLink protocol encode/decode |
| `/hb/comms/crypto` | Drone | AES-256-GCM encryption/decryption |
| `/hb/comms/mesh_monitor` | Drone | Doodle Labs mesh status monitoring |
| `/hb/swarm/flight_leader` | Drone | FL election, group management |
| `/hb/swarm/telemetry_aggregator` | Drone (FL) | Aggregates group telemetry |
| `/hb/video/streamer` | Drone | Adaptive video encoding/streaming |
| `/hb/led/controller` | Drone | LED pattern management |
| `/hb/ir/landing` | Drone | IR-based precision landing |
| `/hb/nest/comms_gateway` | Nest | Multi-radio gateway |
| `/hb/nest/mesh_manager` | Nest | Mesh topology management |
| `/hb/nest/cloud_bridge` | Nest | Cloud connectivity |
| `/hb/nest/mission_planner` | Nest | Mission planning & dispatch |
| `/hb/replay/player` | Nest | Data replay |

### Key Topics

| Topic | Message Type | Rate | Transport |
|-------|-------------|------|-----------|
| `/hb/telemetry/full` | `TelemetryFull` | 10 Hz | Mesh |
| `/hb/telemetry/compact` | `TelemetryCompact` | 20 Hz | Mesh (local) |
| `/hb/comms/link_quality` | `LinkQuality` | 2 Hz | Internal |
| `/hb/comms/mesh/routes` | `MeshRouteTable` | 1 Hz | Internal |
| `/hb/swarm/fl_election` | `FLElectionBid` | Event | Mesh |
| `/hb/swarm/group_state` | `GroupState` | 2 Hz | Mesh |
| `/hb/detection/event` | `DetectionEvent` | Event | Mesh |
| `/hb/video/compressed` | `CompressedImage` | 30 Hz | Mesh/LTE |
| `/hb/led/command` | `LEDCommand` | Event | Internal |
| `/hb/commands/waypoint` | `GotoWaypoint` | Event | Mesh |
| `/hb/emergency/beacon` | `EmergencyBeacon` | 5 Hz | All |

### Code Module Layout

```
hummingbird_ws/src/
├── hb_msgs/                    # Custom message definitions
│   ├── msg/
│   │   ├── TelemetryFull.msg
│   │   ├── TelemetryCompact.msg
│   │   ├── LinkQuality.msg
│   │   ├── LEDCommand.msg
│   │   ├── DetectionEvent.msg
│   │   ├── FLElectionBid.msg
│   │   └── ...
│   └── CMakeLists.txt
├── hb_comms/                   # Communications stack
│   ├── include/hb_comms/
│   │   ├── transport/          # ITransport + implementations
│   │   ├── hivelink/           # Protocol codec
│   │   └── crypto/             # AES-256-GCM, key management
│   ├── src/
│   └── plugins/                # Dynamically loaded transports
├── hb_swarm/                   # Swarm coordination
│   ├── flight_leader/
│   ├── formation/
│   └── collision_avoidance/
├── hb_video/                   # Video pipeline
├── hb_perception/              # Detection, tracking
├── hb_navigation/              # Mission execution, path planning
├── hb_drivers/                 # Hardware drivers (LED, IR, sensors)
├── hb_nest/                    # Nest-specific nodes
└── hb_cloud/                   # Cloud integration (MQTT, gRPC)
```

---

## Appendix B: Bandwidth Calculation Worksheet

### Scenario: 30 Drones, 3 Active Video, 10 MHz Mesh Channel

```
Mesh capacity (10 MHz, 2×2 MIMO):         40 Mbps aggregate
Multi-hop overhead (avg 1.5 hops):         ×0.7 → 28 Mbps effective

Traffic breakdown:
  Telemetry (30 × 3.4 kbps):              102 kbps
  Compact telem (30 × 2.6 kbps):           78 kbps
  Heartbeats (30 × 104 bps):                3.1 kbps
  Sensor status (30 × 64 bps):              1.9 kbps
  Detections (burst avg):                  120 kbps
  Video (3 × 2 Mbps):                       6 Mbps
  FL aggregation (5 × 100 kbps):           500 kbps
  Commands (burst avg):                     50 kbps
  Protocol overhead (headers+crypto+ACKs): ~20% → 1.4 Mbps
                                          ─────────
  TOTAL:                                   ~8.3 Mbps
  
  Utilization: 8.3 / 28 = 29.6%
  Headroom: 19.7 Mbps (for burst video, retransmits, growth)
```

### Worst Case: 10 Simultaneous Video Streams

```
  Video (10 × 2 Mbps):                    20 Mbps
  Everything else:                          2.3 Mbps
  Overhead:                                 4.5 Mbps
  TOTAL:                                   26.8 Mbps → 95.7% utilization ⚠️
  
  → Auto-degrade: reduce to 720p (1 Mbps each) → 14.8 Mbps → 52.9% ✓
```

---

## Appendix C: Hardware Bill of Materials (Comms Only, Per Drone)

| Component | Model | Cost | Weight | Power |
|-----------|-------|------|--------|-------|
| Mesh radio | Doodle Labs RM-2450-12M3 | $1,450 | 36.5 g | 8W max |
| Backup radio | RFD900x | $118 | 14.5 g | 4W max |
| Cellular | Sierra Wireless EM9291 | $250 | 12 g | 5W max |
| 2.4 GHz antennas (×2) | PCB patch, 3 dBi | $20 | 5 g | — |
| 900 MHz antennas (×2) | Whip + wire, 2 dBi | $10 | 8 g | — |
| Cellular antennas (×2) | Flex PCB MIMO | $15 | 4 g | — |
| IR transceivers | TSOP38238 + TFBS4711 | $8 | 2 g | 0.1W |
| LED array | 4× RGB + 8× WS2812B | $5 | 6 g | 2W max |
| **Total comms** | | **$1,848** | **81.5 g** | **17.1W max** |

---

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-03-04 | Initial document |
| 2026-03-11 | **Source error corrections:** Doodle Labs weight ~30g → 36.5g per [Doodle Labs Tech Library](https://techlibrary.doodlelabs.com/doodle-labs-mini-oem-mesh-rider-radio-24002482-mhz). EM9291 speeds corrected: DL 4.9 Gbps → 3.5 Gbps, UL 660 Mbps → 900 Mbps per [Sierra Wireless](https://www.sierrawireless.com/iot-modules/5g-modules/em9291/). RFD900x price ~$90 → $118 per [SpektreWorks](https://spektreworks.com/product/rfd-900x-modem/). Cost summary table updated (Doodle Labs weight 30g→36.5g, power 6W→8W; RFD900x $90→$118). |

*End of Document*
