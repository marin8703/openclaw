# Hummingbird Drone Swarm — Cybersecurity Architecture

> **Version:** 1.0.1 · **Date:** 2026-03-05 · **Classification:** CONFIDENTIAL — INTERNAL USE ONLY
> **Scope:** 30-drone swarm per Nest, first responder / public safety use

**Changelog:**
| Date | Version | Changes |
|------|---------|---------|
| 2026-03-04 | 1.0 | Initial cybersecurity architecture document |
| 2026-03-05 | 1.0.1 | Specified 3DR ZED-F9P RTK GPS (2× per drone, $411 each) in GPS security section |
| 2026-03-11 | 1.0.2 | **Source error corrections:** 3DR ZED-F9P price $411 → $540 per [3DR Store](https://store.3dr.com/zed-f9p-advanced-rtk-gnss-module-w-wifi-compass/). ATECC608B price ~$0.60 → ~$0.90 per DigiKey pricing. CJIS version header corrected from v6.0 → v5.9.5 to match linked document. |

---

## Table of Contents

1. [Threat Model](#1-threat-model)
2. [Hardware Security](#2-hardware-security)
3. [Communications Security](#3-communications-security)
4. [Software Security](#4-software-security)
5. [Swarm-Specific Security](#5-swarm-specific-security)
6. [GPS / Navigation Security](#6-gps--navigation-security)
7. [Data Security](#7-data-security)
8. [Operational Security](#8-operational-security)
9. [Compliance & Standards](#9-compliance--standards)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [References](#11-references)

---

## 1. Threat Model

### 1.1 Threat Actor Profiles

| Actor | Capability | Motivation | Likelihood (First Responder) |
|-------|-----------|------------|------------------------------|
| **Nation-state** | Full spectrum (RF, cyber, physical, supply chain) | Intelligence, disruption of emergency ops | Low–Medium |
| **Criminal organization** | Moderate cyber, RF jammers, physical interception | Evade surveillance, disrupt law enforcement | Medium–High |
| **Hobbyist/hacktivist** | Off-the-shelf SDR, open-source exploit tools | Notoriety, protest | Medium |
| **Insider threat** | Privileged access, knowledge of architecture | Financial gain, coercion, ideology | Low–Medium |

### 1.2 Threat Matrix

| # | Threat | Likelihood | Impact | Risk | Primary Mitigation |
|---|--------|-----------|--------|------|---------------------|
| T1 | **GPS spoofing** | **HIGH** | **CRITICAL** | **CRITICAL** | Sensor fusion, cross-swarm validation, Septentrio upgrade path |
| T2 | **GPS jamming** | **HIGH** | **HIGH** | **HIGH** | Multi-source nav (VIO, IMU dead-reckoning, inter-drone ranging) |
| T3 | **RF jamming (2.4 GHz mesh)** | **HIGH** | **HIGH** | **HIGH** | Tri-radio failover, autonomous operation mode |
| T4 | **RF jamming (all bands)** | Medium | **CRITICAL** | **HIGH** | Pre-programmed RTB, autonomous mission continuation |
| T5 | **Rogue drone injection** | Medium | **CRITICAL** | **HIGH** | Cryptographic identity, IR proximity auth, behavioral analysis |
| T6 | **Man-in-the-middle (mesh)** | Low | **HIGH** | Medium | AES-128-GCM + mutual auth (Doodle Labs handles link layer) |
| T7 | **MITM (LTE backhaul)** | Low | **HIGH** | Medium | mTLS application layer over carrier encryption |
| T8 | **Physical capture** | Medium | **HIGH** | **HIGH** | Tamper response, secure element, remote wipe |
| T9 | **Firmware tampering** | Low–Med | **CRITICAL** | **HIGH** | Secure boot chain, code signing, runtime integrity |
| T10 | **Supply chain attack** | Low | **CRITICAL** | Medium | NDAA compliance, hardware attestation, vendor audits |
| T11 | **Sensor data manipulation** | Low | **HIGH** | Medium | Cross-drone validation, sensor fusion anomaly detection |
| T12 | **Denial of service** | Medium | **HIGH** | **HIGH** | Rate limiting, priority queuing, mesh self-healing |
| T13 | **Insider threat** | Low–Med | **CRITICAL** | Medium | MFA, RBAC, audit logging, separation of duties |
| T14 | **OTA update compromise** | Low | **CRITICAL** | Medium | Dual-signed packages, rollback protection, staged rollout |

### 1.3 Attack Surface Summary

```
┌─────────────────────────────────────────────────────────┐
│                    ATTACK SURFACE                        │
├──────────────┬──────────────────────────────────────────┤
│ RF (wireless)│ 2.4 GHz mesh, 900 MHz backup, LTE/5G,   │
│              │ GPS L1/L2, IR transceivers               │
├──────────────┼──────────────────────────────────────────┤
│ Physical     │ Drone body, debug ports (JTAG/SWD),      │
│              │ SD/NVMe, USB, sensor inputs              │
├──────────────┼──────────────────────────────────────────┤
│ Software     │ ROS2 DDS, PX4 MAVLink, HBP protocol,    │
│              │ OTA update channel, Nest web interface   │
├──────────────┼──────────────────────────────────────────┤
│ Supply chain │ Component sourcing, firmware build,      │
│              │ factory provisioning                     │
└──────────────┴──────────────────────────────────────────┘
```

---

## 2. Hardware Security

### 2.1 Jetson Orin NX — Root of Trust

**Built-in capabilities:**
- **Secure Boot:** RSA-3072 key burned into OTP fuses → UEFI → kernel → rootfs chain of trust
- **Platform Security Controller (PSC):** Dedicated security co-processor for boot, key management, TrustZone
- **Disk Encryption:** LUKS2 with hardware-derived keys (KDK — Key Derivation Key)
- **TrustZone:** ARM TrustZone for secure world isolation

**Implementation:**

```
Boot Chain:
  BootROM (immutable) → MB1 (signed) → MB2 (signed) → UEFI (signed)
  → kernel (signed) → initrd (signed, dm-verity) → rootfs (dm-verity)
```

1. **Burn OTP fuses** with RSA-3072 public key hash during factory provisioning
2. **Enable secure boot** via `BootSecurityInfo` fuse (value `0x9` for RSA-3072)
3. **Encrypt rootfs** using LUKS2 with KDK-derived key — keys never leave the SoC
4. **Enable dm-verity** on rootfs for runtime integrity verification
5. **Disable JTAG** via fuse (irreversible) for production units

**Reference:** [NVIDIA Jetson Secure Boot Documentation](https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/Security/SecureBoot.html)

### 2.2 STM32H7 Flight Controller (ARKV6X)

**Built-in capabilities:**
- **RDP Level 2:** Permanent read-out protection (irreversible, prevents JTAG/SWD debug)
- **Hardware Crypto Acceleration:** AES-256, SHA-256, TRNG
- **Secure user memory (HDP):** Write-protected boot area for secure bootloader
- **Unique Device ID:** 96-bit factory-programmed UID

**Implementation:**

1. **Secure bootloader** in HDP area validates PX4 firmware signature (Ed25519) before execution
2. **RDP Level 2** for production (Level 1 for development — allows re-flash with mass erase)
3. **Firmware encryption:** AES-256-CBC encrypted firmware images, decrypted using chip-unique key derived from UID + provisioned secret
4. **Anti-rollback:** Monotonic version counter in OTP bits — firmware must have version ≥ stored counter

**Reference:** [ST STM32 Security Application Note](https://www.st.com/resource/en/application_note/dm00493651-introduction-to-stm32-microcontrollers-security-stmicroelectronics.pdf)

### 2.3 CrossLink-NX FPGA

**Built-in capabilities:**
- **AES-256 bitstream encryption** with key stored in non-volatile memory
- **ECC-256 bitstream authentication**
- **TRNG, AES, HMAC/SHA** hardware engines
- **Password protection** for configuration interface

**Implementation:**

1. **Enable bitstream encryption** — program AES-256 key during factory provisioning
2. **Enable bitstream authentication** — ECC-256 signature verification on every configuration load
3. **Disable external configuration readback** — prevent IP extraction
4. **Use TRNG** for nonce generation in sensor preprocessing security functions

**Reference:** [Lattice CrossLink-NX-33 Data Sheet (FPGA-DS-02104)](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6448/FPGADS0210410CrossLinkNX33andCrossLinkUNX.pdf)

### 2.4 Secure Element: ATECC608B

**RECOMMENDATION: ADD to each drone.** Weight: 0.5g. Cost: ~$0.90 ([DigiKey](https://www.digikey.com/en/products/detail/microchip-technology/ATECC608B-MAHDA-S/13415130)). I²C interface to Jetson.

**Justification:** The Jetson PSC handles boot-time security, but we need a dedicated secure element for:
- **Drone identity key storage** — private keys never leave the SE
- **ECDH key agreement** for session keys — hardware-accelerated P-256
- **Certificate storage** — X.509 device certificate
- **Monotonic counters** — anti-replay, anti-rollback
- **Secure boot attestation** — signed boot measurements

**Why not a full TPM?**
- TPM 2.0 modules add 3-5g, $15-30, and 2-5ms latency per crypto operation
- ATECC608B provides the critical subset (key storage, ECDH, ECDSA) in a UDFN package at <1ms per operation
- Jetson PSC already provides most TPM-like functions for the Linux side

**Alternative considered:** Microchip ATECC608B-TFLXTLS (pre-provisioned with Microchip CA for zero-touch provisioning) or Infineon OPTIGA Trust M (supports larger key storage, but bigger package).

### 2.5 Tamper Detection & Response

**Physical security layers:**

| Layer | Mechanism | Response |
|-------|-----------|----------|
| **L1 — Enclosure** | Tamper-evident seals, torx screws | Visual inspection |
| **L2 — Switch** | Micro-switch on enclosure lid → GPIO on Jetson | Log event, alert Nest |
| **L3 — Mesh** | Conductive mesh over PCB (optional, production) | Zeroize keys in ATECC608B |
| **L4 — Software** | Boot-time hardware attestation check | Refuse to join swarm if tampered |

**Key zeroization procedure:**
1. Tamper event triggers secure element `Nuke` command
2. ATECC608B overwrites all private key slots with zeros
3. Jetson receives tamper interrupt → logs event → broadcasts swarm alert → initiates safe landing
4. Total zeroization time: <10ms

### 2.6 Hardware Security Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    DRONE PCB                         │
│                                                     │
│  ┌──────────┐    I²C    ┌────────────┐              │
│  │ ATECC608B├───────────┤ Jetson     │              │
│  │ Secure   │           │ Orin NX    │              │
│  │ Element  │           │            │              │
│  │ • Keys   │    SPI    │ • PSC      │   UART      │
│  │ • Certs  ├───────────┤ • TrustZone├─────────┐   │
│  │ • Counters│          │ • dm-verity│         │   │
│  └──────────┘           └─────┬──────┘         │   │
│                               │ SPI            │   │
│                         ┌─────┴──────┐   ┌─────┴──┐│
│                         │CrossLink-NX│   │ARKV6X  ││
│                         │ FPGA       │   │STM32H7 ││
│                         │ • AES-256  │   │• RDP L2││
│                         │ • ECC-256  │   │• HDP   ││
│                         │ • TRNG     │   │• Crypto││
│                         └────────────┘   └────────┘│
│                                                     │
│  ┌────────────┐ ┌─────────┐ ┌──────────┐           │
│  │Doodle Labs │ │RFD900x  │ │Sierra EM │           │
│  │Mesh Rider  │ │900MHz   │ │9291 LTE  │           │
│  │FIPS 140-3  │ │AES-HW   │ │std crypto│           │
│  └────────────┘ └─────────┘ └──────────┘           │
│                                                     │
│  [Tamper Switch] ──── GPIO ──── Jetson              │
└─────────────────────────────────────────────────────┘
```

---

## 3. Communications Security

### 3.1 Security Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: Application     HBP Swarm Protocol         │
│          Security        AES-128-GCM + HMAC         │
├─────────────────────────────────────────────────────┤
│ Layer 3: Transport       mTLS (LTE), DTLS (mesh)    │
│          Security        Session keys from ECDH      │
├─────────────────────────────────────────────────────┤
│ Layer 2: Link            Doodle Labs AES-256 (mesh)  │
│          Security        RFD900x AES-128 (backup)    │
│                          Carrier encryption (LTE)    │
├─────────────────────────────────────────────────────┤
│ Layer 1: Physical        IR proximity auth           │
│          Security        LED challenge-response      │
└─────────────────────────────────────────────────────┘
```

**Defense in depth:** Even if one layer is compromised, the others provide protection. An attacker must break both link-layer AND application-layer encryption.

### 3.2 Key Management

#### 3.2.1 Key Hierarchy

```
Root CA (offline, HSM-protected at HQ)
  └── Nest CA (per Nest base station, in Nest HSM)
        ├── Drone Certificate (per drone, in ATECC608B)
        │     └── Session Keys (ephemeral, ECDH-derived)
        └── Operator Certificate (per operator, in smart card/YubiKey)
```

#### 3.2.2 Key Types and Lifecycle

| Key | Algorithm | Storage | Lifetime | Rotation |
|-----|-----------|---------|----------|----------|
| **Root CA** | ECDSA P-384 | Offline HSM (e.g., YubiHSM 2) | 10 years | Manual ceremony |
| **Nest CA** | ECDSA P-256 | Nest onboard HSM | 2 years | Annual ceremony |
| **Drone Identity** | ECDSA P-256 | ATECC608B slot | Lifetime of drone | Re-provisioning only |
| **Swarm Session** | AES-128-GCM | Jetson RAM (volatile) | 1 hour or mission | Automatic ECDH rekey |
| **Flight Leader Session** | AES-128-GCM | Jetson RAM | Leader tenure | On leader change |
| **Nest-Drone Channel** | AES-256-GCM | Jetson RAM | Per connection | On reconnect |
| **Mesh Link** | AES-256 | Doodle Labs radio | Configurable | Per mission or periodic |
| **RFD900x Link** | AES-128 | RFD900x radio | Configurable | Per mission |

#### 3.2.3 Key Distribution Protocol

**Initial provisioning (factory/depot):**
1. Generate ECDSA P-256 keypair inside ATECC608B (private key never exported)
2. ATECC608B outputs CSR (Certificate Signing Request)
3. Nest CA signs certificate → stored in ATECC608B and Nest database
4. Pre-share Doodle Labs mesh key and RFD900x encryption key via secure provisioning station

**Mission key establishment (runtime):**
1. Drone powers on → presents certificate to Nest via LTE or mesh
2. Nest validates certificate chain (drone cert → Nest CA → Root CA)
3. Mutual ECDH key agreement (P-256) → derive session keys using HKDF-SHA256
4. Session keys loaded into HBP protocol engine
5. **Latency:** ~15ms for ECDH on ATECC608B hardware, one-time per session

**Key rotation during mission:**
- Session keys rotate every 60 minutes or 2^32 packets (whichever first)
- Rotation uses ECDH rekey with new ephemeral keypairs
- Old keys zeroized immediately after rotation
- **Perfect Forward Secrecy:** Ephemeral ECDH ensures compromise of long-term identity key does not compromise past sessions

#### 3.2.4 Key Revocation

- **Certificate Revocation List (CRL):** Maintained on Nest, distributed to all drones at mission start and periodically
- **Short-lived certificates:** Consider 24-hour drone certificates signed at mission start (reduces CRL dependency)
- **Emergency revocation:** Nest broadcasts signed revocation message on all channels; drones immediately exclude revoked peer
- **Physical capture scenario:** Operator marks drone as compromised in Nest → CRL updated → all drones reject that identity within 1 second

### 3.3 Per-Radio Security

#### 3.3.1 Doodle Labs Mesh Rider (2.4 GHz) — PRIMARY

**What Doodle Labs provides:**
- FIPS 140-3 Level 1 validated cryptographic module
- AES-256 or AES-128 link-layer encryption
- Self-forming/self-healing mesh with encrypted management frames
- Frequency hopping for interference avoidance

**What we add on top:**
- Application-layer AES-128-GCM (HBP protocol) — defense in depth
- Mutual authentication via certificate exchange before application data flows
- Doodle Labs mesh key rotated per-mission (configured via secure provisioning API)

**Latency impact:** Doodle Labs hardware crypto adds <0.5ms. Application-layer GCM adds <0.3ms (Jetson hardware AES-NI). **Total overhead: <1ms.**

#### 3.3.2 RFD900x (900 MHz) — BACKUP / WEAK LINK

**Current state:**
- SiK firmware supports AES hardware-accelerated encryption (128-bit)
- Static pre-shared key (configured via AT commands)
- No mutual authentication
- No perfect forward secrecy
- No anti-replay protection at link layer
- Key must be manually configured (no dynamic key exchange)

**Hardening measures:**

| Priority | Measure | Implementation |
|----------|---------|----------------|
| **P1** | Enable AES-128 encryption | Set `ENCRYPTION_LEVEL=1` and configure 128-bit key |
| **P1** | Application-layer HBP encryption | Same AES-128-GCM as mesh — RFD900x is just a transport pipe |
| **P1** | Reduce to telemetry/C2 only | No sensitive payload data over 900 MHz |
| **P2** | Per-mission key rotation | Provisioning station updates key before each deployment |
| **P2** | Message sequence numbers | HBP protocol layer provides anti-replay (see §3.5) |
| **P3** | Custom firmware investigation | Fork SiK to add ECDH key exchange (significant effort) |

**Risk acceptance:** RFD900x is backup-only. With application-layer HBP encryption on top, the static link-layer key is a secondary concern. Document this in risk register.

#### 3.3.3 Sierra Wireless EM9291 (LTE/5G) — BACKHAUL

**Carrier-provided security:**
- 4G: 128-bit AES encryption (EEA2), SNOW 3G integrity (EIA1)
- 5G: 256-bit encryption, enhanced subscriber privacy (SUPI/SUCI)

**What we add:**
- **mTLS** for Nest↔Cloud and Nest↔Drone backhaul channels
- **Certificate pinning** — drones only accept Nest's specific certificate
- **Application-layer encryption** — HBP protocol encrypted regardless of transport
- **VPN tunnel** (WireGuard) for cloud connectivity — adds ~2ms, acceptable for non-real-time backhaul

### 3.4 IR Side-Channel Authentication

**Purpose:** Physical proximity verification that cannot be spoofed remotely.

**Protocol:**
1. Drone A transmits random challenge via IR (close range, <5m, line-of-sight)
2. Drone B signs challenge with ATECC608B private key, returns signature via IR
3. Drone A verifies signature against B's certificate
4. Mutual authentication (B also challenges A)
5. **Result:** Drones that have IR-authenticated each other get elevated trust score

**Use cases:**
- **Swarm join:** New drone must IR-authenticate with ≥2 existing swarm members before joining
- **Landing verification:** Drone IR-authenticates with Nest before landing on charging pad
- **Post-partition reunion:** When swarm fragments reconnect, IR re-authentication required

**Latency:** ~50ms round-trip (IR is slow). Acceptable because this is a one-time gate, not on the hot path.

### 3.5 Anti-Replay Protection

**HBP protocol header (added fields):**

```c
struct hbp_security_header {
    uint32_t sequence_number;    // Per-sender monotonic counter
    uint32_t timestamp_ms;       // Milliseconds since mission start
    uint8_t  nonce[8];           // Random nonce (from ATECC608B TRNG)
    uint8_t  auth_tag[16];       // AES-128-GCM authentication tag
};
// Total overhead: 32 bytes per message
```

**Validation rules:**
- Reject if `sequence_number ≤ last_seen[sender_id]` (sliding window of 64 allows reordering)
- Reject if `|timestamp_ms - local_time_ms| > 500ms` (clock skew tolerance)
- Reject if GCM auth tag verification fails
- **Latency:** Sequence/timestamp check: <1μs. GCM verify: <0.2ms on Jetson AES-NI.

---

## 4. Software Security

### 4.1 Secure Boot Chain (Complete)

```
┌────────────────────────────────────────────────────┐
│ POWER ON                                            │
│                                                     │
│ 1. Jetson BootROM (immutable silicon)               │
│    └─ Verify MB1 signature (RSA-3072, OTP key)     │
│                                                     │
│ 2. MB1 Bootloader                                   │
│    └─ Verify MB2 signature                          │
│                                                     │
│ 3. MB2 Bootloader                                   │
│    └─ Verify UEFI signature                         │
│    └─ Initialize PSC, derive disk encryption keys   │
│                                                     │
│ 4. UEFI                                             │
│    └─ Verify kernel + initrd signatures             │
│    └─ Measure boot components (PCR-like)            │
│                                                     │
│ 5. Linux Kernel (PREEMPT_RT)                        │
│    └─ dm-verity validates rootfs blocks on read     │
│    └─ IMA (Integrity Measurement Architecture)      │
│         validates executables on exec               │
│                                                     │
│ 6. Init → ROS2 Launch                               │
│    └─ SROS2 security plugins loaded                 │
│    └─ HBP daemon authenticates with Nest            │
│                                                     │
│ 7. ATECC608B attestation                            │
│    └─ Sign boot measurements → send to Nest         │
│    └─ Nest verifies before allowing swarm join      │
│                                                     │
│ ═══ PARALLEL: STM32H7 Boot ═══                     │
│                                                     │
│ A. STM32 secure bootloader (in HDP area)            │
│    └─ Verify PX4 firmware signature (Ed25519)       │
│    └─ Check anti-rollback counter                   │
│    └─ Decrypt firmware (AES-256-CBC)                │
│                                                     │
│ B. PX4 firmware starts                              │
│    └─ Verify Jetson handshake (shared secret)       │
│                                                     │
│ ═══ PARALLEL: FPGA Boot ═══                        │
│                                                     │
│ X. CrossLink-NX loads encrypted bitstream           │
│    └─ AES-256 decryption + ECC-256 auth             │
│    └─ Configuration complete in <3ms                │
└────────────────────────────────────────────────────┘
```

**Total secure boot time:** ~8-12 seconds (Jetson dominates). Acceptable for power-on; drones pre-boot before mission.

### 4.2 Code Signing

| Artifact | Signing Algorithm | Signed By | Verification Point |
|----------|------------------|-----------|-------------------|
| Jetson bootloader chain | RSA-3072 | Build server HSM | BootROM / each stage |
| Linux kernel + modules | RSA-3072 | Build server HSM | UEFI + IMA |
| ROS2 application packages | Ed25519 | CI/CD pipeline | Package manager |
| PX4 firmware | Ed25519 | Build server HSM | STM32 secure bootloader |
| FPGA bitstream | ECC-256 | Build workstation | CrossLink-NX silicon |
| OTA update bundles | Ed25519 + RSA-3072 (dual) | Release manager + build HSM | Nest + drone update agent |

**Dual-signature OTA:** Both an automated build signature AND a human release manager signature required. Prevents compromised CI/CD from pushing malicious updates.

### 4.3 OTA Update Security

**Update flow:**
1. Build server produces signed, encrypted update bundle
2. Bundle uploaded to Nest (via authenticated, encrypted channel)
3. Nest validates dual signatures
4. Nest distributes to drones (only when on ground / in Nest)
5. Drone validates dual signatures independently
6. Drone checks anti-rollback version counter
7. A/B partition scheme — new image written to inactive partition
8. Reboot into new partition; if boot fails 3×, automatic rollback to previous
9. Post-update attestation sent to Nest

**Constraints:**
- **No OTA during flight** — updates only applied when docked in Nest
- **Staged rollout** — update 1 drone first, verify 10 minutes, then batch of 5, then remaining
- **Network-independent** — updates can be loaded via USB at depot (air-gapped option)

### 4.4 ROS2 / SROS2 Security

**SROS2** provides DDS-Security plugin integration:

| DDS Security Plugin | Function | Our Configuration |
|---------------------|----------|-------------------|
| **Authentication** | Mutual auth between ROS2 nodes | PKI-based (X.509 certificates per node enclave) |
| **Access Control** | Topic-level publish/subscribe permissions | Governance XML with signed policies |
| **Cryptographic** | Encrypt/sign DDS messages | AES-256-GCM for inter-process DDS |

**CRITICAL CAVEAT:** SROS2 adds latency. For the critical path (100Hz+ control loops), we use **Iceoryx zero-copy shared memory** which bypasses DDS entirely.

**Strategy:**
- **Iceoryx (intra-drone):** No network exposure → security via Linux process isolation (namespaces, seccomp, AppArmor). No encryption overhead.
- **DDS over network (inter-drone):** SROS2 enabled for all inter-drone ROS2 topics. BUT — the hot-path swarm coordination uses HBP (custom binary protocol) NOT DDS.
- **DDS for diagnostics/non-critical:** SROS2 with full encryption for telemetry, logging, configuration topics.

**Latency budget:**
- Iceoryx shared memory: ~1μs (no security overhead)
- HBP over mesh: ~0.5ms encryption + ~3ms network = ~3.5ms
- SROS2 DDS over network: ~2ms encryption + ~5ms DDS overhead = ~7ms (non-critical path only)

**Reference:** [ROS2 DDS-Security Integration](https://design.ros2.org/articles/ros2_dds_security.html), [SROS2 Security Vulnerabilities (CCS 2022)](https://tianweiz07.github.io/Papers/22-ccs-2.pdf)

**Known SROS2 issues (from CCS 2022 paper):**
- Default configurations may leak metadata
- Access control governance XML must be carefully crafted
- Discovery protocol can reveal node topology
- **Mitigation:** Restrict DDS discovery to local subnet, disable multicast discovery for inter-drone (use unicast), sign governance files

### 4.5 Memory Safety (C++ Hardening)

The hot path is C++. We cannot rewrite in Rust (too much PX4/ROS2 ecosystem dependency). Instead:

| Measure | Tool/Flag | Overhead |
|---------|-----------|----------|
| **Stack canaries** | `-fstack-protector-strong` | <1% |
| **ASLR** | Kernel default (enabled) | 0% |
| **PIE** | `-fPIE -pie` | <1% |
| **RELRO + BIND_NOW** | `-Wl,-z,relro,-z,now` | 0% runtime |
| **Fortify source** | `-D_FORTIFY_SOURCE=2` | <1% |
| **CFI (Control Flow Integrity)** | Clang `-fsanitize=cfi` | 1-3% |
| **Shadow stack** | GCC `-fcf-protection=full` (if ARM supports) | <1% |
| **ASan (dev only)** | `-fsanitize=address` | 2× slowdown (dev only!) |
| **UBSan (dev only)** | `-fsanitize=undefined` | 10-30% (dev only!) |
| **Static analysis** | `clang-tidy`, `cppcheck`, Coverity | Build-time only |
| **Fuzzing** | AFL++ / libFuzzer on parsers | CI/CD only |

**Total production runtime overhead: <5%.** Well within our latency budget.

**Critical parsers to fuzz:** HBP message parser, MAVLink parser, GPS NMEA/UBX parser, sensor data decoders.

### 4.6 Runtime Integrity Monitoring

| Mechanism | What It Checks | Frequency |
|-----------|---------------|-----------|
| **dm-verity** | Rootfs block integrity (Merkle tree) | Every block read |
| **IMA** | Executable file hashes before exec | Every exec() |
| **Watchdog** | Application liveness | 100ms heartbeat |
| **ATECC608B attestation** | Boot measurement chain | On swarm join, hourly |
| **Process allowlist** | Only expected processes running | Every 10 seconds |
| **Network allowlist** | Only expected ports/connections | Continuous (nftables) |
| **Kernel module signing** | Only signed kernel modules load | On module load |

---

## 5. Swarm-Specific Security

### 5.1 Drone Identity & Authentication

**Identity model:**
- Each drone has a unique identity rooted in ATECC608B hardware
- Identity = (Serial Number, ECDSA P-256 Public Key, X.509 Certificate)
- Certificate signed by Nest CA, chains to Root CA

**Swarm join protocol:**

```
1. Drone → Nest:  "Join request" + Certificate + Nonce
2. Nest:          Validate cert chain, check CRL, check hardware attestation
3. Nest → Drone:  "Challenge" (random 32 bytes)
4. Drone:         Sign challenge with ATECC608B private key
5. Drone → Nest:  Signature
6. Nest:          Verify signature. If valid:
7. Nest → Swarm:  "Drone X joined" (signed announcement)
8. Drone ↔ Peers: ECDH session key establishment with each neighbor
9. Drone ↔ Peers: IR proximity authentication (if physically near)
```

**Join latency:** ~200ms total (dominated by ECDH with multiple peers). One-time cost.

**Swarm leave:**
- Voluntary: Drone sends signed departure message
- Involuntary: Heartbeat timeout (500ms) → peers mark as absent → Nest notified
- Revocation: Nest sends signed revocation → all drones drop peer immediately

### 5.2 Rogue Drone Detection

**Multi-layer detection approach:**

| Method | Detection Target | Confidence | Latency |
|--------|-----------------|------------|---------|
| **Certificate validation** | Unknown identity | 100% | <50ms |
| **IR proximity auth** | Remote impersonation | 99% | ~100ms |
| **RF fingerprinting** | Cloned identity | 85-95% | ~1s |
| **Behavioral analysis** | Compromised legitimate drone | 70-90% | 5-30s |
| **Cross-drone position validation** | Spoofed position | 90-95% | <100ms |

**RF fingerprinting (future — P3):**
Each radio has unique hardware characteristics (clock drift, signal rise time, power amplifier nonlinearities). ML model trained on legitimate fleet can detect imposters. Research indicates 85-95% accuracy for similar radio models.

**Behavioral analysis engine:**
```python
# Anomaly score computed per drone, per second
anomaly_score = weighted_sum(
    position_deviation_from_formation,    # weight: 0.3
    velocity_consistency,                  # weight: 0.2
    message_frequency_deviation,           # weight: 0.15
    command_compliance_delay,              # weight: 0.15
    sensor_data_consistency,               # weight: 0.1
    communication_pattern_deviation,       # weight: 0.1
)

if anomaly_score > THRESHOLD_WARN:  # e.g., 0.7
    alert_flight_leader()
    increase_monitoring()

if anomaly_score > THRESHOLD_EJECT:  # e.g., 0.9
    flight_leader_initiates_vote()  # Requires 2/3 consensus
    if vote_passes:
        revoke_and_exclude(drone_id)
```

### 5.3 Byzantine Fault Tolerance

**Threat:** Up to f compromised drones sending false data (positions, sensor readings, votes).

**BFT requirements for 30-drone swarm:**
- Classic BFT needs n ≥ 3f + 1. For f=3 compromised drones, need n ≥ 10 in agreement.
- With 30 drones, we can tolerate up to f=9 Byzantine drones (theoretical).
- **Practical target:** Tolerate f=3 (10%) compromised drones.

**Implementation — Lightweight BFT (not blockchain):**

We do NOT use blockchain (too slow, too much overhead for real-time swarm). Instead:

1. **Sensor data cross-validation:**
   - Every drone shares position and key sensor readings with neighbors
   - Each drone independently validates neighbors against its own observations
   - Position claims validated via: inter-drone UWB ranging (future), RF signal strength triangulation, visual tracking
   - Outliers flagged (>3σ deviation from consensus)

2. **Command validation:**
   - Flight leader commands signed and sequence-numbered
   - Drones independently validate commands against mission constraints (geofence, speed limits, formation rules)
   - If >50% of drones reject a command, flight leader election triggered

3. **Voting protocol for critical decisions:**
   - Swarm-wide decisions (leader election, drone eviction, mission abort) use lightweight voting
   - Requires 2/3 supermajority (21/30 drones)
   - Votes are signed with drone identity keys
   - Timeout: 500ms — if consensus not reached, fall back to Nest authority

**Reference:** [Reputation-Enhanced PBFT for UAV Networks (2025)](https://www.researchgate.net/publication/392162174), [Dual-layer PBFT for UAV Swarm Management](https://link.springer.com/chapter/10.1007/978-3-031-96944-7_19)

### 5.4 Secure Flight Leader Election

**Current design:** Fitness scoring (signal strength, battery, position, compute load).

**Security hardening:**

| Attack | Mitigation |
|--------|-----------|
| **Fitness score manipulation** | Scores validated by neighbors (e.g., battery voltage cross-checked against flight time) |
| **Election flooding** | Rate limit: max 1 election per 30 seconds per drone |
| **Split-brain** | Nest is tiebreaker; if Nest unreachable, highest-certificate-serial wins |
| **Refusing leadership** | Mandatory acceptance; refusal = anomaly score increase |

**Election protocol:**
1. Trigger: Leader heartbeat timeout (500ms), or Nest command, or leader voluntary step-down
2. Each drone broadcasts signed fitness score
3. All drones independently compute winner (deterministic algorithm on same inputs)
4. Winner confirmed when 2/3 of drones acknowledge
5. New leader establishes leader session key with Nest
6. **Total election time: <2 seconds**

### 5.5 Swarm Partitioning Security

**Scenario:** RF jamming splits swarm into groups that can't communicate.

**Rules per partition:**
- Each partition elects its own flight leader
- Partitions operate independently with last-known mission parameters
- When partitions reconnect:
  1. Leaders exchange signed partition logs
  2. IR re-authentication of any drones not previously seen
  3. Nest adjudicates conflicts in mission state
  4. Single leader election across merged swarm

**Minimum viable partition:** 3 drones (below this, drones enter "solo safe mode" — hover/RTB)

### 5.6 Cooperative Anomaly Detection

Drones collectively monitor each other:

- **Position consensus:** Each drone maintains a position estimate for all visible peers (via radio ranging, visual, expected trajectory). Significant deviations flagged.
- **Communication monitoring:** Each drone tracks message frequency and patterns from peers. Sudden changes flagged.
- **Formation compliance:** Drones verify neighbors maintain expected formation distances.
- **Watchdog rings:** Each drone is assigned 2 "buddy" drones to intensively monitor. Buddy assignments rotate every 5 minutes.

---

## 6. GPS / Navigation Security

### 6.1 The Problem

The u-blox ZED-F9P RTK GPS receivers (2× per drone, [$199 each](https://www.digikey.com/en/products/detail/u-blox/ZED-F9P-04B/15761778); also available as 3DR integration board at higher cost) have **no built-in anti-spoofing**. They accept any valid-looking GPS signal. This is the single biggest security gap in the hardware stack.

### 6.2 Spoofing Detection (Multi-Layer)

#### Layer 1: IMU/GPS Cross-Validation (P1 — Implement Immediately)

```
Algorithm: Continuous IMU-GPS consistency check
- Integrate IMU accelerometer/gyro to predict position delta over last 100ms
- Compare predicted delta with GPS-reported delta
- If |predicted - GPS| > threshold (adaptive, based on flight dynamics):
    → GPS_SPOOFING_SUSPECT flag raised
    → Switch to IMU-only navigation for 5 seconds
    → Alert swarm and Nest
    
Threshold tuning:
- Straight flight: 2m deviation → suspect
- Aggressive maneuver: 5m deviation → suspect  
- Hover: 1m deviation → suspect

False positive rate target: <0.1% per hour
```

**Reference:** [Real-Time GPS Spoofing Detection via Multi-Sensor Fusion and TimesNet (IEEE 2025)](https://ieeexplore.ieee.org/document/10964312/)

#### Layer 2: Swarm-Based Position Validation (P1)

```
Each drone estimates neighbors' positions via:
  1. RF signal strength/timing (Doodle Labs mesh provides RSSI)
  2. Expected position from last known velocity vector
  3. Visual detection (camera-based relative positioning)

Cross-check:
  If Drone_A says it's at position X, but 3+ neighbors 
  estimate Drone_A is actually at position Y (>10m discrepancy):
    → Drone_A's GPS flagged as potentially spoofed
    → Drone_A notified to switch to alternative nav
```

#### Layer 3: GPS Signal Quality Monitoring (P1)

```
Monitor u-blox ZED-F9P diagnostic data:
  - C/N0 (carrier-to-noise ratio) — spoofed signals often have uniform, high C/N0
  - Number of satellites — sudden changes suspicious
  - HDOP/VDOP jumps — spoofing causes solution quality changes
  - Doppler shift consistency — compare expected vs measured
  - Multi-frequency consistency — L1/L2 signals should be consistent

Alert if:
  - All satellites suddenly have identical C/N0 (natural variation is 10-20 dB)
  - Satellite count drops then recovers with different constellation
  - Position jumps >5m in single epoch without corresponding IMU data
```

#### Layer 4: Barometric Cross-Check (P1)

```
Barometric altitude (from ARKV6X) vs GPS altitude:
  - Should agree within ~3m (after temperature compensation)
  - Spoofing that changes only lat/lon but not altitude: caught by 3D inconsistency
  - Spoofing that changes altitude: caught by barometer disagreement
```

#### Layer 5: Visual Odometry (P2)

```
Stereo camera + optical flow provides independent velocity estimate:
  - Compare VIO velocity with GPS velocity
  - Significant divergence → GPS suspect
  - Works best in textured environments (urban/suburban — typical first responder scenarios)
```

### 6.3 Jamming Detection and Response

| Signal | Detection | Response |
|--------|-----------|----------|
| **GPS jammed** | C/N0 drop, loss of fix, AGC level spike | Switch to IMU + VIO + barometer; alert Nest; continue mission if safe |
| **2.4 GHz jammed** | Doodle Labs reports link loss, noise floor increase | Failover to 900 MHz + LTE; reduce mesh data rate |
| **900 MHz jammed** | RFD900x RSSI drop, packet loss >50% | Rely on mesh + LTE |
| **All RF jammed** | Loss of all comm links | Autonomous behavior: complete immediate objective or RTB on dead reckoning |
| **LTE jammed** | Carrier signal loss | Mesh + 900 MHz for swarm coordination; mission continues |

**Graceful degradation order:**
1. Full connectivity (mesh + 900 MHz + LTE + GPS) — normal operations
2. GPS denied — IMU/VIO navigation, reduced precision, alert operators
3. Single radio lost — failover to remaining radios, reduced bandwidth
4. Two radios lost — minimal telemetry on remaining radio, consider RTB
5. All comms lost — autonomous RTB or safe landing, 60-second timeout before landing

### 6.4 Future: Septentrio Anti-Spoofing Upgrade Path

**Recommended upgrade:** Septentrio mosaic-X5 or AsteRx-m3

**Capabilities:**
- AIM+ anti-jamming / anti-spoofing technology
- Multi-frequency, multi-constellation
- Spoofing detection built into receiver firmware
- OSNMA (Galileo Open Service Navigation Message Authentication) support

**Integration plan:**
- Same form factor as ZED-F9P (mosaic-X5 is drop-in compatible)
- Same serial interface (UART)
- Driver update in PX4 (Septentrio already supported)
- **Estimated cost delta:** ~$200/unit more than ZED-F9P
- **Timeline:** P3 (production v2)

---

## 7. Data Security

### 7.1 Data Classification

| Classification | Examples | Encryption | Retention | Destruction |
|---------------|----------|------------|-----------|-------------|
| **CRITICAL** | Encryption keys, certificates | ATECC608B hardware | Permanent until revoked | Secure element zeroization |
| **SENSITIVE** | Mission video, sensor logs, flight paths, operator commands | AES-256 at rest | Per retention policy (typically 90 days) | Cryptographic erasure |
| **LAW ENFORCEMENT** | Evidence-grade video, photos | AES-256 at rest + chain of custody | Per CJIS policy (varies) | Per court order / policy |
| **OPERATIONAL** | Telemetry, health data, diagnostics | AES-128 at rest | 30 days | Standard deletion |
| **PUBLIC** | Drone serial number, model, operator agency | None required | Permanent | N/A |

### 7.2 Data at Rest Encryption

**Jetson NVMe/SD storage:**
- **LUKS2** full-disk encryption with hardware-derived key (KDK from Jetson PSC)
- Key sealed to secure boot state — disk unreadable if boot chain is tampered
- AES-256-XTS cipher
- Performance: NVMe throughput with LUKS2 on Jetson Orin NX: ~2 GB/s (hardware AES) — negligible impact on video recording

**Flight controller (STM32H7):**
- Flight logs stored in internal flash — protected by RDP Level 2
- No external storage on flight controller

### 7.3 Evidence Chain of Custody

For law enforcement use cases, mission data must be forensically sound:

1. **Capture:** All video/photos timestamped with GPS time + monotonic counter
2. **Hash:** SHA-256 hash computed on capture, signed with drone identity key
3. **Metadata:** Signed manifest includes: drone ID, timestamp, GPS position, operator ID, mission ID
4. **Transfer:** Data transferred to Nest via encrypted channel with integrity verification
5. **Storage:** Immutable storage on Nest (append-only filesystem or WORM storage)
6. **Access logging:** Every access to evidence data logged (who, when, what, why)
7. **Export:** Evidence exported with complete hash chain and certificate for court admissibility

### 7.4 Secure Data Destruction

**Remote wipe capability:**

| Trigger | Action | Time |
|---------|--------|------|
| Operator command | Cryptographic erasure (delete LUKS keys) | <1 second |
| Tamper detection | ATECC608B key zeroization + LUKS key deletion | <100ms |
| Loss of contact >30 min | Automatic cryptographic erasure (configurable) | Immediate |
| Physical capture detected | Tamper switch → full zeroization | <100ms |

**Cryptographic erasure** is preferred over data overwrite — simply destroying the encryption key renders all encrypted data unrecoverable, and is instant.

### 7.5 Privacy Considerations

- **Camera footage:** May capture bystanders, license plates, private property
- **Minimization:** Record only during active mission phases; auto-delete non-evidentiary footage per policy
- **Blurring:** ML-based face/plate blurring for non-target individuals (post-processing at Nest)
- **Access control:** Only authorized personnel can access raw footage
- **Audit trail:** All footage access logged
- **Compliance:** Follow agency's privacy impact assessment (PIA) requirements

---

## 8. Operational Security

### 8.1 Operator Authentication

**Nest base station access:**

| Method | Implementation | Required For |
|--------|---------------|-------------|
| **Something you have** | YubiKey 5 NFC (FIDO2 + PIV) | All access |
| **Something you know** | PIN (6+ digits) | All access |
| **Something you are** | Fingerprint (optional, for high-security deployments) | Mission launch |

**Multi-factor requirement:** YubiKey + PIN minimum for all Nest operations.

**Session management:**
- Session timeout: 15 minutes of inactivity
- Maximum session: 12 hours
- Re-authentication required for: mission launch, OTA updates, configuration changes, emergency commands

### 8.2 Role-Based Access Control

| Role | Permissions |
|------|------------|
| **Operator** | Launch/land drones, monitor telemetry, basic mission control |
| **Mission Commander** | All operator + modify mission parameters, manual override, view video |
| **Administrator** | All commander + user management, configuration, OTA updates |
| **Maintenance** | Hardware diagnostics, firmware updates (with admin approval), physical access |
| **Auditor** | Read-only access to all logs and audit trails |
| **Emergency** | Break-glass access for safety-critical situations (all permissions, heavily logged) |

**Implementation:** RBAC enforced at Nest software level. Roles stored in signed configuration, not modifiable without Administrator + second Administrator approval (dual control).

### 8.3 Audit Logging

**What's logged:**
- All authentication attempts (success/failure)
- All mission operations (launch, land, waypoint changes, emergency commands)
- All configuration changes
- All data access (especially evidence/video)
- All security events (tamper alerts, anomaly detections, rogue drone alerts)
- All OTA update operations
- All key management operations

**Log security:**
- Logs signed with Nest key (tamper-evident)
- Forwarded to remote syslog server in real-time (when connected)
- Local log buffer survives power loss (battery-backed or flash-based)
- Log retention: 1 year minimum (CJIS requirement)

### 8.4 Incident Response

**Security incident categories:**

| Category | Examples | Response |
|----------|---------|----------|
| **SEV-1 CRITICAL** | Swarm compromise, rogue drone injected, mass GPS spoofing | Immediate RTB, ground all drones, notify CISO |
| **SEV-2 HIGH** | Single drone compromise suspected, persistent jamming, tamper alert | Isolate affected drone, continue mission with reduced swarm |
| **SEV-3 MEDIUM** | Authentication failure, anomaly score spike, intermittent jamming | Increase monitoring, log for analysis, alert operator |
| **SEV-4 LOW** | Failed login attempt, minor sensor discrepancy | Log only, periodic review |

**Automated responses:**
- GPS spoofing detected → automatic switch to alternative nav
- Rogue drone detected → automatic exclusion from swarm
- Tamper alert → automatic key zeroization
- All-band jamming → autonomous RTB

### 8.5 Security Monitoring

**Real-time dashboard on Nest:**
- Per-drone security status (green/yellow/red)
- Active anomaly scores
- Communication link health
- GPS integrity status
- Last attestation time
- Active alerts

---

## 9. Compliance & Standards

### 9.1 NIST Cybersecurity Framework (CSF 2.0) Mapping

| CSF Function | Hummingbird Implementation |
|-------------|---------------------------|
| **GOVERN** | This document; security policies; RBAC; training |
| **IDENTIFY** | Asset inventory (each drone); threat model (§1); data classification (§7.1) |
| **PROTECT** | Secure boot (§4.1); encryption (§3, §7); access control (§8.2); code signing (§4.2) |
| **DETECT** | Anomaly detection (§5.2, §5.6); GPS spoof detection (§6.2); runtime integrity (§4.6) |
| **RESPOND** | Incident response (§8.4); automated responses; operator alerts |
| **RECOVER** | A/B partition rollback; swarm self-healing; spare drone deployment |

### 9.2 FIPS 140-3

| Component | FIPS Status | Notes |
|-----------|-------------|-------|
| Doodle Labs Mesh Rider | **FIPS 140-3 Level 1 Validated** | Primary crypto for mesh |
| Jetson Orin NX | Not FIPS validated | Use FIPS-validated OpenSSL module (BoringCrypto or similar) |
| ATECC608B | FIPS 140-2 Level 2 (Microchip) | Check if FIPS 140-3 validation available at time of production |
| RFD900x | Not FIPS validated | Covered by application-layer FIPS-validated crypto |
| Software crypto (OpenSSL) | Use FIPS-validated module | OpenSSL 3.x FIPS provider or wolfSSL FIPS |

**Action item:** For government contracts requiring FIPS 140-3, ensure all cryptographic operations route through a FIPS-validated module. Doodle Labs covers link layer. Application layer needs FIPS-validated OpenSSL/wolfSSL.

### 9.3 CJIS Security Policy (v5.9.5)

**Relevant when drones access or capture Criminal Justice Information (CJI):**

| CJIS Requirement | Hummingbird Implementation |
|-----------------|---------------------------|
| **Advanced Authentication** (§5.6.2.2) | MFA with YubiKey + PIN |
| **Encryption** (§5.10.1.2) | AES-128 minimum (we use AES-128-GCM and AES-256) |
| **Encryption in Transit** (§5.10.1.2.1) | All links encrypted (§3) |
| **Encryption at Rest** (§5.10.1.2.2) | LUKS2 AES-256-XTS (§7.2) |
| **Audit Logging** (§5.4) | Comprehensive logging (§8.3) |
| **Access Control** (§5.5) | RBAC (§8.2) |
| **Personnel Security** | Background checks for operators (organizational policy) |
| **Physical Protection** | Tamper detection (§2.5), secure Nest facility |
| **Media Protection** | Encrypted storage, secure data destruction (§7.4) |
| **Incident Response** | IR procedures (§8.4) |

**Reference:** [FBI CJIS Security Policy v5.9.5](https://le.fbi.gov/cjis-division/cjis-security-policy-resource-center/cjis_security_policy_v5-9-5_20240709.pdf)

### 9.4 DO-326A / ED-202A (Airborne Cybersecurity)

**Applicability:** Not legally required for sUAS (Part 107), but following the framework demonstrates due diligence and prepares for future regulation.

**Key activities from DO-326A we implement:**

1. **Security Risk Assessment:** Threat model (§1) serves as basis
2. **Security Requirements:** Derived from threat model, documented in this architecture
3. **Security Development:** Secure coding practices, code signing, SAST/DAST
4. **Security Verification:** Penetration testing, fuzzing, security review
5. **Security Configuration Management:** Signed configurations, change control
6. **Security Assurance:** Attestation, audit trails, compliance evidence

**Reference:** [AFuzion DO-326A/ED-202A Overview](https://afuzion.com/do-326a-ed-202a-aviation-cyber-security/)

### 9.5 Additional Standards

| Standard | Relevance | Status |
|----------|-----------|--------|
| **CISA UAS Cybersecurity Best Practices** | Direct guidance for commercial UAS operators | Implemented throughout |
| **NIST SP 800-53 Rev 5** | Security controls (CJIS maps to these) | Mapped via CJIS |
| **Blue UAS Framework** | DoD-approved drone list compliance | Doodle Labs is Blue UAS; overall platform should pursue |
| **NDAA Section 889** | No prohibited components (Huawei, ZTE, etc.) | Verified — all components NDAA compliant |

**Reference:** [CISA Cybersecurity Best Practices for UAS](https://www.cisa.gov/sites/default/files/publications/CISA%20Cybersecurity%20Best%20Practices%20for%20Operating%20Commerical%20UAS%20(508).pdf)

---

## 10. Implementation Roadmap

### Phase 1: Prototype (P1) — Minimum Viable Security
**Timeline:** 8-12 weeks · **Effort:** ~2 FTE security engineer months

| Item | Description | Effort |
|------|------------|--------|
| Jetson Secure Boot | Enable RSA-3072 secure boot, burn OTP fuses | 1 week |
| LUKS2 Disk Encryption | Encrypt rootfs with KDK-derived key | 1 week |
| dm-verity | Read-only rootfs with integrity checking | 1 week |
| HBP AES-128-GCM | Implement encryption in swarm protocol | 2 weeks |
| Anti-replay | Sequence numbers + timestamps in HBP | 1 week |
| Doodle Labs AES-256 | Configure link-layer encryption | 1 day |
| RFD900x AES-128 | Enable hardware encryption | 1 day |
| GPS spoof detection (basic) | IMU/GPS cross-validation + C/N0 monitoring | 2 weeks |
| Basic PKI | Root CA + Nest CA + drone certificates (manual provisioning) | 1 week |
| Operator authentication | YubiKey + PIN for Nest access | 1 week |
| Audit logging | Basic structured logging | 1 week |
| Code signing | Sign PX4 firmware + Jetson packages | 1 week |
| C++ hardening flags | Compiler security flags enabled | 2 days |
| STM32 RDP Level 1 | Enable read-out protection (reversible for dev) | 1 day |

**P1 delivers:** Encrypted communications, secure boot, basic identity, GPS spoof detection, operator auth. Sufficient for controlled testing.

### Phase 2: Production (P2) — Full Security
**Timeline:** 16-24 weeks · **Effort:** ~6 FTE security engineer months

| Item | Description | Effort |
|------|------------|--------|
| ATECC608B integration | Hardware secure element, factory provisioning station | 4 weeks |
| Full PKI automation | Automated certificate lifecycle, CRL, OCSP | 3 weeks |
| SROS2 deployment | DDS security for non-critical topics | 2 weeks |
| Rogue drone detection | Behavioral analysis engine | 3 weeks |
| Byzantine fault tolerance | Cross-validation, voting protocol | 4 weeks |
| Secure flight leader election | Hardened election protocol | 2 weeks |
| OTA update system | Dual-signed, A/B partition, staged rollout | 4 weeks |
| IR authentication | Proximity verification protocol | 2 weeks |
| Remote wipe | Cryptographic erasure capability | 1 week |
| Evidence chain of custody | Signed hashes, immutable logs | 2 weeks |
| Visual odometry nav backup | VIO integration for GPS-denied operation | 3 weeks |
| RBAC system | Full role-based access control | 2 weeks |
| Security monitoring dashboard | Real-time security status | 2 weeks |
| Penetration testing | External red team engagement | 2 weeks |
| CJIS compliance audit | Gap analysis and remediation | 2 weeks |
| STM32 RDP Level 2 | Permanent read-out protection | 1 day |
| FPGA bitstream encryption | Enable AES-256 + ECC-256 | 1 week |
| Tamper detection hardware | Enclosure switches, integration | 2 weeks |
| IMA + kernel module signing | Runtime integrity | 1 week |
| Fuzzing campaign | AFL++ on all protocol parsers | 2 weeks (ongoing) |

**P2 delivers:** Production-grade security suitable for law enforcement deployment. CJIS compliant.

### Phase 3: Advanced / Future (P3)
**Timeline:** 6-18 months post-production · **Effort:** Variable

| Item | Description | Priority |
|------|------------|----------|
| Septentrio GPS upgrade | Anti-spoofing hardware receivers | High |
| RF fingerprinting | ML-based radio authentication | Medium |
| UWB ranging | Precise inter-drone distance for position validation | Medium |
| Post-quantum crypto | Hybrid ECDH + ML-KEM key exchange | Low (monitor NIST PQC timeline) |
| Conductive mesh tamper | PCB-level tamper detection | Low |
| Formal verification | Key protocol components formally verified | Low |
| FIPS 140-3 platform validation | Full platform (not just Doodle Labs) | Medium (if gov contracts require) |
| Blue UAS certification | DoD approved drone list | High (if DoD market) |
| AI anomaly detection | Deep learning for swarm behavior analysis | Medium |

### Cost Summary

| Phase | Hardware Cost (per drone) | Engineering Effort | Timeline |
|-------|--------------------------|-------------------|----------|
| **P1** | ~$0 (software/config only) | 2 FTE-months | 8-12 weeks |
| **P2** | ~$5-10 (ATECC608B + tamper switch) | 6 FTE-months | 16-24 weeks |
| **P3** | ~$200-300 (Septentrio + UWB) | Ongoing | 6-18 months |

---

## 11. References

### Standards & Frameworks
1. NIST Cybersecurity Framework 2.0 — https://www.nist.gov/cyberframework
2. NIST SP 800-53 Rev 5 — https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
3. FBI CJIS Security Policy v5.9.5 — https://le.fbi.gov/cjis-division/cjis-security-policy-resource-center/cjis_security_policy_v5-9-5_20240709.pdf
4. CISA UAS Cybersecurity Best Practices — https://www.cisa.gov/sites/default/files/publications/CISA%20Cybersecurity%20Best%20Practices%20for%20Operating%20Commerical%20UAS%20(508).pdf
5. CISA Drone Privacy and Data Protection — https://www.cisa.gov/sites/default/files/2023-01/FINAL_508%20Compliant_Secure%20Your%20Drone_Privacy%20and%20Data%20Protection%20Guidance_24JAN2023.pdf
6. DO-326A/ED-202A Airworthiness Security — https://afuzion.com/do-326a-ed-202a-aviation-cyber-security/

### Hardware Documentation
7. NVIDIA Jetson Secure Boot — https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/Security/SecureBoot.html
8. STM32 Security Application Note — https://www.st.com/resource/en/application_note/dm00493651-introduction-to-stm32-microcontrollers-security-stmicroelectronics.pdf
9. STM32 Secure Boot and Secure Firmware Update — https://wiki.st.com/stm32mcu/wiki/Security:Introduction_to_Secure_boot_and_Secure_firmware_update
10. Lattice CrossLink-NX-33 Data Sheet — https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6448/FPGADS0210410CrossLinkNX33andCrossLinkUNX.pdf
11. Doodle Labs Mesh Rider FIPS 140-3 — https://doodlelabs.com/news/how-doodle-labs-helix-mesh-rider-radio-achieves-blue-uas-compliance/
12. Doodle Labs OEM Specifications — https://doodlelabs.com/product/oem/
13. RFD900x SiK Firmware Manual — https://files.rfdesign.com.au/Files/documents/RFD900x%20Peer-to-peer%20V3.X%20User%20Manual%20V1.4.pdf
14. RidgeRun Jetson Secure Boot Guide — https://developer.ridgerun.com/wiki/index.php/RidgeRun_Platform_Security_Manual/Getting_Started/Secure_Boot/NVIDA-Jetson
15. RidgeRun Jetson TPM Guide — https://developer.ridgerun.com/wiki/index.php/RidgeRun_Platform_Security_Manual/Getting_Started/Trusted-Platform-Module/NVIDA-Jetson

### Research Papers
16. "Cybersecurity and AI in UAVs: Emerging Challenges" (IET 2025) — https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/ise2/2046868
17. "Reputation-Enhanced PBFT for UAV Node Capture Attacks" (2025) — https://www.researchgate.net/publication/392162174
18. "Dual-layer PBFT for UAV Swarm Management" (Springer 2025) — https://link.springer.com/chapter/10.1007/978-3-031-96944-7_19
19. "Survey on Security of UAV Swarm Networks" (ACM Computing Surveys 2025) — https://dl.acm.org/doi/10.1145/3703625
20. "Secure Communication Framework for Drone Swarms" (SCIRP 2024) — https://www.scirp.org/journal/paperinformation?paperid=137084
21. "Real-Time GPS Spoofing Detection via Multi-Sensor Fusion" (IEEE 2025) — https://ieeexplore.ieee.org/document/10964312/
22. "GPS Spoofing Detection Using Distributed Radar Tracking" (IEEE Sensors 2024) — https://ieee-sensorsalert.org/articles/gps-spoofing-detection-and-mitigation-for-drones-using-distributed-radar-tracking-and-fusion/
23. "GNSS Spoofing Detection via Doppler and C/N0" (ScienceDirect 2024) — https://www.sciencedirect.com/science/article/abs/pii/S1383762124001498
24. "Neutralization of IMU-Based GPS Spoofing Detection" (arXiv 2025) — https://arxiv.org/abs/2512.20964
25. "On the (In)Security of Secure ROS2" (CCS 2022) — https://tianweiz07.github.io/Papers/22-ccs-2.pdf
26. "SROS2: Usable Cyber Security Tools for ROS 2" (2022) — https://aliasrobotics.com/files/SROS2.pdf
27. "ROS2 DDS-Security Integration Design" — https://design.ros2.org/articles/ros2_dds_security.html
28. "SROS2 Multi-Robot Security" — https://osrf.github.io/ros2multirobotbook/security.html
29. "ROS2-Based UAV Cyberphysical Security Analysis" (arXiv 2024) — https://arxiv.org/html/2410.03971v1
30. "Towards Resilient UAV Swarms" (MDPI Drones 2022) — https://www.mdpi.com/2504-446X/6/11/340
31. "C2B-DroneNet: Blockchain for Drone Networks" (Springer 2025) — https://link.springer.com/article/10.1007/s10207-025-01149-2
32. "Revolutionizing Drone Swarm Reliability: PBFT in Action" (2024) — https://decentcybersecurity.eu/revolutionizing-drone-swarm-reliability-pbft-in-action/
33. "Cyber Threats in Drone Systems: Forensics and Legal Admissibility" (Frontiers 2025) — https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2025.1661928/full

---

> **Document Status:** Living document. Update as architecture evolves.
> **Next Review:** Upon completion of P1 implementation.
> **Owner:** Security Architecture Team
