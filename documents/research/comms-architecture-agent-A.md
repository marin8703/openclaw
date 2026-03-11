# Hummingbird Swarm Communications Architecture

**Version:** 1.0  
**Date:** 2026-03-04  
**Author:** Agent A  
**Status:** Architecture Design Document

---

## Table of Contents

1. [Hardware Layer](#1-hardware-layer)
2. [Software Layer](#2-software-layer)
3. [Protocol Layer](#3-protocol-layer)
4. [Network Topology](#4-network-topology)
5. [Degraded Operations](#5-degraded-operations)
6. [Cloud/Ground Layer](#6-cloudground-layer)
7. [Extensibility](#7-extensibility)

---

## 1. Hardware Layer

### 1.1 Primary Mesh — Doodle Labs Mesh Rider 2.4 GHz (mini-OEM)

| Parameter | Value |
|---|---|
| Model | RM-2450-2LSX-SA-ST (mini-OEM) |
| Frequency | 2400–2482 MHz (ISM/Wi-Fi band) |
| Modulation | COFDM, adaptive BPSK → 64QAM per-packet |
| MIMO | 2×2 MIMO |
| Throughput | 80 Mbps (20 MHz ch), 40 Mbps (10 MHz), 20 Mbps (5 MHz) |
| Encryption | FIPS 140-3 AES-128 (full throughput) / AES-256 (12 Mbps max) |
| Latency | 1.5–10 ms (URLLC mode) |
| Range | 10+ km line-of-sight (field tested >100 km with high-gain antennas) |
| Dimensions | Baseband: 47 × 28 × 5 mm; RF Board: 46 × 51 × 6.5 mm |
| Weight | 36.5 g |
| Interfaces | Ethernet (100 Base-T), USB-Dev, UART |
| Power | 5V ±5% input, 5W avg (50% Tx/Rx), 8W peak, 2W Rx |
| Operating Temp | −40°C to +85°C |
| Modes | Mesh, WDS AP, WDS Client, NAT gateway |
| Antenna | 2× MMCX-Female, ANT-2450-3-O (3 dBi omni recommended) |

**Source:** [Doodle Labs Tech Library](https://techlibrary.doodlelabs.com/doodle-labs-mini-oem-mesh-rider-radio-24002482-mhz)

**Connection to Jetson:** Ethernet (100 Base-T) via carrier board RJ45 or direct board-to-board header. The Mesh Rider runs OpenWrt internally and presents a standard IP network interface to the Jetson.

**Role:** Primary swarm mesh carrying all message types — telemetry, commands, video relay, discovery, election traffic. This is the workhorse link.

---

### 1.2 Backup Long-Range — RFD900x-US (900 MHz)

| Parameter | Value |
|---|---|
| Frequency | 902–928 MHz (US ISM) |
| Modulation | FHSS (frequency hopping spread spectrum) |
| Air Data Rate | 4–500 kbps (user selectable, default 64 kbps) |
| UART Rate | 9600–921600 baud (default 57600) |
| TX Power | 1W (+30 dBm), 1 dB steps |
| RX Sensitivity | −121 dBm at low data rates |
| Range | >40 km demonstrated, 80 km max (balloon test) |
| Antenna | 2× RP-SMA (diversity switching) |
| Size | 30 × 57 × 12.8 mm |
| Weight | 14.5 g |
| Power | 3.5–5.5 VDC, ~800 mA peak at max TX |
| Interface | TTL UART (3.3V logic) |
| Firmware | SiK (open source), MAVLink framing support |
| Operating Temp | −40°C to +85°C (tested −73°C to +123°C) |

**Source:** [RFD900x Datasheet](https://files.rfdesign.com.au/Files/documents/RFD900x%20DataSheet%20V1.2.pdf), [SpektreWorks](https://spektreworks.com/product/rfd-900x-modem/)

**Connection to Jetson:** UART via Jetson carrier board GPIO header or USB-UART bridge. We use `/dev/ttyTHS2` (dedicated UART) or USB-serial adapter.

**Role:** Backup low-bandwidth link for critical C2 messages, heartbeats, and safety alerts when mesh is degraded or jammed. Also used for Nest↔swarm C2 at extreme range. NOT used for video or bulk data.

---

### 1.3 Cellular Backhaul — Sierra Wireless EM9291 (LTE/5G)

| Parameter | Value |
|---|---|
| Technology | 5G NR Sub-6 GHz, LTE Cat 20, 3G fallback |
| DL Speed | Up to 3.5 Gbps (5G) |
| UL Speed | Up to 900 Mbps (5G) |
| 5G Bands | n1, n2, n3, n5, n7, n8, n12–n14, n18, n20, n25, n26, n28, n29, n30, n38, n40, n41, n48, n66, n70, n71, n77, n78 |
| Form Factor | M.2 (Key B), 3042 |
| Host Interface | USB 3.1, PCIe Gen 3 ×1 |
| GNSS | Integrated (GPS, GLONASS, BeiDou, Galileo) |
| SIM | Nano SIM |
| Power | 3.3V typical, varies by mode |
| Operating Temp | −40°C to +85°C (industrial grade) |

**Source:** [Sierra Wireless EM9291](https://www.sierrawireless.com/iot-modules/5g-modules/em9291/)

**Connection to Jetson:** M.2 slot on Jetson carrier board (PCIe preferred for throughput, USB 3.1 fallback). Presents as standard `wwan0` network interface via ModemManager/NetworkManager.

**Role:** Cloud/ground station backhaul. NOT used for swarm-to-swarm. Primary use: video streaming to ground, cloud relay, OTA firmware updates. One drone per subgroup acts as **LTE Gateway**, bridging mesh traffic to cellular. GNSS receiver provides secondary position source.

---

### 1.4 IR Communication System

| Component | Details |
|---|---|
| Emitters | 850nm IR LEDs (4× per drone, cardinal directions + 1× downward) |
| Receivers | Photodiode array with bandpass filter (matched to 850nm) |
| Data Rate | ~1 kbps (modulated on/off keying) |
| Range | 0.5–30 m effective |
| Interface | CrossLink-NX FPGA GPIO (modulation/demodulation in FPGA) |
| Purpose | Precision landing alignment, close-range drone-to-drone ID, Nest docking guidance |

**Protocol:** Simple OOK (on-off keying) modulated at 38 kHz carrier (standard IR remote protocol base). Each drone transmits its 8-bit swarm ID in a 32-bit frame (8-bit preamble, 8-bit ID, 8-bit command, 8-bit CRC). The FPGA handles all IR timing — zero Jetson CPU load.

**Nest Landing Use:** The Nest landing pad has a grid of upward-facing IR emitters broadcasting pad-slot assignments. Drones use downward IR receiver to lock onto assigned slot during final approach (<5m).

---

### 1.5 LED Signaling System

| Parameter | Details |
|---|---|
| Hardware | WS2812B addressable RGB LED strip (8 LEDs per drone, distributed around frame) |
| Control | Jetson GPIO → FPGA → LED data line (800 kHz serial protocol) |
| Visibility | 500m+ daylight (high-brightness variant), 1km+ at night |
| Power | ~0.3W typical, ~2W max (all white full brightness) |

**LED State Table:**

| Pattern | Color | Meaning |
|---|---|---|
| Solid | Green | Normal operations |
| Solid | Blue | Flight Leader role |
| Pulsing | Yellow | Low battery / RTB imminent |
| Rapid flash | Red | Emergency / collision warning |
| Alternating | Red/Blue | Law enforcement identification |
| Chase pattern | White | Search pattern active |
| Off | — | Stealth/covert mode |
| Rainbow cycle | Multi | System boot / self-test |

LED patterns are commanded via ROS2 topic `/hbird/led/command` and driven by the FPGA at hardware timing precision.

---

### 1.6 Inter-Board Communication

```
┌──────────────────────────────────────────────────────────┐
│                    DRONE COMPUTE STACK                     │
│                                                            │
│  ┌─────────────┐    PCIe x4     ┌──────────────┐          │
│  │  Jetson      │◄─────────────►│  CrossLink-NX │          │
│  │  Orin NX     │               │  FPGA          │          │
│  │              │    SPI (aux)   │               │          │
│  │  - ROS2      │◄─────────────►│  - Sensor DSP │          │
│  │  - Comms SW  │               │  - IR encode  │          │
│  │  - AI/ML     │    UART       │  - LED driver  │          │
│  │              │◄─────────────►│               │          │
│  └──────┬───────┘               └───────────────┘          │
│         │                                                   │
│         │ UART (/dev/ttyTHS0 or ttyTHS1)                   │
│         │ MAVLink v2, 921600 baud                          │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │  ARKV6X      │                                           │
│  │  (PX4)       │                                           │
│  │              │                                           │
│  │  - Flight    │                                           │
│  │    control   │                                           │
│  │  - IMU ×3    │                                           │
│  │  - Baro      │                                           │
│  │  - GPS       │                                           │
│  └─────────────┘                                           │
│                                                            │
│  External Radios:                                          │
│  ┌──────────┐  Ethernet    ┌──────────┐  UART              │
│  │ Doodle   │◄────────────►│          │◄────────►RFD900x   │
│  │ Labs Mesh│  (100Base-T) │  Jetson  │  (TTL)             │
│  └──────────┘              │          │                    │
│  ┌──────────┐  M.2 PCIe   │          │                    │
│  │ EM9291   │◄────────────►│          │                    │
│  │ 5G       │              └──────────┘                    │
│  └──────────┘                                              │
└──────────────────────────────────────────────────────────┘
```

**Interface Summary:**

| Link | Bus | Speed | Protocol |
|---|---|---|---|
| Jetson ↔ ARKV6X | UART | 921600 baud | MAVLink v2 (via MAVSDK/px4_ros_com) |
| Jetson ↔ FPGA | PCIe x4 Gen3 | ~4 GB/s | Custom DMA (sensor frames, video preprocessing) |
| Jetson ↔ FPGA (aux) | SPI | 50 MHz | Register read/write, config |
| Jetson ↔ Doodle Labs | 100 Base-T | 100 Mbps | IP/UDP |
| Jetson ↔ RFD900x | UART | 57600–921600 | Custom binary serial |
| Jetson ↔ EM9291 | PCIe Gen3 x1 | ~1 GB/s | IP/TCP/UDP via wwan0 |
| FPGA → IR emitters | GPIO | ~1 kbps | OOK modulated |
| FPGA → LEDs | GPIO | 800 kHz | WS2812B protocol |

**Source (ARKV6X ↔ Jetson):** [PX4 ARK Jetson PAB Carrier Docs](https://docs.px4.io/main/en/companion_computer/ark_jetson_pab_carrier)

---

## 2. Software Layer

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                      │
│  Mission Planner │ Swarm Coordinator │ AI/Perception     │
├─────────────────────────────────────────────────────────┤
│                SWARM PROTOCOL ENGINE                     │
│  Election │ Discovery │ Goal Distribution │ Aggregation  │
├─────────────────────────────────────────────────────────┤
│          COMMUNICATIONS ABSTRACTION LAYER (CAL)          │
│  Unified Send/Recv │ Priority Router │ Link Monitor     │
├────────────┬────────────┬────────────┬──────────────────┤
│  MeshRadio │  RFD900x   │  Cellular  │  IR/LED          │
│  Manager   │  Manager   │  Manager   │  Manager         │
├────────────┴────────────┴────────────┴──────────────────┤
│               ROS2 / DDS / Iceoryx                       │
├─────────────────────────────────────────────────────────┤
│          PREEMPT_RT Linux Kernel                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Communications Abstraction Layer (CAL)

The CAL is the centerpiece — a custom C++ library that provides a **transport-agnostic interface** to all radio hardware.

```cpp
// cal/include/cal/transport_interface.hpp
namespace hbird::cal {

enum class Priority : uint8_t {
    SAFETY_CRITICAL = 0,   // Collision avoidance, emergency stop
    COMMAND         = 1,   // Goal distribution, re-tasking
    ELECTION        = 2,   // Leader election, fitness broadcasts
    TELEMETRY       = 3,   // Position, battery, health
    BULK_DATA       = 4,   // Video, sensor logs
    BEST_EFFORT     = 5    // Diagnostics, debug
};

enum class TransportId : uint8_t {
    MESH_2G4   = 0,  // Doodle Labs 2.4 GHz
    RFD_900    = 1,  // RFD900x 900 MHz
    CELLULAR   = 2,  // EM9291 LTE/5G
    IR         = 3,  // IR close-range
    LOOPBACK   = 255 // Local test
};

struct TransportStatus {
    TransportId id;
    bool available;
    int8_t rssi_dbm;
    uint32_t throughput_bps;   // current estimated
    uint16_t latency_ms;       // rolling avg RTT
    float packet_loss_ratio;   // 0.0 – 1.0
    uint64_t bytes_tx;
    uint64_t bytes_rx;
};

class ITransport {
public:
    virtual ~ITransport() = default;
    virtual TransportId id() const = 0;
    virtual bool initialize(const YAML::Node& config) = 0;
    virtual bool send(const uint8_t* data, size_t len, 
                      const Address& dest, Priority prio) = 0;
    virtual void set_receive_callback(ReceiveCallback cb) = 0;
    virtual TransportStatus status() const = 0;
    virtual uint32_t max_mtu() const = 0;
    virtual void shutdown() = 0;
};

} // namespace hbird::cal
```

**Key design decisions:**
- All transports implement `ITransport` — adding a new radio = one new class
- Priority is embedded at the CAL level, not the transport level
- Each transport reports its own health metrics continuously
- Configuration via YAML files (`/etc/hbird/transports/*.yaml`)

### 2.3 Message Router

The Message Router sits above the CAL and makes routing decisions:

```cpp
// cal/include/cal/message_router.hpp
namespace hbird::cal {

class MessageRouter {
public:
    // Register a transport plugin
    void register_transport(std::unique_ptr<ITransport> transport);
    
    // Send a message — router picks best transport(s)
    SendResult send(const SwarmMessage& msg);
    
    // Multicast to all reachable nodes
    SendResult broadcast(const SwarmMessage& msg);
    
    // Subscribe to incoming messages by type
    void subscribe(MessageType type, MessageCallback cb);

private:
    // Priority queue per transport — SAFETY_CRITICAL always first
    std::array<PriorityQueue, 6> tx_queues_;  // one per priority level
    
    // Transport selection policy
    TransportId select_transport(const SwarmMessage& msg);
    
    // Fallback chain: MESH → RFD900 → CELLULAR
    std::vector<TransportId> fallback_chain_;
    
    // Link quality monitor
    LinkQualityMonitor link_monitor_;
};

} // namespace hbird::cal
```

**Routing Policy:**

| Priority | Primary Transport | Fallback | Max Latency Budget |
|---|---|---|---|
| SAFETY_CRITICAL | Mesh + RFD900x (simultaneous) | Cellular | 10 ms |
| COMMAND | Mesh | RFD900x → Cellular | 50 ms |
| ELECTION | Mesh | RFD900x | 100 ms |
| TELEMETRY | Mesh | RFD900x → Cellular | 200 ms |
| BULK_DATA | Mesh (if BW available) | Cellular | 1000 ms |
| BEST_EFFORT | Mesh | Dropped if unavailable | 5000 ms |

**Safety-critical messages are sent on ALL available transports simultaneously** (redundant delivery). The receiver deduplicates via message ID.

### 2.4 Radio Interface Managers

#### 2.4.1 Mesh Radio Manager (`MeshTransport`)

```cpp
class MeshTransport : public ITransport {
    // Connects to Doodle Labs via Ethernet socket
    // Doodle Labs runs OpenWrt — we use raw UDP sockets
    // Multicast group 239.0.0.1:PORT for broadcast
    // Unicast UDP for point-to-point
    // Leverages URLLC channel for Priority 0-1
    // Standard channel for Priority 2-5
    
    int eth_socket_;          // Raw UDP socket to mesh interface
    std::string mesh_iface_;  // "eth1" typically
    
    // Doodle Labs API integration for channel/power control
    DoodleLabsAPI dl_api_;    // REST API on 192.168.1.1
};
```

The Doodle Labs radio exposes a REST management API on its internal IP. We use this to:
- Monitor link quality and neighbor table
- Adjust channel bandwidth dynamically (20→10→5 MHz as range increases)
- Read mesh routing table for topology awareness
- Configure QoS queues mapping to our priority levels

#### 2.4.2 RFD900x Manager (`Rfd900Transport`)

```cpp
class Rfd900Transport : public ITransport {
    // Serial UART interface
    // Framed binary protocol over transparent serial link
    // FHSS handles RF-level robustness
    
    int serial_fd_;              // /dev/ttyTHS2
    uint32_t baud_rate_;         // 57600 default, 115200 for higher throughput
    Rfd900Framer framer_;        // COBS framing for binary data
    
    // AT command interface for config
    void configure_radio();      // Set air rate, TX power, net ID
};
```

**Bandwidth budget at 64 kbps air rate:**
- Heartbeat: 32 bytes × 2 Hz = 512 bps per drone
- 30 drones × 512 bps = 15.4 kbps (heartbeats alone)
- Remaining: ~48 kbps for commands and safety alerts
- At 250 kbps air rate: much more headroom but reduced range

We default to **64 kbps** for maximum range and switch to **250 kbps** when range allows.

#### 2.4.3 Cellular Manager (`CellularTransport`)

```cpp
class CellularTransport : public ITransport {
    // Standard Linux network interface (wwan0)
    // Uses UDP sockets to cloud relay server
    // TCP for reliable bulk transfers (firmware, logs)
    // WireGuard VPN tunnel for all traffic
    
    WireGuardTunnel vpn_;       // wg0 interface
    std::string relay_host_;    // Cloud relay server
    uint16_t relay_port_;       // Default 51820 (WG)
    
    // LTE gateway mode — bridge mesh traffic
    bool gateway_mode_;
    MeshBridge bridge_;
};
```

#### 2.4.4 IR/LED Manager (`IrLedTransport`)

```cpp
class IrLedTransport : public ITransport {
    // Communicates with FPGA via shared memory (Iceoryx)
    // FPGA handles all timing-critical modulation
    // Very limited: ID beacons, dock commands only
    
    FpgaSharedMem fpga_mem_;
    
    // IR is not a general-purpose transport
    uint32_t max_mtu() const override { return 4; } // 4 bytes max
};
```

### 2.5 ROS2 Integration

#### 2.5.1 What We Use from ROS2/Aerostack2

| Component | Source | Use |
|---|---|---|
| `px4_ros_com` | PX4/ROS2 bridge | MAVLink ↔ ROS2 topics for flight controller |
| `px4_msgs` | PX4 message definitions | Standard PX4 message types |
| Aerostack2 `as2_platform_px4` | Aerostack2 | Platform interface to PX4 |
| Aerostack2 behavior trees | Aerostack2 | Mission behavior framework |
| `ros2_shared_memory_transport` | ROS2 | Iceoryx zero-copy within single drone |
| `tf2` | ROS2 | Coordinate frame transforms |
| `diagnostics` | ROS2 | System health monitoring |

#### 2.5.2 What We Build Custom

| Component | Reason |
|---|---|
| `hbird_cal` (Communications Abstraction Layer) | No existing ROS2 package handles multi-radio swarm comms |
| `hbird_swarm_protocol` | Custom election, discovery, goal distribution |
| `hbird_mesh_transport` | Doodle Labs-specific integration |
| `hbird_rfd_transport` | RFD900x serial framing |
| `hbird_cell_transport` | Cellular gateway/bridge logic |
| `hbird_ir_led` | FPGA interface for IR/LED |
| `hbird_link_monitor` | Cross-radio health monitoring and failover |
| `hbird_crypto` | End-to-end encryption layer |

#### 2.5.3 ROS2 Topics (Communications)

```
# Outbound (application → CAL)
/hbird/cal/tx                    # SwarmMessage to send
/hbird/cal/broadcast             # SwarmMessage to broadcast

# Inbound (CAL → application)
/hbird/cal/rx                    # Received SwarmMessage
/hbird/cal/rx/safety             # Safety-critical only (separate for RT)
/hbird/cal/rx/command            # Commands only

# Transport status
/hbird/cal/status                # Array of TransportStatus
/hbird/cal/link_quality          # Per-neighbor link quality
/hbird/cal/topology              # Mesh topology snapshot

# Swarm protocol
/hbird/swarm/heartbeat           # Heartbeat broadcast
/hbird/swarm/election/fitness    # Fitness score broadcast
/hbird/swarm/election/result     # Election results
/hbird/swarm/discovery/announce  # New drone announcement
/hbird/swarm/goal                # Goal assignments (down from leader)
/hbird/swarm/status_agg          # Aggregated status (up to leader)

# Flight controller
/fmu/in/vehicle_command          # PX4 commands (via px4_ros_com)
/fmu/out/vehicle_status          # PX4 status
/fmu/out/vehicle_gps_position    # GPS data

# LED control
/hbird/led/command               # LED pattern command
/hbird/ir/rx                     # IR received data
```

### 2.6 DDS / Iceoryx Integration

**Intra-drone (single machine):** Iceoryx zero-copy shared memory transport. All ROS2 nodes on a single drone communicate via Iceoryx — no serialization, no network stack, sub-microsecond latency.

**Inter-drone (across radios):** We do NOT use DDS discovery across the mesh. DDS multicast discovery is too chatty for constrained radio links. Instead:

1. The CAL serializes `SwarmMessage` structs into our custom binary format (see Protocol Layer)
2. Binary payloads are sent over UDP via the appropriate radio
3. On the receiving drone, the CAL deserializes and publishes to local ROS2 topics via Iceoryx

This gives us the best of both: zero-copy local IPC AND efficient radio utilization.

```
Drone A                              Drone B
┌──────────────────┐                ┌──────────────────┐
│ ROS2 Node        │                │ ROS2 Node        │
│   ↕ Iceoryx      │                │   ↕ Iceoryx      │
│ CAL Router       │                │ CAL Router       │
│   ↕ serialize    │                │   ↕ deserialize  │
│ MeshTransport    │ ══UDP/Radio══► │ MeshTransport    │
└──────────────────┘                └──────────────────┘
```

**Iceoryx Configuration (`/etc/iceoryx/roudi_config.toml`):**
```toml
[general]
version = 1

[[segment]]
reader = ["hbird"]
writer = ["hbird"]

[[segment.mempool]]
size = 128
count = 1000    # Small messages (heartbeats, commands)

[[segment.mempool]]
size = 1024
count = 500     # Medium messages (telemetry)

[[segment.mempool]]
size = 65536
count = 50      # Large messages (sensor data)

[[segment.mempool]]
size = 1048576
count = 10      # Video frames
```

---

## 3. Protocol Layer

### 3.1 Swarm Protocol — "HBP" (Hummingbird Binary Protocol)

All inter-drone and Nest↔drone communication uses HBP regardless of transport.

### 3.2 Message Format

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│  MAGIC (0xHB)   │ VER │PRI│ FLAGS │        MESSAGE TYPE          │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│                      SEQUENCE NUMBER (32-bit)                     │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│         SOURCE ID (16-bit)        │     DESTINATION ID (16-bit)   │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│                      TIMESTAMP (32-bit, ms since epoch mod 2^32) │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│         PAYLOAD LENGTH (16-bit)   │      HEADER CRC16            │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│                        PAYLOAD (variable)                         │
│                            ...                                    │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│                      AUTH TAG (128-bit, AES-GCM)                  │
│                            ...                                    │
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

**Header: 20 bytes fixed**

| Field | Bits | Description |
|---|---|---|
| MAGIC | 16 | `0x4842` ("HB") — fast rejection of non-HBP data |
| VER | 4 | Protocol version (0–15), current = 1 |
| PRI | 4 | Priority level (0=SAFETY_CRITICAL … 5=BEST_EFFORT) |
| FLAGS | 8 | Bit flags: `[encrypted, compressed, ack_req, fragment, multicast, reserved×3]` |
| MESSAGE TYPE | 16 | Enum of message types (see below) |
| SEQUENCE | 32 | Monotonic per-source, used for dedup and ordering |
| SOURCE ID | 16 | Sender drone ID (0x0000 = Nest, 0x0001–0x00FF = drones) |
| DEST ID | 16 | Receiver (0xFFFF = broadcast, 0xFFFE = flight-leader-group) |
| TIMESTAMP | 32 | Milliseconds since GPS epoch mod 2^32 (~49.7 day rollover) |
| PAYLOAD LEN | 16 | Payload bytes (max 65535, but MTU-constrained per transport) |
| HEADER CRC | 16 | CRC-16/CCITT of header bytes 0–17 |

**Auth Tag: 16 bytes** — AES-128-GCM authentication tag over header + payload. Provides both integrity and authentication.

**Total overhead:** 36 bytes per message (20 header + 16 auth tag).

### 3.3 Message Types

```cpp
enum class MessageType : uint16_t {
    // Safety (Priority 0)
    COLLISION_ALERT      = 0x0001,  // Imminent collision warning
    EMERGENCY_STOP       = 0x0002,  // E-stop command
    GEOFENCE_BREACH      = 0x0003,  // Geofence violation alert
    AIRSPACE_ALERT       = 0x0004,  // Manned aircraft detected
    
    // Command (Priority 1)
    GOAL_ASSIGN          = 0x0100,  // Goal assignment (Nest→Leader→Drone)
    GOAL_UPDATE          = 0x0101,  // Goal modification
    GOAL_CANCEL          = 0x0102,  // Goal cancellation
    RTB_COMMAND          = 0x0103,  // Return to base
    FORMATION_CMD        = 0x0104,  // Formation change
    WAYPOINT_CMD         = 0x0105,  // Waypoint navigation
    
    // Election (Priority 2)
    FITNESS_BROADCAST    = 0x0200,  // Fitness score announcement
    ELECTION_START       = 0x0201,  // Trigger new election
    ELECTION_VOTE        = 0x0202,  // Vote for candidate
    ELECTION_RESULT      = 0x0203,  // Elected leader announcement
    LEADER_HEARTBEAT     = 0x0204,  // Leader alive signal
    LEADER_ABDICATE      = 0x0205,  // Leader stepping down
    
    // Telemetry (Priority 3)
    POSITION_REPORT      = 0x0300,  // GPS + IMU fused position
    BATTERY_STATUS       = 0x0301,  // Battery voltage, current, remaining
    HEALTH_STATUS        = 0x0302,  // Sensor health, compute load
    MISSION_STATUS       = 0x0303,  // Current goal progress
    WEATHER_LOCAL        = 0x0304,  // Wind, temp from onboard sensors
    AGGREGATED_STATUS    = 0x0305,  // Leader → Nest: group summary
    
    // Discovery (Priority 2)
    ANNOUNCE             = 0x0400,  // "I exist" broadcast
    ANNOUNCE_ACK         = 0x0401,  // Welcome response
    TOPOLOGY_UPDATE      = 0x0402,  // Mesh neighbor table
    SYNC_REQUEST         = 0x0403,  // Time sync request
    SYNC_RESPONSE        = 0x0404,  // Time sync response
    
    // Bulk Data (Priority 4)
    VIDEO_FRAME          = 0x0500,  // H.265 video frame fragment
    SENSOR_DATA          = 0x0501,  // Thermal, multispectral data
    MAP_TILE             = 0x0502,  // Orthomosaic tile
    LOG_UPLOAD           = 0x0503,  // Flight log segment
    
    // System (Priority 5)
    FIRMWARE_CHUNK       = 0x0600,  // OTA firmware update
    CONFIG_UPDATE        = 0x0601,  // Configuration change
    DEBUG_MSG            = 0x0602,  // Debug/diagnostic
    PING                 = 0x0603,  // Latency measurement
    PONG                 = 0x0604,  // Latency response
};
```

### 3.4 Key Payload Structures

#### Position Report (40 bytes)
```cpp
struct PositionReport {
    int32_t  lat_e7;         // Latitude × 1e7 (degrees)
    int32_t  lon_e7;         // Longitude × 1e7 (degrees)  
    int32_t  alt_mm;         // Altitude MSL (millimeters)
    int16_t  vx_cms;         // Velocity North (cm/s)
    int16_t  vy_cms;         // Velocity East (cm/s)
    int16_t  vz_cms;         // Velocity Down (cm/s)
    uint16_t heading_cdeg;   // Heading (centidegrees, 0-35999)
    uint8_t  fix_type;       // GPS fix type
    uint8_t  satellites;     // Number of satellites
    uint16_t hdop;           // HDOP × 100
    uint16_t vdop;           // VDOP × 100
    int16_t  roll_cdeg;      // Roll (centidegrees)
    int16_t  pitch_cdeg;     // Pitch (centidegrees)
    uint32_t flight_time_s;  // Seconds since takeoff
    uint16_t ground_speed_cms; // Ground speed cm/s
    uint16_t _reserved;
};
```

#### Fitness Broadcast (16 bytes)
```cpp
struct FitnessBroadcast {
    uint16_t drone_id;
    uint16_t fitness_score;  // 0-10000 composite score
    uint8_t  battery_pct;    // 0-100
    uint8_t  sensor_health;  // Bitfield: [cam, thermal, lidar, imu, gps, ...]
    uint8_t  compute_load;   // CPU % (0-100)
    int8_t   mesh_rssi;      // Best mesh RSSI (dBm, signed)
    uint8_t  drone_count;    // Number of drones this node can hear
    uint8_t  is_candidate;   // 1 = willing to be leader
    uint16_t uptime_min;     // Minutes since boot
    uint32_t _reserved;
};
```

#### Goal Assignment (variable, typical ~80 bytes)
```cpp
struct GoalAssign {
    uint32_t goal_id;          // Unique goal identifier
    uint16_t target_drone_id;  // 0xFFFF = group goal
    uint8_t  goal_type;        // enum: SEARCH, TRACK, ORBIT, OVERWATCH, RTB, LAND
    uint8_t  priority;         // Goal priority (for local resource allocation)
    int32_t  wp_lat_e7;        // Target latitude
    int32_t  wp_lon_e7;        // Target longitude
    int32_t  wp_alt_mm;        // Target altitude
    uint16_t radius_m;         // Operating radius (meters)
    uint16_t duration_s;       // Goal duration (0 = indefinite)
    uint16_t speed_cms;        // Desired speed (cm/s, 0 = default)
    uint8_t  sensor_mode;      // Which sensors to activate
    uint8_t  params_len;       // Additional params length
    uint8_t  params[];         // Goal-type-specific parameters (variable)
};
```

### 3.5 Encryption and Authentication

**Scheme:** AES-128-GCM (Galois/Counter Mode)

- **Why AES-128 not 256:** Performance. AES-128-GCM runs ~2× faster on ARM NEON (Jetson) and the Doodle Labs hardware AES supports 128-bit at full throughput vs 12 Mbps for 256-bit. AES-128 remains secure against all known attacks.
- **Why GCM:** Provides authenticated encryption — integrity + confidentiality + authentication in one operation. No need for separate HMAC.
- **IV/Nonce:** 96-bit nonce = `source_id (16) || sequence_number (32) || random (48)`. Sequence numbers are monotonic, guaranteeing nonce uniqueness per source.

**Key Management:**

```
Key Hierarchy:
├── Master Key (256-bit) — provisioned at manufacturing, stored in Jetson secure enclave (NVIDIA Trusty TEE)
│   ├── Swarm Session Key (128-bit) — derived per mission via HKDF
│   │   ├── Mesh Encryption Key — used for all HBP messages
│   │   └── Per-Drone Auth Key — for individual drone authentication
│   └── Nest-Drone Key (128-bit) — for Nest ↔ individual drone secure channel
└── LTE VPN Key — WireGuard key pair, rotated weekly
```

**Key Distribution:**
1. Drones receive the Master Key during provisioning (factory or secure loading station)
2. On mission start, Nest broadcasts an encrypted `SESSION_KEY_DISTRIBUTE` message (encrypted with Master Key)
3. Session keys rotate every 4 hours or on Nest command
4. If a drone is compromised, Nest issues `KEY_REVOKE` with new session key excluding the compromised drone ID

**Authentication:** Every HBP message carries the 128-bit GCM auth tag. Receivers verify before processing. Messages failing auth are silently dropped and logged.

### 3.6 Priority Levels and Radio Mapping

| Priority | Name | Radios | Behavior |
|---|---|---|---|
| 0 | SAFETY_CRITICAL | Mesh + RFD900x (simultaneous) | Redundant TX, preempts queue, max 10ms |
| 1 | COMMAND | Mesh (primary), RFD900x (fallback) | Reliable delivery (ACK), retry 3× |
| 2 | ELECTION | Mesh (primary), RFD900x (fallback) | Broadcast, no ACK needed |
| 3 | TELEMETRY | Mesh | Rate-limited per drone (10 Hz position, 1 Hz health) |
| 4 | BULK_DATA | Mesh or Cellular | Fragmented, best-effort on mesh, reliable on cellular |
| 5 | BEST_EFFORT | Mesh only | Dropped under congestion, no retry |

### 3.7 Heartbeat / Keepalive Design

```
Every drone broadcasts:
  POSITION_REPORT    @ 10 Hz  (Priority 3, Mesh only, 40 bytes)
  HEALTH_STATUS      @  1 Hz  (Priority 3, Mesh only, 24 bytes)
  FITNESS_BROADCAST  @  0.5 Hz (Priority 2, Mesh + RFD900x, 16 bytes)

Flight Leaders additionally broadcast:
  LEADER_HEARTBEAT   @  2 Hz  (Priority 2, Mesh + RFD900x, 8 bytes)
  AGGREGATED_STATUS  @  0.5 Hz (Priority 3, Mesh → Nest, variable)
```

**Failure Detection Timeouts:**

| Condition | Timeout | Action |
|---|---|---|
| No POSITION_REPORT from drone | 2 s | Mark drone STALE, alert leader |
| No POSITION_REPORT from drone | 10 s | Mark drone LOST, remove from mesh table |
| No LEADER_HEARTBEAT | 3 s | Trigger leader re-election |
| No Nest heartbeat | 30 s | Enter autonomous mission continuation |
| No Nest heartbeat | 300 s (5 min) | Begin phased RTB |

### 3.8 Flight Leader Election Protocol

**Algorithm: Modified Bully with Fitness Scoring**

The election uses a **fitness score** (0–10000) computed locally by each drone:

```cpp
uint16_t compute_fitness() {
    float score = 0.0f;
    
    // Battery (30% weight) — higher is better
    score += 3000.0f * (battery_pct / 100.0f);
    
    // Sensor health (20% weight) — all sensors working = max
    score += 2000.0f * (healthy_sensors / total_sensors);
    
    // Compute load (15% weight) — lower is better
    score += 1500.0f * (1.0f - cpu_load / 100.0f);
    
    // Signal strength (20% weight) — best mesh RSSI normalized
    score += 2000.0f * normalize_rssi(mesh_rssi);
    
    // Connectivity (15% weight) — more neighbors = better leader
    score += 1500.0f * std::min(1.0f, neighbors / 10.0f);
    
    return static_cast<uint16_t>(std::clamp(score, 0.0f, 10000.0f));
}
```

**Election Flow:**

```
1. TRIGGER: Leader heartbeat timeout (3s) OR explicit LEADER_ABDICATE
     │
2. ELECTION_START broadcast (any drone can trigger)
     │
3. ELECTION WINDOW: 500ms
   │  All drones broadcast FITNESS_BROADCAST with is_candidate=1
     │
4. Each drone independently determines winner:
   │  - Highest fitness score wins
   │  - Tie-breaker: lowest drone_id
   │  - Drone must have is_candidate=1
     │
5. Winner broadcasts ELECTION_RESULT
     │
6. All drones ACK by including new leader_id in next heartbeat
     │
7. If no ELECTION_RESULT within 2s → retry from step 2 (max 3 retries)
     │
8. If 3 retries fail → each drone operates autonomously (no leader)
```

**Subgroup elections:** When the mesh fragments, each fragment independently elects its own leader. When fragments rejoin, the leader with the higher fitness score becomes the unified leader. The other leader sends `LEADER_ABDICATE`.

---

## 4. Network Topology

### 4.1 Overall Architecture

```
                            ┌─────────────┐
                            │   CLOUD     │
                            │  RELAY SVR  │
                            └──────┬──────┘
                                   │ Internet
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                NEST (Ground Station)         │
            │  ┌──────────┐  ┌─────────┐  ┌────────────┐ │
            │  │Doodle    │  │RFD900x  │  │LTE/5G      │ │
            │  │Labs Mesh │  │Base Stn │  │Backhaul    │ │
            │  │(Master)  │  │         │  │            │ │
            │  └────┬─────┘  └────┬────┘  └─────┬──────┘ │
            │       │             │              │        │
            └───────┼─────────────┼──────────────┼────────┘
                    │             │              │
         ┌──────── │2.4 GHz──────│──────────────│─────────┐
         │   MESH  │   MESH      │ 900MHz       │ LTE     │
         │         │             │              │         │
    ┌────▼──┐ ┌───▼───┐   ┌────▼──┐      ┌───▼───┐     │
    │Drone 1│◄►│Drone 2│◄─►│Drone 3│      │Drone 4│     │
    │       │  │(FL)   │   │       │      │(LTE   │     │
    │       │  │       │   │       │      │ GW)   │     │
    └───┬───┘  └───┬───┘   └───┬───┘      └───┬───┘     │
        │          │           │              │         │
        ◄──────────►───────────►──────────────►         │
              2.4 GHz Mesh (all interconnected)          │
         │                                               │
         │   ┌───────┐ ┌───────┐     ┌───────┐          │
         │   │Drone 5│ │Drone 6│ ... │Drone30│          │
         │   └───────┘ └───────┘     └───────┘          │
         └───────────────────────────────────────────────┘
```

### 4.2 Mesh Topology and Routing

**Doodle Labs Mesh Rider routing:**
- Self-forming, self-healing MANET (Mobile Ad-hoc Network)
- Layer 2 transparent bridging mode (all drones appear on same L2 segment)
- Optimized Link State Routing (OLSR) variant built into firmware
- Automatic path selection based on link quality metrics (ETX)
- Multi-hop: up to ~8 hops before throughput degrades significantly
- Each drone is both a node and a relay

**Our overlay on top of mesh:**
- HBP multicast (`239.0.0.1:18420`) for broadcasts (heartbeats, election, discovery)
- HBP unicast (UDP, port `18421`) for point-to-point messages
- HBP leader channel (`239.0.0.2:18420`) for leader-only multicast group

**Bandwidth Planning (30 drones, 20 MHz channel = 80 Mbps aggregate):**

| Traffic Type | Per Drone | × 30 Drones | Total |
|---|---|---|---|
| Position (10 Hz, 76 bytes) | 6.1 kbps | 183 kbps | |
| Health (1 Hz, 60 bytes) | 0.5 kbps | 15 kbps | |
| Fitness (0.5 Hz, 52 bytes) | 0.2 kbps | 6 kbps | |
| Commands (burst) | ~1 kbps avg | 30 kbps | |
| Video (1 stream) | 2–8 Mbps | N/A | |
| **Subtotal C2** | | **~234 kbps** | |
| **Video (3 active)** | | **~12 Mbps** | |
| **Total** | | **~12.2 Mbps** | **15% of capacity** |

Comfortable headroom. Even with 10 simultaneous video streams (~40 Mbps), we use only 50% of mesh capacity.

### 4.3 LTE Gateway Bridging

One drone per subgroup is designated the **LTE Gateway** (elected role, similar to flight leader but based on signal strength):

```
Drones ──mesh──► LTE Gateway Drone ──LTE──► Cloud Relay ──► Nest
```

**Gateway selection criteria:**
1. Best LTE signal strength (RSRP > −100 dBm)
2. Battery > 30% (LTE radio consumes extra power)
3. Not the Flight Leader (avoid single point of failure)

**Gateway responsibilities:**
- NAT/bridge mesh traffic to LTE tunnel
- Aggregate video streams (forward only active/requested streams)
- Compress and batch telemetry for efficiency
- Maintain WireGuard VPN to cloud relay

**Failover:** If LTE gateway loses cellular, next-best drone auto-promotes. If no drone has cellular coverage, fall back to mesh-only (Nest direct via mesh or RFD900x).

### 4.4 RFD900x Fallback Scenarios

The 900 MHz link activates when:
1. Mesh RSSI drops below −85 dBm for >5 seconds
2. Mesh packet loss exceeds 30%
3. Safety-critical messages (always sent on both)
4. Drones at extreme range (>8 km from nearest mesh peer)

**900 MHz Network Configuration:**
- Multipoint mode (all drones share one network ID)
- Air rate: 64 kbps default (max range), 250 kbps if range <10 km
- Only carries: heartbeats, safety alerts, commands, election traffic
- NO video, NO bulk data on 900 MHz

**Nest has a high-power RFD900x base station** with directional antenna (Yagi, ~10 dBi gain) for 40+ km range to any drone.

### 4.5 Range Analysis

| Link | Hardware | Typical Range (LOS) | Urban/NLOS | Throughput |
|---|---|---|---|---|
| Mesh 2.4 GHz | Doodle Labs + 3 dBi omni | 10–15 km | 2–5 km | 80 Mbps |
| Mesh 2.4 GHz | Doodle Labs + 8 dBi directional | 25–40 km | N/A | 80 Mbps |
| 900 MHz | RFD900x + dipole | 20–40 km | 5–10 km | 64–250 kbps |
| 900 MHz | RFD900x + Yagi (Nest) | 40–80 km | 10–20 km | 64 kbps |
| LTE/5G | EM9291 | Cell coverage | Cell coverage | Up to 3.5 Gbps |
| IR | Custom 850nm | 0.5–30 m | N/A | ~1 kbps |

### 4.6 Latency Budget

| Path | Expected Latency | Budget |
|---|---|---|
| Drone → Drone (mesh, 1 hop) | 2–5 ms | 10 ms |
| Drone → Drone (mesh, 3 hops) | 8–15 ms | 25 ms |
| Drone → Nest (mesh direct) | 3–10 ms | 20 ms |
| Drone → Nest (RFD900x) | 50–150 ms | 200 ms |
| Drone → Cloud (LTE) | 20–80 ms | 150 ms |
| Drone → Cloud → Nest | 40–120 ms | 200 ms |
| IR close-range | <1 ms | 5 ms |
| Intra-drone (Iceoryx) | <10 µs | 100 µs |

---

## 5. Degraded Operations

### 5.1 Degradation Levels

```
LEVEL 0: FULL COMMS        — All radios operational, Nest connected
LEVEL 1: DEGRADED MESH     — Mesh quality poor, using RFD900x supplement
LEVEL 2: MESH LOST         — No mesh, RFD900x + LTE only
LEVEL 3: NEST DISCONNECTED — No Nest comms, swarm self-organizing
LEVEL 4: FRAGMENTED SWARM  — Mesh split into disconnected subgroups
LEVEL 5: SOLO              — All radios lost, fully autonomous
```

### 5.2 Loss of Mesh Link (Single Drone)

```
Trigger: No mesh packets received for 5s
  │
  ├─► Attempt mesh re-association (scan channels)
  ├─► Activate RFD900x as primary link
  ├─► Report via RFD900x: HEALTH_STATUS with mesh_down flag
  ├─► If in subgroup: Leader marks drone as "mesh-degraded"
  ├─► Continue mission via RFD900x C2
  └─► If RFD900x also lost → escalate to LEVEL 5
```

### 5.3 Loss of All Radio (LEVEL 5 — Fully Autonomous)

```
Trigger: No packets on ANY transport for 30s
  │
  ├─► Enter AUTONOMOUS SAFE mode
  ├─► Continue current goal for up to 5 minutes
  ├─► Maintain safe altitude and separation (visual/IR avoidance)
  ├─► Periodically attempt radio re-acquisition (every 10s)
  ├─► After 5 min with no goal progress → initiate RTB
  ├─► RTB via pre-loaded waypoints (stored locally)
  ├─► If RTB path blocked → orbit at safe altitude, continue radio attempts
  └─► After 30 min total isolation → emergency land at nearest safe point
```

**Pre-loaded safety data (always cached locally):**
- RTB waypoints (Nest GPS coordinates + approach path)
- Geofence boundaries
- No-fly zones
- Emergency landing zones (pre-surveyed)
- Last known positions of all swarm members (for deconfliction)

### 5.4 Loss of Nest Connectivity

```
Trigger: No Nest heartbeat for 30s
  │
  ├─► Flight Leader assumes tactical authority
  ├─► Continue current mission goals (already distributed)
  ├─► Leader can re-task drones within mission parameters
  ├─► Compress and store telemetry locally for later upload
  ├─► Attempt Nest reconnection via all transports
  │     ├─ Mesh: increase TX power, try alternate channels
  │     ├─ RFD900x: switch to lower air rate for more range
  │     └─ LTE: try alternate APN, cellular scan
  │
  ├─► After 5 min: reduce mission scope (tighten operating area)
  ├─► After 15 min: begin orderly RTB of low-battery drones
  └─► After 30 min: full swarm RTB
```

### 5.5 Partial Mesh / Fragmented Swarm

```
Trigger: Mesh neighbor count drops, topology splits detected
  │
  ├─► Each fragment independently elects a local Flight Leader
  ├─► Local leaders attempt cross-fragment comms via:
  │     ├─ RFD900x (900 MHz has longer range, may bridge fragments)
  │     ├─ LTE relay (both fragments → cloud → reconnect)
  │     └─ Dispatch relay drones to bridge gaps (if available)
  │
  ├─► Fragments operate semi-independently:
  │     ├─ Each continues mission within its area
  │     ├─ Coordinate via RFD900x/LTE if available
  │     └─ Avoid overlapping search areas (use pre-divided sectors)
  │
  └─► On rejoin: leaders negotiate (higher fitness = unified leader)
       └─ Merge topology tables, deduplicate goals, reconcile state
```

### 5.6 Degradation Decision Matrix

| Condition | Mesh | RFD900x | LTE | Action |
|---|---|---|---|---|
| Normal | ✅ | ✅ | ✅ | Full operations |
| Urban canyon | ❌ | ✅ | ✅ | C2 via 900MHz, video via LTE |
| Rural beyond cell | ✅ | ✅ | ❌ | Normal mesh ops, no cloud relay |
| Jammed 2.4GHz | ❌ | ✅ | ✅ | C2 via 900MHz, data via LTE |
| Jammed 2.4+900 | ❌ | ❌ | ✅ | All traffic via LTE (high latency C2) |
| No coverage | ❌ | ❌ | ❌ | LEVEL 5: Autonomous + RTB |

---

## 6. Cloud/Ground Layer

### 6.1 Nest Ground Station Hardware

```
┌────────────────────────────────────────────────────────┐
│                    NEST GROUND STATION                   │
│                                                          │
│  ┌──────────────┐  Antenna:                             │
│  │ Doodle Labs  │  2× sector antennas (120° each)       │
│  │ Mesh Rider   │  or 1× omni (360°) + 1× directional  │
│  │ (Base Unit)  │  Coverage: full swarm operating area   │
│  │ 2.4 GHz      │  Interface: 100Base-T to Nest server  │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────┐  Antenna:                             │
│  │ RFD900x      │  1× Yagi directional (~10 dBi)       │
│  │ (Base Unit)  │  or 1× omni (omnidirectional)         │
│  │ 900 MHz      │  Interface: USB-UART to Nest server   │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────┐                                       │
│  │ LTE/5G       │  Sierra Wireless RV55 industrial      │
│  │ Router       │  gateway (or EM9291 in custom board)  │
│  │              │  Interface: GbE to Nest server        │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────┐                                       │
│  │ Nest Server  │  Intel NUC or ruggedized mini-PC      │
│  │ (Compute)    │  Ubuntu 22.04, ROS2 Humble            │
│  │              │  Runs: Mission Planner, CAD bridge,   │
│  │              │  SwarmOS, Operator UI backend          │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────┐                                       │
│  │ UPS Battery  │  ~2hr runtime for portable ops        │
│  └──────────────┘                                       │
│                                                          │
│  Optional:                                               │
│  ┌──────────────┐                                       │
│  │ Starlink     │  Backup satellite backhaul            │
│  │ Terminal     │  for remote/disaster deployments      │
│  └──────────────┘                                       │
└────────────────────────────────────────────────────────┘
```

### 6.2 Cloud Relay Architecture

```
┌─────────┐    LTE/5G    ┌──────────────┐    WAN    ┌─────────────┐
│  Drone  │──WireGuard──►│ Cloud Relay  │◄─────────►│ Nest Server │
│  (LTE   │   VPN        │ Server       │ WireGuard │ (if remote) │
│  Gateway)│              │              │   VPN     │             │
└─────────┘              │  - UDP relay │           └─────────────┘
                          │  - Video MUX │
                          │  - Auth/ACL  │           ┌─────────────┐
                          │  - Logging   │◄─────────►│ Operator    │
                          │  - API GW    │  HTTPS/   │ Web Console │
                          └──────────────┘  WSS      └─────────────┘
```

**Cloud Relay Server:**
- Deployed on AWS/GCP in region closest to operating area
- WireGuard VPN hub — all drones and Nest connect
- Lightweight UDP relay (not processing, just forwarding)
- Video multiplexer: receives H.265 streams, transcodes to WebRTC for operator console
- REST API for external integrations (CAD systems)
- Runs in containers (Kubernetes) for auto-scaling

**Data flows through cloud:**

| Flow | Protocol | Purpose |
|---|---|---|
| Drone → Cloud → Nest | UDP/WireGuard | Telemetry relay when mesh unavailable |
| Drone → Cloud → Console | WebRTC | Live video streaming to operators |
| Nest → Cloud → Drone | UDP/WireGuard | Commands when mesh unavailable |
| CAD → Cloud → Nest | REST/HTTPS | Dispatch calls, incident updates |
| Cloud → Cloud | Internal | Logging, analytics, ML training data |

### 6.3 CAD/Dispatch Integration

```
┌───────────┐   CAD2CAD    ┌──────────────┐   REST    ┌───────────┐
│ 911 CAD   │──(NENA i3)──►│ Hummingbird  │◄─────────►│ Nest      │
│ System    │   or NIEM     │ Cloud API    │          │ Server    │
│           │               │              │          │           │
│ Tyler New │   webhook     │  - Incident  │ pub/sub  │  Mission  │
│ World     │──────────────►│    Ingest    │─────────►│  Planner  │
│ Hexagon   │               │  - Resource  │          │           │
│ Motorola  │◄──────────────│    Status    │◄─────────│  Status   │
│           │   status push │  - Mapping   │          │  Engine   │
└───────────┘               └──────────────┘          └───────────┘
```

**Integration protocol:**
- Inbound: Webhook receivers for major CAD systems (Tyler New World, Hexagon, Motorola PremierOne)
- Standard: NENA i3 / NIEM CAD-to-CAD when available
- Outbound: Push drone status/video URLs back to CAD for dispatcher view
- Authentication: OAuth 2.0 + API keys per agency

**Data exchanged:**

| Direction | Data | Format |
|---|---|---|
| CAD → Hummingbird | Incident (type, location, priority) | JSON/NIEM |
| CAD → Hummingbird | Dispatch request (units needed, constraints) | JSON |
| Hummingbird → CAD | Drone ETA, status, position | JSON |
| Hummingbird → CAD | Video feed URL (WebRTC/RTSP) | URL |
| Hummingbird → CAD | Aerial situation report | JSON |

### 6.4 Operator Interface Data Flows

```
Operator Tablet/Laptop
    │
    │ WebSocket (wss://)
    │ + WebRTC (video)
    │
    ▼
┌──────────────────┐
│ Nest UI Backend  │  (Node.js or Rust web server)
│                  │
│ /api/swarm       │ → Swarm status, positions (1 Hz push)
│ /api/mission     │ → Mission CRUD
│ /api/drone/:id   │ → Individual drone detail
│ /api/video/:id   │ → Video stream negotiation (WebRTC signaling)
│ /api/command     │ → Manual override commands
│ /ws/live         │ → WebSocket: real-time telemetry stream
└──────────────────┘
    │
    │ ROS2 bridge (rosbridge_suite or custom)
    │
    ▼
┌──────────────────┐
│ Nest ROS2 Nodes  │
│                  │
│ swarm_manager    │ → Aggregates all drone states
│ mission_planner  │ → Goal generation and assignment
│ cal_node         │ → Communications (sends/receives HBP)
│ video_router     │ → Video stream management
└──────────────────┘
```

---

## 7. Extensibility

### 7.1 Plugin Architecture for Transports

New radio types are added by implementing the `ITransport` interface and dropping a shared library into `/opt/hbird/transports/`:

```
/opt/hbird/
├── transports/
│   ├── libmesh_transport.so      # Doodle Labs
│   ├── librfd900_transport.so    # RFD900x
│   ├── libcell_transport.so      # LTE/5G
│   ├── libir_transport.so        # IR
│   └── libstarlink_transport.so  # Future: Starlink direct
├── config/
│   ├── transports.yaml           # Which transports to load
│   ├── mesh.yaml                 # Mesh-specific config
│   ├── rfd900.yaml               # RFD900x config
│   └── cellular.yaml             # Cellular config
└── plugins/
    └── protocol/
        ├── libhbp_v1.so          # Protocol v1 codec
        └── libhbp_v2.so          # Future protocol versions
```

**Transport discovery (plugin loading):**
```yaml
# /opt/hbird/config/transports.yaml
transports:
  - name: mesh_2g4
    library: libmesh_transport.so
    enabled: true
    config: mesh.yaml
    
  - name: rfd900
    library: librfd900_transport.so
    enabled: true
    config: rfd900.yaml
    
  - name: cellular
    library: libcell_transport.so
    enabled: true
    config: cellular.yaml
    
  - name: ir
    library: libir_transport.so
    enabled: true
    config: ir.yaml
```

At startup, the CAL scans `transports.yaml`, `dlopen()`s each library, calls the factory function `create_transport()`, and registers it with the Message Router.

### 7.2 Adding New Message Types

Message types are defined in a protobuf-like IDL file and compiled to C++ structs:

```
# /opt/hbird/protocol/messages.hbp

@version 1
@namespace hbird::msg

message PositionReport : 0x0300 {
    int32  lat_e7;
    int32  lon_e7;
    int32  alt_mm;
    # ... etc
}

# Adding a new message — just add to the file:
message ChemicalDetection : 0x0350 {
    uint16 sensor_id;
    uint8  chemical_type;    # enum
    float32 concentration_ppm;
    int32  lat_e7;
    int32  lon_e7;
}
```

The HBP codec is versioned (4-bit version in header). Old drones ignore unknown message types gracefully (skip payload based on PAYLOAD_LEN).

### 7.3 Protocol Versioning

- Header version field (4 bits) supports 16 protocol versions
- Backward compatible: new fields added at end of payloads
- Breaking changes increment version — drones negotiate version on discovery
- Nest can run multi-version codec to support mixed fleets during OTA rollout

### 7.4 Future Extension Points

| Extension | How It Plugs In |
|---|---|
| New radio (e.g., Starlink, UHF, LoRa) | New `ITransport` plugin + config YAML |
| New message type | Add to `.hbp` IDL, recompile codec |
| New election algorithm | Swap `ElectionStrategy` implementation |
| New encryption scheme | Swap `CryptoProvider` (interface already abstracted) |
| Inter-swarm communication | New overlay protocol on top of CAL |
| Drone-to-vehicle (ground robots) | Same HBP protocol, new transport for 802.11p or similar |
| AI-driven routing | Replace `select_transport()` with ML model |

### 7.5 ROS2 Composition

All comms nodes are designed as ROS2 **composable nodes** (components). They can be loaded into a single process for zero-copy intra-process communication, or run as separate processes for isolation:

```xml
<!-- /opt/hbird/launch/comms.launch.xml -->
<launch>
  <node_container pkg="rclcpp_components" exec="component_container_mt" name="comms_container">
    <composable_node pkg="hbird_cal" plugin="hbird::cal::MessageRouterNode" />
    <composable_node pkg="hbird_cal" plugin="hbird::cal::MeshTransportNode" />
    <composable_node pkg="hbird_cal" plugin="hbird::cal::Rfd900TransportNode" />
    <composable_node pkg="hbird_cal" plugin="hbird::cal::CellularTransportNode" />
    <composable_node pkg="hbird_cal" plugin="hbird::cal::IrLedNode" />
    <composable_node pkg="hbird_cal" plugin="hbird::cal::LinkMonitorNode" />
    <composable_node pkg="hbird_swarm" plugin="hbird::swarm::ElectionNode" />
    <composable_node pkg="hbird_swarm" plugin="hbird::swarm::DiscoveryNode" />
    <composable_node pkg="hbird_crypto" plugin="hbird::crypto::CryptoNode" />
  </node_container>
</launch>
```

---

## Appendix A: Bandwidth Budget Summary

| Traffic | Rate | Size (w/ HBP overhead) | Per Drone | 30 Drones |
|---|---|---|---|---|
| Position telemetry | 10 Hz | 76 B | 6.1 kbps | 183 kbps |
| Health status | 1 Hz | 60 B | 0.5 kbps | 15 kbps |
| Fitness broadcast | 0.5 Hz | 52 B | 0.2 kbps | 6 kbps |
| Leader heartbeat | 2 Hz | 44 B | 0.7 kbps | 0.7 kbps |
| Commands (burst avg) | ~0.1 Hz | ~116 B | 0.1 kbps | 3 kbps |
| **Total C2 overhead** | | | | **~208 kbps** |
| Video stream (H.265) | continuous | — | 2–8 Mbps | 3 streams = 12 Mbps |
| **Total with video** | | | | **~12.2 Mbps** |
| **Mesh capacity** | | | | **80 Mbps** |
| **Utilization** | | | | **~15%** |

## Appendix B: Source URLs

| Component | URL |
|---|---|
| Doodle Labs mini-OEM 2.4GHz | https://techlibrary.doodlelabs.com/doodle-labs-mini-oem-mesh-rider-radio-24002482-mhz |
| Doodle Labs product page | https://doodlelabs.com/product/oem/ |
| RFD900x Datasheet | https://files.rfdesign.com.au/Files/documents/RFD900x%20DataSheet%20V1.2.pdf |
| RFD900x Specs (SpektreWorks) | https://spektreworks.com/product/rfd-900x-modem/ |
| Sierra Wireless EM9291 | https://www.sierrawireless.com/iot-modules/5g-modules/em9291/ |
| ARKV6X Flight Controller | https://docs.px4.io/main/en/flight_controller/ark_v6x |
| ARK Jetson PAB Carrier | https://docs.px4.io/main/en/companion_computer/ark_jetson_pab_carrier |
| PX4 ROS2 Bridge | https://docs.px4.io/main/en/ros2/ |
| Iceoryx | https://iceoryx.io/ |

## Appendix C: Glossary

| Term | Definition |
|---|---|
| CAL | Communications Abstraction Layer |
| HBP | Hummingbird Binary Protocol |
| FL | Flight Leader |
| MANET | Mobile Ad-hoc Network |
| URLLC | Ultra-Reliable Low Latency Communication |
| COFDM | Coded Orthogonal Frequency Division Multiplexing |
| FHSS | Frequency Hopping Spread Spectrum |
| OOK | On-Off Keying |
| ETX | Expected Transmission Count (routing metric) |
| RTB | Return To Base |
| GCM | Galois/Counter Mode (authenticated encryption) |
| TEE | Trusted Execution Environment |

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-03-04 | Initial document |
| 2026-03-11 | **Source error corrections:** Doodle Labs mini-OEM specs corrected from manufacturer datasheet ([Doodle Labs Tech Library](https://techlibrary.doodlelabs.com/doodle-labs-mini-oem-mesh-rider-radio-24002482-mhz)): weight 102g → 36.5g, dimensions 57×86×13mm → Baseband 47×28×5mm / RF Board 46×51×6.5mm, power 5-36 VDC → 5V ±5% (5W avg/8W peak/2W Rx), antenna RP-SMA → MMCX-Female, Ethernet GbE → 100 Base-T. All GbE references to Doodle Labs updated to 100 Base-T throughout. |
