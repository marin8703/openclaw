# Axon Fusus — Comprehensive Analysis for Hummingbird Technologies

**Date:** March 9, 2026  
**Prepared for:** Marin Walters, Hummingbird Technologies  
**Purpose:** Evaluate Axon Fusus for integration with Hummingbird Nest autonomous drone swarm platform

---

## Executive Summary — Key Takeaways for Marin

1. **Fusus is THE dominant RTCC platform** — 2,000+ agencies, acquired by Axon (Feb 2024), now deeply embedded in the Axon ecosystem (body cams, Evidence, TASER, Air, 911).

2. **Dearborn is already live** — As of Feb 2, 2026, Dearborn PD deployed FUSUS + Skydio DFR. They're the first in Michigan. This is our backyard and our reference customer.

3. **Integration is achievable** — Fusus has an open REST API (JSON over HTTPS with basic auth) that accepts video, sensor, and data feeds. No public SDK, but the API is documented for partners. Skydio's integration is cloud-to-cloud via API tokens — a model we can replicate.

4. **Video ingestion uses RTSP** — The FususCORE appliance connects to cameras via RTSP. Cloud integrations (like Skydio) push video and telemetry via API. We should support both paths.

5. **Strategic recommendation: Build a FUSUS-compatible output interface, not a dependency.** Offer agencies a toggle: "Stream to Fusus" as one of many output options from Hummingbird Nest. Don't make our architecture depend on Axon's ecosystem.

6. **Privacy/political risk is real** — EFF and ACLU actively campaign against Fusus. Dearborn specifically drew ACLU-Michigan scrutiny (May 2025) over protest surveillance concerns. We must have a clear privacy narrative.

7. **Competitive landscape** — Skydio DFR Command also pushes video to Motorola Command Aware, STRAX, Genetec, Milestone, and DroneSense. We should be platform-agnostic too.

---

## 1. What is Axon Fusus?

### Product Overview

Axon Fusus (formerly Fusus, stylized as fūsus) is a cloud-based **Real-Time Crime Center (RTCC) platform** that unifies live video, sensor data, and field intelligence into a single map-based operational view. It connects:

- Public and private camera systems (CCTV, body-worn, dash cams)
- Drone video feeds (Skydio, Axon Air)
- License plate readers (ALPR/LPR)
- Gunshot detection systems (ShotSpotter/SoundThinking, Shooter Detection Systems)
- CAD/RMS systems
- IoT devices and sensors
- Officer locations and alerts

The platform enables law enforcement, command staff, and RTCC analysts to see all data sources on one interactive map in real time.

**Source:** [Axon product page](https://www.axon.com/products/axon-fusus), [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-ba2wu4h5tdgu6)

### Product Components

| Component | Description |
|-----------|-------------|
| **FususONE** | Cloud-based web dashboard — the main interface. Map-based, browser-accessible. Unlimited seat licenses. |
| **FususCORE** | On-premise hardware appliance placed on a network. Auto-discovers and connects to all IP cameras via RTSP. Comes in Pro and Elite tiers. |
| **FususSYNC** | Cloud-based virtual CORE for cameras that can't accommodate physical hardware (WiFi, cellular cameras). |
| **FususAI** | AI analytics layer — weapon detection, vehicle identification, object search. Excludes facial recognition. |
| **Community Connect** | Opt-in program for residents/businesses to share private camera feeds with law enforcement. |
| **FususALERT** | Panic alerting with geolocation. |
| **FususVAULT** | CJIS-compliant evidence storage. |
| **FususOPS** | iOS/Android mobile app for field communication. |
| **FususNOTIFY** | SMS notification service for community alerts. |
| **FususTIPS** | SMS-based tip submission (photos, audio, video). |
| **FususREGISTRY** | Public-facing portal for registering privately-owned cameras. |

**Source:** [UK Digital Marketplace listing](https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/545079185812154), [Benchmark Magazine](https://benchmarkmagazine.com/fusus-fususone/)

### Acquisition by Axon

- **Acquired:** February 1, 2024
- **Terms:** Undisclosed
- **Prior relationship:** Strategic partnership since May 2022
- **Rationale:** Gave Axon RTCC capability it didn't have; extends Axon into retail, healthcare, private security, and federal sectors
- **Current branding:** "Axon Fusus" — now a core part of Axon's product suite alongside Evidence, Body Cameras, TASER, Air, and 911

**Source:** [Axon investor press release](https://investor.axon.com/2024-02-01-Axon-Accelerates-Real-Time-Operations-Solution-with-Strategic-Acquisition-of-Fusus), [Police1](https://www.police1.com/police-products/real-time-crime-centers/axon-acquires-real-time-crime-center-technology-developer-fusus)

### Adoption & Scale

- **2,000+ agencies** as of Axon's 2024 annual report (Feb 2025)
- **Millions of livestreams per year**
- **$1B+ in bookings** tied to newer products including Fusus (2025)
- **FedRAMP compliant** — package submitted, enabling federal adoption
- Deployed on **AWS GovCloud** with AES 256-bit encryption and TLS 1.3

**Source:** [Axon 2024 annual report](https://investor.axon.com/2025-02-25-Axon-2024-revenue-grows-33-to-2-1-billion-third-consecutive-year-of-30-annual-growth), [Axon Morgan Stanley conference 2026](https://aicommission.org/2026/03/axon-enterprise-flags-broad-2025-momentum-as-ai-bookings-hit-750m-at-morgan-stanley-conference/)

### Pricing Model

⚠️ **Unverified** — Fusus does not publicly disclose pricing. Based on available signals:
- SaaS subscription model (per-agency or per-site)
- FususCORE hardware is sold/leased per location
- FususONE includes unlimited seat licenses (no per-user charge)
- Community Connect (FususSYNC) appears to have a "low monthly price" for businesses
- Likely bundled into Axon's broader agency contracts (AI Era Plan, etc.)

---

## 2. Technical Architecture

### Deployment Model: Hybrid (On-Prem Edge + Cloud)

```
[Cameras/Sensors] --RTSP--> [FususCORE appliance (on-prem)]
                                    |
                              TLS 1.3 outbound
                                    |
                                    v
                          [AWS GovCloud - FususONE]
                                    |
                              Web browser
                                    v
                          [Operators / RTCC / Field]
```

- **FususCORE** sits on the local camera network. It auto-discovers IP cameras and ingests video via **RTSP**.
- CORE establishes an **outbound-only TLS 1.3 connection** to AWS GovCloud — no inbound ports needed.
- **FususONE** is the cloud dashboard, accessible via any web browser.
- Data encrypted **AES 256-bit** at rest, in transit, and in cloud.
- For cameras without on-prem CORE access, **FususSYNC** provides cloud-based virtual CORE.

**Source:** [Campbell CA FAQ](https://www.campbellca.gov/FAQ.aspx?QID=333), [Benchmark Magazine](https://benchmarkmagazine.com/fusus-fususone/), [Reddit r/911dispatchers](https://www.reddit.com/r/911dispatchers/comments/1g04inw/fusus_users/)

### Video Ingestion Protocols

| Protocol | Use Case |
|----------|----------|
| **RTSP** | Primary — FususCORE connects to IP cameras via RTSP streams. Verkada integration confirmed via RTSP. |
| **Cloud API** | For cloud-native integrations (e.g., Skydio). Video + telemetry pushed via HTTPS API. |
| **Webhooks** | For alert/event integrations (e.g., Verkada LPR sends webhook to `fusus-alarms.fususone.com`). |

⚠️ **Unverified:** Whether RTMP or WebRTC are supported. RTSP is the confirmed primary protocol.

### API

**Fusus provides REST API endpoints:**
- **Format:** JSON payload over HTTPS
- **Auth:** Basic authentication
- **Capabilities:** Accepts video, sensor, and data feeds
- **Endpoint example:** `fusus-alarms.fususone.com` (for webhook-based integrations like Verkada LPR)
- **No public API documentation** — API access appears to be provided to integration partners on request

The API is described as enabling "rapid and easy integration of different types of videos, sensor, and data feeds into the FususONE platform" and is "supported by any technical library that supports" standard HTTP.

**Source:** [UK Digital Marketplace](https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/545079185812154)

### Skydio-Fusus Integration (Reference Model for Hummingbird)

This is the most important reference for our integration approach:

1. **Cloud-to-cloud integration** — Skydio Cloud connects to FususONE via API tokens
2. **Setup process:**
   - Agency contacts Fusus support team for an integration token
   - Token is entered in Skydio Cloud settings
   - Agency copies a Skydio API personal access token into Fusus App Store configuration
3. **Data flow:** Skydio drone → Skydio Cloud → Fusus API → FususONE dashboard
4. **What gets pushed:** Live video stream + telemetry (GPS location, altitude, heading)
5. **The drone appears as a data source on the Fusus map** alongside body cams, fixed cameras, LPR, etc.
6. **Skydio also supports RTSP streaming** via their Live APIs for non-Fusus platforms
7. **Post-flight:** Media auto-uploads to Axon Evidence for chain-of-custody

**Key insight:** The Skydio integration is **not** via RTSP directly into a FususCORE. It's a **cloud API integration** where Skydio Cloud pushes data to FususONE. This is the model we should replicate.

**Source:** [Skydio support article](https://support.skydio.com/hc/en-us/articles/30195714152987-How-to-integrate-Skydio-Cloud-with-Fusus), [Skydio blog](https://www.skydio.com/blog/skydio-axon-fusus-integration-dfr-common-operating-procedures)

### Data Formats & Standards

⚠️ **Unverified** — No confirmed use of specific standards like CAP, NIEM, or Cursor on Target (CoT). The API accepts JSON payloads. Given Fusus's focus on being "technology agnostic" and their use of webhooks, it's likely proprietary JSON schemas rather than formal standards.

---

## 3. Integration Ecosystem

### Known Integrations

| Category | Integrated Systems |
|----------|--------------------|
| **Drones** | Skydio (DFR Command), Axon Air |
| **Body/Fleet Cameras** | Axon Body Cameras, various BWC vendors |
| **Fixed Cameras/VMS** | Verkada, Axis, Mobotix, virtually any RTSP-capable IP camera, most VMS platforms |
| **LPR/ALPR** | Verkada LPR, Flock Safety, Vaxtor (on Axis/Mobotix), other ALPR vendors |
| **Gunshot Detection** | SoundThinking (ShotSpotter), Shooter Detection Systems (SDS) |
| **CAD Systems** | Various CAD integrations (specific vendors vary by agency) |
| **Evidence Management** | Axon Evidence, Axon Records |
| **Mobile Surveillance** | LVT (LiveView Technologies) — integrated Aug 2024 |
| **Tracking** | TrackStar (Nashville PD confirmed) |
| **Axon Ecosystem** | Axon Respond, Axon 911 (first integration shipped Q4 2025), TASER alerts |

**Source:** [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-ba2wu4h5tdgu6), [Nashville FUSUS report](https://www.nashville.gov/sites/default/files/2024-11/NCRB-FUSUS-2024-Informational-Report-Update-RS2024-792-ADA.pdf), [LVT press release](https://www.lvt.com/press/lvt-integrates-axons-real-time-crime-center), [SDS integration matrix](https://shooterdetectionsystems.com/wp-content/uploads/sites/7/2024/01/SDS_Integrations_Matrix_2024_v2.0.pdf)

### Integration Partner Program

⚠️ **Partially verified** — Fusus has a concept of "certified integrations" referenced on their product page. There's a **Fusus App Store** within the FususONE platform where integrations can be configured (Skydio integration is set up through this). Job postings for "Implementation Engineer II, Fusus" and "Solutions Architect II, Fusus" at Axon describe working with a "Director of Integrations" to build, test, and deploy new integrations.

**To become a certified integration partner, Hummingbird would likely need to:**
1. Contact Axon's Fusus integrations team (possibly via `tenders@axon.com`)
2. Get API documentation and integration token
3. Build and test integration in a dev environment
4. Work with Fusus team to validate and certify
5. Get listed in the Fusus App Store

---

## 4. Competitive / Market Position

### RTCC Platform Comparison

| Platform | Owner | Strengths | Fusus Advantage |
|----------|-------|-----------|-----------------|
| **Axon Fusus** | Axon | 2,000+ agencies, deep Axon ecosystem, cloud-native, open API | Market leader, most integrations, Axon bundle deals |
| **Genetec Citigraf** | Genetec | Strong VMS heritage, enterprise video | More traditional VMS focus, less RTCC-specific |
| **Motorola Command Aware** | Motorola Solutions | CAD/radio integration, huge installed base | Strong in dispatch, but Fusus leads in video aggregation |
| **Milestone** | Milestone Systems | Open platform VMS, large camera support | More VMS than RTCC — different layer |
| **STRAX** | STRAX Intelligence | RTCC focused | Smaller market share |
| **DroneSense** | DroneSense | Drone-specific operations platform | Drone ops only, not full RTCC |

**Key fact:** Skydio DFR Command integrates with ALL of the above — Fusus, Motorola Command Aware, STRAX, DroneSense, Genetec, and Milestone. This confirms that being platform-agnostic is the right strategy.

**Source:** [Skydio DFR Command press release, Feb 2026](https://www.prnewswire.com/news-releases/skydio-dfr-command-surpasses-10-million-calls-for-service-making-it-the-most-integrated-drone-as-first-responder-system-in-the-world-302699005.html)

### Market Trajectory

- Axon 2024 revenue: **$2.1B** (+33% YoY)
- Q4 2025 revenue: **$797M** (+39% YoY)
- Fusus is a growth driver — part of $1B+ in "newer product" bookings
- Axon 911 + Fusus integration shipped Q4 2025 — deepening the moat
- FedRAMP compliance opens federal market

**Source:** [Axon investor relations](https://investor.axon.com/2025-02-25-Axon-2024-revenue-grows-33-to-2-1-billion-third-consecutive-year-of-30-annual-growth), [Axon Q4 2025 report](https://www.prnewswire.com/news-releases/axon-reports-q4-2025-revenue-of-797-million-up-39-year-over-year-302696190.html)

### Controversies & Privacy Concerns

**This is significant and Hummingbird must be aware:**

- **EFF (May 2023):** Published "Neighborhood Watch Out" — detailed investigation of how Fusus incorporates private cameras into police surveillance networks. Core concern: camera owners "opt in" but people being recorded don't consent. [Source](https://www.eff.org/deeplinks/2023/05/neighborhood-watch-out-cops-are-incorporating-private-cameras-their-real-time)

- **Reuters (May 2023):** "Privacy or safety? U.S. brings 'surveillance city to the suburbs'" — Minneapolis PD's Fusus program scrutinized. [Source](https://www.reuters.com/article/usa-tech-cities-idUSL8N35O0IE/)

- **ACLU-Michigan vs. Dearborn (May 2025):** ACLU raised concerns about Dearborn's Fusus deployment specifically, warning it could be used to monitor pro-Palestinian protesters. Attorney Ramis Wadood called it "really concerning." [Source](https://www.clickondetroit.com/news/local/2025/05/27/dearborn-greenlights-real-time-camera-network-amid-aclu-privacy-concerns/)

- **EFF vs. Nashville (March 2025):** EFF and Lucy Parsons Labs opposed Nashville's Fusus deployment, arguing "guardrails" are insufficient. [Source](https://www.eff.org/deeplinks/2025/03/guardrails-wont-protect-nashville-residents-against-ai-enabled-camera-networks)

- **San Francisco lawsuit:** EFF and ACLU-NorCal filed Williams v. San Francisco over real-time surveillance technology ordinance violations.

**⚠️ Dearborn is a politically sensitive market** due to its large Arab-American population and active protest culture. Our integration with FUSUS in Dearborn will be scrutinized.

---

## 5. Hummingbird Integration Opportunities

### What Data Can Hummingbird Feed Into Fusus?

| Data Type | Fusus Compatibility | Priority |
|-----------|-------------------|----------|
| **Live drone video streams** | ✅ Confirmed — Skydio does this | P0 — Minimum viable |
| **GPS position / telemetry** | ✅ Confirmed — drone appears on Fusus map | P0 — Minimum viable |
| **AI detections (person, vehicle, weapon)** | ✅ Likely — Fusus accepts sensor/alert data via API | P1 |
| **Multi-drone swarm overview** | ⚠️ Novel — Fusus shows individual sources, swarm view would be new | P2 |
| **Sensor data (thermal, LIDAR, air quality)** | ✅ Fusus accepts IoT/sensor data | P2 |
| **Automated alerts** | ✅ Webhook/API alert ingestion confirmed | P1 |

### Recommended Integration Architecture

```
[Hummingbird Nest Platform]
        |
        |--- RTSP output -----> [FususCORE] (for agencies with on-prem CORE)
        |
        |--- REST API (JSON/HTTPS) --> [FususONE Cloud] (cloud-to-cloud, like Skydio)
        |
        |--- RTSP output -----> [Genetec / Milestone / etc.] (platform-agnostic)
        |
        |--- RTMP/WebRTC -----> [Any web viewer] (direct access)
```

### Minimum Viable Integration (MVI)

Based on the Skydio reference model:

1. **Hummingbird Nest Cloud → Fusus API** — push live video stream + GPS coordinates
2. Each active drone appears as a **positioned data source on the Fusus map**
3. Video is viewable in FususONE alongside all other agency feeds
4. **Authentication:** API token exchange (Hummingbird token in Fusus App Store, Fusus token in Nest)
5. **Estimated effort:** 2-4 weeks engineering to implement the API integration, assuming we get API docs from Axon

### Interface/Protocol We Need to Implement

1. **REST API client** — POST JSON payloads to Fusus endpoints over HTTPS with basic auth
2. **Video streaming** — Either push via API (cloud) or expose RTSP endpoint (on-prem CORE)
3. **Telemetry format** — JSON with GPS coordinates, altitude, heading, drone ID, timestamp
4. **Alert/event format** — JSON webhook payable to Fusus alarm endpoints
5. **App Store listing** — Configuration page for token exchange

---

## 6. Strategic Considerations

### Pros of Fusus Integration

| Benefit | Detail |
|---------|--------|
| **Instant market access** | 2,000+ agencies already on Fusus — integration makes us immediately compatible |
| **Dearborn reference** | Our target market already runs Fusus — integration is table stakes |
| **Proven model** | Skydio's integration proves the path — we're not pioneering anything |
| **Axon relationship** | Being in the Fusus App Store gives us visibility in Axon's sales channel |
| **Low engineering cost** | REST API + JSON — standard web integration, not exotic protocols |

### Risks & Cons

| Risk | Detail | Mitigation |
|------|--------|------------|
| **Axon ecosystem lock-in** | Axon owns Fusus AND has deep Skydio integration. They could favor Skydio over us. | Build Fusus as ONE output option, not a dependency. Support Genetec, Milestone, Motorola too. |
| **Competitive conflict** | Axon could view our swarm platform as competing with their Axon Air / Skydio partnership. | Position as complementary (swarm ≠ single DFR). Focus on capabilities they can't offer. |
| **Privacy backlash** | Being integrated with Fusus associates us with surveillance concerns. Dearborn is politically sensitive. | Build privacy-first features: audit trails, data retention limits, transparency dashboards. |
| **API dependency** | Fusus API is not publicly documented. They control access and could change terms. | Implement as a thin adapter layer. Core Nest platform must function without Fusus. |
| **No public SDK** | Integration requires working with Fusus team directly. Could slow us down. | Start outreach to Axon Fusus integrations team early. |

### Recommended Approach

**"FUSUS-compatible, not FUSUS-dependent"**

1. **Build a generic RTCC output interface** in Hummingbird Nest that can push video + telemetry + alerts to any RTCC
2. **Implement Fusus adapter first** (because Dearborn) — thin layer that formats our data for Fusus's API
3. **Also implement** Genetec, Milestone, and RTSP generic output
4. **Market positioning:** "Works with your existing RTCC" — don't lead with Fusus specifically
5. **Engage Axon's Fusus integration team** to get API docs and begin certification process
6. **Build privacy features** into our platform proactively — transparency dashboard, audit logs, data retention policies

### Next Steps

1. **Contact Axon Fusus integrations team** — request API documentation and integration partnership discussion
2. **Study Skydio's RTSP Live API** as a reference for our own streaming architecture
3. **Design Hummingbird Nest's RTCC output interface** as a pluggable adapter pattern
4. **Begin Fusus MVI development** once API docs are obtained
5. **Prepare privacy/civil liberties narrative** for Dearborn deployment

---

## Sources Index

| # | Source | URL |
|---|--------|-----|
| 1 | Axon acquisition press release | https://investor.axon.com/2024-02-01-Axon-Accelerates-Real-Time-Operations-Solution-with-Strategic-Acquisition-of-Fusus |
| 2 | Axon Fusus product page | https://www.axon.com/products/axon-fusus |
| 3 | AWS Marketplace listing | https://aws.amazon.com/marketplace/pp/prodview-ba2wu4h5tdgu6 |
| 4 | UK Digital Marketplace (API details) | https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/services/545079185812154 |
| 5 | Skydio-Fusus integration blog | https://www.skydio.com/blog/skydio-axon-fusus-integration-dfr-common-operating-procedures |
| 6 | Skydio-Fusus setup guide | https://support.skydio.com/hc/en-us/articles/30195714152987-How-to-integrate-Skydio-Cloud-with-Fusus |
| 7 | Skydio DFR Command 10M calls PR | https://www.prnewswire.com/news-releases/skydio-dfr-command-surpasses-10-million-calls-for-service-making-it-the-most-integrated-drone-as-first-responder-system-in-the-world-302699005.html |
| 8 | Axon 2024 annual report | https://investor.axon.com/2025-02-25-Axon-2024-revenue-grows-33-to-2-1-billion-third-consecutive-year-of-30-annual-growth |
| 9 | Axon Q4 2025 earnings | https://www.prnewswire.com/news-releases/axon-reports-q4-2025-revenue-of-797-million-up-39-year-over-year-302696190.html |
| 10 | EFF Fusus investigation | https://www.eff.org/deeplinks/2023/05/neighborhood-watch-out-cops-are-incorporating-private-cameras-their-real-time |
| 11 | ACLU-Michigan Dearborn concerns | https://www.clickondetroit.com/news/local/2025/05/27/dearborn-greenlights-real-time-camera-network-amid-aclu-privacy-concerns/ |
| 12 | Dearborn DFR/FUSUS launch | https://dearborn.gov/dearborn-first-state-deploy-drone-first-responder-program-boost-response |
| 13 | Dearborn WXYZ coverage | https://www.wxyz.com/news/region/wayne-county/dearborn-police-launch-first-of-its-kind-real-time-crime-fighting-system-with-drones-and-integrated-cameras |
| 14 | Verkada-Fusus RTSP setup | https://help.verkada.com/en/articles/10279825-set-up-the-verkada-fusus-camera-integration |
| 15 | Verkada-Fusus LPR webhook | https://help.verkada.com/en/articles/9966767-set-up-the-verkada-fusus-lpr-integration |
| 16 | Nashville FUSUS report | https://www.nashville.gov/sites/default/files/2024-11/NCRB-FUSUS-2024-Informational-Report-Update-RS2024-792-ADA.pdf |
| 17 | Campbell CA FAQ (encryption) | https://www.campbellca.gov/FAQ.aspx?QID=333 |
| 18 | LVT-Fusus integration | https://www.lvt.com/press/lvt-integrates-axons-real-time-crime-center |
| 19 | SDS-Fusus integration matrix | https://shooterdetectionsystems.com/wp-content/uploads/sites/7/2024/01/SDS_Integrations_Matrix_2024_v2.0.pdf |
| 20 | Benchmark Magazine FUSUS article | https://benchmarkmagazine.com/fusus-fususone/ |
| 21 | Reddit r/911dispatchers Fusus thread | https://www.reddit.com/r/911dispatchers/comments/1g04inw/fusus_users/ |
| 22 | Skydio integrations catalog — Fusus | https://www.skydio.com/integrations-catalog/axon-fusus |
| 23 | EFF Nashville/Fusus (March 2025) | https://www.eff.org/deeplinks/2025/03/guardrails-wont-protect-nashville-residents-against-ai-enabled-camera-networks |
| 24 | Axon Morgan Stanley conference 2026 | https://aicommission.org/2026/03/axon-enterprise-flags-broad-2025-momentum-as-ai-bookings-hit-750m-at-morgan-stanley-conference/ |
| 25 | MLive Dearborn drones (March 2026) | https://www.mlive.com/news/detroit/2026/03/dearborn-sterling-heights-police-turn-to-drones-to-reach-emergency-scenes-faster.html |
