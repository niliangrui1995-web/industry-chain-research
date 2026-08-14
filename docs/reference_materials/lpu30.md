# LPU30 — Platform Overview

**Platform:** LPU30 (LP30 system generation — rack-scale LPU v3 platform)
**Source:** LP30 System Architecture / Manageability Overview slides + LP30 LPU Module Management diagram + LPU30-OOB screenshots (Secure FW Update / OOB Telemetry / NUDDs / Security Overview) + platform owner comprehensive interface list (2026-05-21)
**Last updated:** 2026-05-21

> All content in this document is sourced directly from platform owners. Do not infer, extrapolate, or carry over details from other platforms. If a detail is not listed here, it is unknown. The document is scoped to **OOB management architecture, devices, and protocols** — the high-bandwidth datapath (LPU C2C fabric, FPGA-to-LPU interconnect, OSFP optics) is not the focus and is summarized only where it intersects manageability.

---

## 1. Rack Composition

| Item | Count / Value |
| --- | --- |
| Form factor | 48RU rack |
| LPUs per rack | 256× LPU |
| Compute trays per rack | 16× |
| LPU modules per compute tray | 8× modules (2 LPUs per module → 16 LPUs per tray) |
| FPGA boards per compute tray | 2× (1 Altera Agilex 7 M-series per board) |
| HPM (host CPU) per compute tray | 1× Intel Granite Rapids 1S |
| DPU per compute tray | 1× BlueField-4 (BF-4) — North/South NIC; **optional** (own BMC, reachable via USB.NET → Redfish) |
| IO-Board (CX-9) per compute tray | 1× (always present); has its own SMA bridge; manages NVMe + provides CX-9 management |
| OSFP per compute tray | 10× (LPU C2C inter-rack optics + FPGA Ethernet) |
| Management module per compute tray | 1× SMM (carries BMC, optional HMC, EROTs, MCU, CPLD) |
| DCSCM (Data Center Secure Control Module) | 1× per tray; houses BMC + BMC-side ERoT |
| Baseboard | P4223 (implements PDB power control via HSCs and HSCCs; carries CP2112 USB-to-GPIO controller) |
| Management module connector | P4105 → HPM (USB-first reduced 28-pin + MCIO optional PCIe) |
| LPU C2C fabric per LPU | 96× 100G full-duplex lanes; 2.4 TB/s per-LPU C2C bandwidth |
| Mass storage on tray | None on data path; 1× E1.S boot drive only; 1× boot NVMe SSD managed via NVMe-MI |
| Commercial model | Appliance — NVIDIA-provided tray/system software, defined external APIs, no operator shell access |

---

## 2. Compute Tray

### 2.1 Service Architecture

- **BMC** is the **Service Root** for all OOB management services exposed externally over Redfish — Telemetry & RAS, FW Update, Attestation, Recovery, Debug, Leak Detect, Remote Power Control.
- **HMC** is **optional** in LP30 — ASPEED AST2600-based, running OpenBMC. Role: **abstracts NVIDIA complexity from the partner BMC**. **No external network access.** Sits on the internal management plane between BMC and the LPU / FPGA management fan-out. When present, HMC handles NVIDIA-specific protocols / paths so the partner BMC only sees standardized Redfish.
- Partner BMCs talk Redfish to the LP30 BMC; the BMC (with HMC as the internal abstraction layer when present) drives the device-side OOB management.

### 2.2 Component Inventory

> **Naming note:** the LP30 management slides use both **MCU** (device class) and **SMA** (role label, e.g. SMA-M, SMA-M1, SMA-C, SMA-MB) for the same hardware. This document uses **MCU-* as primary nomenclature**; treat `MCU-M ≡ SMA-M`, `MCU-M1 ≡ SMA-M1`, `MCU-C ≡ SMA-C`, `MCU-MB ≡ SMA-MB` throughout.

| Component | Device | Vendor | Count / Tray | Notes |
| --- | --- | --- | --- | --- |
| LPU module | LPU (v3) | NVIDIA | 8× modules × 2 LPUs each | 2 LPUs + 2 MCUs (MCU-M + MCU-C) + supporting parts per module. Detailed in §3. |
| FPGA board | Altera Agilex 7 M-series | Intel/Altera | 2× | 1 FPGA + 1 MCU-M1 per board. Hosts OSFP for LPU C2C + FPGA Ethernet. Detailed in §4. |
| HPM (host CPU) | Granite Rapids 1S | Intel | 1× | x86 host; reached by BMC via multiple interfaces (eSPI / PECI / I3C / USB-via-MCU / PCIe / UART / SGPIO / JTAG / SSIF) |
| DPU / N/S NIC | BlueField-4 | NVIDIA | 1× (optional) | N/S NIC; PCIe to HPM; managed by BMC via USB.NET → BF4 BMC → Redfish; only present when configured |
| CX-9 / IO-Board | — | NVIDIA | 1× | Always present on tray; has IO-Board SMA bridge; BMC reaches CX-9 via SMA → I3C and NVMe via SMA → I2C |
| BMC | — | — | 1× | On DCSCM block; Service Root for Redfish; manages host side and orchestrates all FW updates; peers with HMC over USB |
| HMC (optional) | ASPEED AST2600 | Aspeed | 0× or 1× | Runs OpenBMC; no external network; partner-BMC abstraction layer; manages LPU / FPGA via USB → SMA fan-out |
| MCU-M (≡ SMA-M) | NXP MCXNV556 | NXP | 8× (one per LPU module) | LPU management; vRoT for both LPUs on the module; multi-bus interface to LPU (I3C primary + I2C fallback + SPI for FW + GPIO) |
| MCU-M1 (≡ SMA-M1) | MCU | — | 2× (one per FPGA board) | FPGA management; vRoT for FPGA; USB↔HMC; I3C → FPGA; SPI → FPGA flash |
| MCU-C (≡ SMA-C) | NXP MCXNV556 | NXP | 8× (one per LPU module) | **Control-plane only** (not management); USB↔Host CPU; SPI↔LPU; receives reset/recovery from MCU-M |
| MCU-MB (≡ SMA-MB) | — | — | 1× | HPM-side MCU; BMC↔MCU-MB over USB; bridges BMC to host CPU (CPU UART, CPU QSPI flash) and ERoT (PLDM/MCTP/SPI to BMC ERoT, MCTP/SPI to Host CPU ERoT) |
| IO-Board SMA | — | — | 1× | On CX-9 IO board; BMC↔IO-Board SMA over USB; bridges to CX-9 via I3C, to NVMe via I2C |
| EROT (HMC-side) | — | — | 1× (when HMC present) | IRoT anchor for HMC chain only; not a comm channel |
| EROT (BMC-side) | — | — | 1× | On DCSCM; IRoT anchor for BMC + x86 chain only; not a comm channel |
| Host CPU EROT | — | — | 1× | Anchors x86 host CPU FW chain; reached by BMC via MCU-MB → MCTP/SPI |
| CPLD | — | — | 1× | On HPM block; reached by BMC via vROT → I2C (FW update) and via MCU-MB virtual-I2C (runtime GPIO/CPLD access via CP2112 emulation) |
| CP2112 | USB-to-GPIO controller | Silicon Labs (TBD exact part) | 1× | On P4223 baseboard; breaks out discrete GPIO sidebands from HMC USB to LPU modules (reset / power-good / presence) |
| TPM | — | — | 1× | SPI interface from BMC |
| Boot NVMe SSD | NVMe | — | 1× | Managed via NVMe-MI over SMBus / MCTP (BMC → I2C → SSD) |
| Boot drive | E1.S | — | 1× | HPM boot drive |
| Front IO | — | — | 1× | GPIO from BMC for buttons / LEDs |
| Tray USB HUBs | — | — | — | Fan out USB between BMC, HMC, and the LPU / FPGA / IO-Board SMAs |

### 2.3 System Management Module (SMM) and DCSCM

- The **SMM** consolidates BMC, optional HMC, both EROTs (BMC-side and HMC-side when HMC is present), MCU-MB, CPLD, and the link out to BF-4.
- **DCSCM** = Data Center Secure Control Module — houses BMC + BMC-side ERoT as a secure subsystem. Provides the immutable secure-boot / FW-update / recovery / attestation anchor for the BMC chain.
- The **P4223 baseboard** is separate hardware from the SMM — it carries the PDB power-control infrastructure (HSCs, HSCCs) plus the CP2112 USB-to-GPIO controller that exposes per-LPU sideband GPIOs from HMC's USB pathway.

---

## 3. LPU Module

Each compute tray carries **8× LPU modules**. Two LPUs per module, with shared management infrastructure.

### 3.1 LPU Module Inventory

| Component | Device | Count / Module | Notes |
| --- | --- | --- | --- |
| LPU ASIC | LPU v3 | 2× | Two LPUs per module. **Not MCTP endpoints** (no EID, no direct NSM) |
| MCU-M (LPU management) | NXP MCXNV556 | 1× | vRoT for both LPUs on the module; owns LPU FW flash; multi-bus interface (see §3.2) |
| MCU-C (LPU control plane) | NXP MCXNV556 | 1× | USB↔Host CPU, SPI↔LPU; control-plane only — **not a management bridge** |
| SPI Flash | — | 1× | LPU firmware; routed through a MUX so MCU-M can program it |
| MUX | — | 1× | Routes SPI Flash between MCU-M (FW programming) and LPU runtime access |
| FRU EEPROM | — | 1× | Inventory data (I2C from MCU-M) |
| CLK GEN | — | 1× | Clock generation |
| Temp Sensor | — | 1× | Thermal telemetry (I2C, TMP452-class) — also reachable directly by MCU-M for sensor-read fallback |
| PWR SEQ | — | 1× | Power sequencing controller |
| Voltage Regulators | HSCC VR, VDDL VR, Core/C2C VR, VDDM VR, VDDH VR | 5× rails | I2C-controlled by MCU-M; enable lines (EN) per rail |

### 3.2 LPU Module Interfaces — Multi-Bus

The LPU's primary management bus is **I3C**, but multiple physical buses connect MCU-M to LPU concurrently, each carrying a specific class of traffic:

| Bus | Traffic class | Protocol |
| --- | --- | --- |
| **I3C** | Primary management — telemetry, attestation, MCTP bridging, EID management | MCTP / NSM / PLDM T2 |
| **SPI** | Firmware update path — secure boot, write protection, background copy | PLDM T5 over ERoT |
| **I2C** (TMP452-class) | Direct temperature sensor read (fallback path) | Raw I2C |
| **I2C** (CP2112 virtual over USB) | OCP Recovery — LPU recovery stage 1 I2C forwarding | OCP Recovery |
| **GPIO** | Reset control, IRoT error detection, recovery triggering | Signal only |

**Management entry (HMC → MCU-M):**

- `From HMC` USB1.1 → MCU-M USB2 port — primary management entry.
- `From I2C IOX` (the CP2112 GPIO breakout on the P4223 baseboard) → MCU-M reset/power signals (`RST_B`, `P0_6`).
- MCU-M supplementary lines to LPU: `USB1.1`, `GPIO` (boot status / boot complete), `UART`, `AHB`, `ISO` (isolation).
- MCU-M → LPU reset / recovery: `MCU_C_RST_L`, `MCU_C_RECOV` (also gate MCU-C — see §3.4).
- MCU-M → SPI Flash via MUX → LPU firmware programming path.
- MCU-M → on-module I2C devices: FRU EEPROM, Temp Sensor, VR monitoring (HSCC, VDDL, Core/C2C, VDDM, VDDH) with GPIO `EN` lines per VR rail.

**Control-plane entry (Host CPU → MCU-C):**

- `From Host CPU` USB1.1 → MCU-C USB2 port — control-plane entry (not management).
- MCU-C ↔ LPU buses: `USB1.1`, `I2C`, `RST_B`, `P0_6`, `SPI`, `SPI_RDY` (with level shifters).
- MCU-C is exclusively a USB→SPI bridge on the LPU control plane for the host CPU — OOB management traffic never traverses MCU-C.
- Host CPU reaches MCU-C via a **PCIe-to-USB controller** on the HPM block.

**External debug:**

- `JTAG (RISC-V)` header — for MCU debug.
- `JTAG (ASIC)` header — for LPU ASIC debug.
- `GLOBAL_WP` — write-protect signal feeding the I2C side of the module.

### 3.3 LPU is Not an MCTP Endpoint

The LPU ASIC does not implement MCTP, has no EID, and does not accept NSM commands directly. All OOB management visibility into the LPU is provided by **MCU-M** acting as the bridge between HMC's USB management pathway and the LPU's internal I3C / SPI / GPIO / UART surfaces. The MCTP / PLDM messages that flow from HMC over USB terminate at MCU-M; MCU-M translates them to local-bus operations on the LPU.

### 3.4 MCU-M Owns MCU-C Reset and Recovery

A notable hierarchy: MCU-M can reset MCU-C and trigger MCU-C recovery via the `MCU_C_RST_L` and `MCU_C_RECOV` signals. The management chain (HMC → MCU-M) has hardware authority over the control-plane chain at the module level — if the control-plane MCU misbehaves, MCU-M (and through it, HMC) can recover it without operator intervention.

---

## 4. FPGA Board

Each compute tray carries **2× FPGA boards**.

| Item | Value |
| --- | --- |
| FPGA | 1× Altera Agilex 7 M-series |
| MCU-M1 (FPGA management) | 1× — vRoT for FPGA; USB↔HMC; I3C↔FPGA (telemetry/MCTP); SPI↔FPGA flash (FW update) |
| OSFP cages | Hosts LPU C2C inter-rack optics + FPGA Ethernet (10× OSFP per tray across the 2 boards) |

**OSFP management** is routed through the FPGA, which means both the **Host CPU** (in-band) and the **HMC** (OOB, via MCU-M1 → I3C → FPGA → OSFP) can access OSFP telemetry and control. The FPGA is not an MCTP endpoint — managed exclusively via MCU-M1.

---

## 5. Management Architecture

### 5.1 Service Architecture and Ownership

External: partner BMCs / operators see a Redfish surface anchored on the LP30 BMC.

Internal management plane (BMC owns most paths; optional HMC abstracts NVIDIA-specific traffic from the partner BMC when present):

| Manager | Devices Managed | Primary Transport |
| --- | --- | --- |
| **BMC** | HPM (x86 host CPU) | eSPI / PECI / I3C / USB (via MCU-MB) / PCIe / UART / SGPIO / JTAG / SSIF |
| BMC | BF-4 (when present) | USB.NET → BF4 BMC → Redfish |
| BMC | CX-9 / IO-Board | USB → IO-Board SMA → I3C |
| BMC | NVMe boot SSD | USB → IO-Board SMA → I2C; or NVMe-MI over SMBus/MCTP |
| BMC | CPLD | USB → MCU-MB → I2C-virtual (runtime); USB → vROT → I2C (FW update) |
| BMC | TPM | SPI |
| BMC | Front IO (buttons, LEDs) | GPIO |
| BMC | PDB (HSCs, fan controller, VR/ADC, temp sensors) | I2C |
| BMC | BMC ERoT | MCTP/SPI |
| BMC | Host CPU ERoT | USB → MCU-MB → MCTP/SPI |
| BMC | All FW update orchestration | See §5.4 FW Update Path Table |
| **BMC ↔ HMC** | Internal peer (when HMC present) | USB (CDC/USBnet, Redfish over USB Ethernet gadget + MCTP-over-USB); I2C (virtual EEPROM/FRU, MCTP/I2C to ERoT); SPI (PLDM T5 over MCTP/SPI via ERoT); GPIO (reset/recovery/presence) |
| **HMC** (when present) | LPU modules (8× modules × 2 LPUs) | USB → tray HUB → MCU-M on each module → I3C/SPI/I2C/GPIO to LPU |
| HMC | FPGA boards (2×) | USB → tray HUB → MCU-M1 → I3C/SPI to FPGA |
| HMC | OSFP (via FPGA) | Same path as FPGA, reaches OSFP through FPGA management surface |
| HMC | LPU ERoT chain | MCTP via MCU/SMA bridges (SPDM over MCTP for attestation, secure key exchange) |
| HMC | x86 / LPU IRoT | NSM Type 6 for FW update, attestation, DOT |
| HMC | LPU streaming boot, USBRCM, CSWP, POST code read | USB |
| **Host CPU (control plane, NOT management)** | LPU (control plane only) | USB → PCIe-to-USB controller → MCU-C on each LPU module → SPI to LPU |

### 5.2 Management Topology Diagram

```
                       External Operator / Partner BMC
                              |
                              | Redfish over HTTPS
                              v
+------------------------ Compute Tray (per tray) -----------------------+
|                                                                        |
|   +--------+ (DCSCM)                          +--------+ (optional)    |
|   |EROT-BMC|                                  |EROT-HMC|               |
|   +---+----+                                  +---+----+               |
|       |                                           |                    |
|       v       USB (PLDM/MCTP/USB, via tray HUB)   v                    |
|   +-------+----------------------------------+--------+                |
|   |  BMC  |---- USB CDC/USBnet + I2C + SPI --|  HMC   |                |
|   +--+----+                                  +---+----+                |
|      |                                           |                     |
|      | (host-side fan-out, see §5.1)             | USB                 |
|      v                                           v                     |
|  HPM block:                              +-----------------+           |
|    x86 (Granite Rapids)                  | Tray HMC-side   |           |
|    BF-4 (optional)                       | USB HUB         |           |
|    CPLD                                  +-+-----------+---+           |
|    MCU-MB (USB↔SPI/UART/I2C/SPI ERoT)      |           |               |
|    Host CPU ERoT                           |           |               |
|    TPM                                     |           |               |
|    Front IO                                |           |               |
|    PDB (via I2C)                           |           |               |
|                                            |           |               |
|                                            |           |               |
|                                       x8   |           |   x2          |
|                                  +---------v----+   +--v-----+         |
|                                  | LPU Module    |  |FPGA    |         |
|                                  | (2 LPUs each) |  |Board   |         |
|                                  |               |  |        |         |
|                                  | MCU-M         |  | MCU-M1 |         |
|                                  | (vRoT,        |  | (vRoT) |         |
|                                  |  SMA-M)       |  |        |         |
|                                  |  | I3C        |  |  | I3C |         |
|                                  |  | SPI        |  |  | SPI |         |
|                                  |  | I2C        |  |  v     |         |
|                                  |  | GPIO       |  |+----+  |         |
|                                  |  v            |  ||FPGA|--+--> OSFP |
|                                  | +----+ +----+ |  |+----+  |   x10   |
|                                  | |LPU | |LPU | |  +--------+         |
|                                  | +----+ +----+ |                     |
|                                  +---------------+                     |
|                                                                        |
|   BMC ↔ CX-9 / NVMe via IO-Board SMA:                                 |
|       BMC → USB → IO-Board SMA → I3C → CX-9                            |
|       BMC → USB → IO-Board SMA → I2C → NVMe                            |
|                                                                        |
|   Sideband GPIO path:                                                  |
|       HMC USB → CP2112 (on P4223 baseboard) → per-LPU reset / PG /    |
|                   presence GPIOs into each module's MCU-M             |
|                                                                        |
|   Control-plane path (in-band, not OOB):                              |
|       Host CPU USB → PCIe-to-USB controller → MCU-C per LPU module    |
|                                                                        |
+------------------------------------------------------------------------+

  Labels: MCU-M ≡ SMA-M, MCU-M1 ≡ SMA-M1, MCU-C ≡ SMA-C, MCU-MB ≡ SMA-MB
  EROT-BMC and EROT-HMC are independent IRoT anchors (not interconnected).
```

### 5.3 Endpoint Scale (per rack)

| Device | Path | Endpoints / Tray | Endpoints / Rack (16 trays) |
| --- | --- | --- | --- |
| LPU | HMC → tray HUB → MCU-M → I3C → LPU (2 LPUs per module) | 16 LPUs (8 modules × 2) | 256 LPUs |
| LPU module | HMC → tray HUB → MCU-M | 8 modules | 128 modules |
| FPGA | HMC → tray HUB → MCU-M1 → I3C → FPGA | 2 | 32 |
| OSFP | HMC → MCU-M1 → FPGA → OSFP | 10 | 160 |
| HPM (x86) | BMC → multi-bus (see §5.1) | 1 | 16 |
| BF-4 DPU | BMC → USB.NET → BF4 BMC → Redfish (when present) | 0 or 1 | 0–16 |
| CX-9 / IO-Board | BMC → USB → IO-Board SMA → I3C | 1 | 16 |
| NVMe boot SSD | BMC → USB → IO-Board SMA → I2C (or NVMe-MI) | 1 | 16 |
| HMC | BMC ↔ HMC USB peer link (when present) | 0 or 1 | 0–16 |
| CPLD | BMC → MCU-MB → I2C-virtual / vROT | 1 | 16 |

### 5.4 FW Update Path Table

All FW updates orchestrated by the **BMC**, unified protocol is **PLDM** (Type 5 for FW update).

| Target | Updater | Path | Protocol |
| --- | --- | --- | --- |
| LPU | BMC | BMC → MCTPoUSB → SMA(M) → vROT → LPU SPI | PLDM |
| FPGA (baseline bitstream) | BMC | BMC → MCTPoUSB → SMA(M1) → vROT → FPGA SPI | PLDM |
| LPU – SMA(C) | BMC | BMC → MCTPoUSB → SMA(M) → MCTPoI2C → SMA(C) | PLDM |
| LPU – SMA(M) | BMC | BMC → MCTPoUSB → SMA(M) | PLDM |
| FPGA – SMA(M1) | BMC | BMC → MCTPoUSB → SMA(M1) | PLDM |
| HPM – SMA(MB) | BMC | BMC → MCTPoUSB → SMA(MB) | PLDM |
| Host CPU (BIOS boot flash) | BMC | BMC → MCTPoUSB → SMA(MB) → MCTPoSPI → EROT → SPI | PLDM |
| Host CPU ERoT | BMC | BMC → MCTPoUSB → SMA(MB) → MCTPoSPI → EROT | PLDM |
| HPM CPLD | BMC | BMC → MCTPoUSB → vROT → I2C → CPLD | PLDM |
| BMC | BMC | BMC → MCTPoSPI → EROT | PLDM |
| BMC ERoT | BMC | BMC → MCTPoSPI → EROT | PLDM |
| SSD (Boot NVMe) | BMC | BMC → I2C → SSD | NVMe-MI |
| CX-9 | BMC | BMC → MCTPoUSB → SMA → MCTPoI3C → CX9 | PLDM |
| OSFP | LPU Driver | In-band via FPGA | TBD |

### 5.5 OOB Telemetry Path Table

All OOB telemetry exposed externally via **Redfish API** under the BMC service root. Internally, two transport patterns are used: **LSTPoUSB** (LSTP over USB) for raw-I2C / sensor-style telemetry from devices behind SMAs, and **MCTPoUSB** for NSM telemetry from the SMAs themselves and from MCTP-speaking devices.

| Target | Path | Protocol | New vs VR-NVL72 |
| --- | --- | --- | --- |
| LPU | BMC → LSTPoUSB → SMA(M) → I2C → LPU | Raw I2C | Yes |
| FPGA | BMC → LSTPoUSB → SMA(M1) → I2C → FPGA | Raw I2C | Yes |
| LPU – SMA(M) | BMC → MCTPoUSB → SMA(M) | NSM | No |
| FPGA – SMA(M1) | BMC → MCTPoUSB → SMA(M1) | NSM | No |
| OSFP | BMC → LSTPoUSB → SMA(M1) → I2C → FPGA → OSFP | Raw I2C | Yes |
| SSD | BMC → I2C → SSD | NVMe-MI | No |
| BF-4 (when present) | BMC → MCTPoUSB → SMA → MCTPoI3C → CX9 | NSM | No |
| x86 | BMC → MCTPoUSB → SMA-M → MCTPoI3C → x86 OR BMC → eSPI → x86 | Vendor defined | Same as DGX |

### 5.6 P4105 Management Module Connector

The SMM-to-HPM connection uses a **"USB-first" reduced 28-pin connector plus MCIO** (optional PCIe).

| Signal class | Count | Notes |
| --- | --- | --- |
| `USB_MGMT` | 2× | 1 dedicated to BMC, 1 dedicated to HMC |
| `I2C_MGMT` | 3× | Split between BMC and HMC |
| `SPI` | 1× | BMC, with mux |
| `SSIF` | 1× | BMC |
| `MCIO` (PCIe) | optional | When PCIe path between HPM and SMM is required |

---

## 6. Transport Map (Detailed)

LP30's OOB management is layered: USB at the SMA/HMC ingress, then bridged into device-local buses (I3C, I2C, SPI, GPIO, UART). MCTP terminates at SMAs (not at LPU/FPGA). LSTP carries raw-I2C-style telemetry that doesn't fit MCTP framing.

### 6.1 BMC ↔ HMC

| Transport | Purpose |
| --- | --- |
| USB 2.0 (CDC/USBnet) | Redfish over USB Ethernet gadget; MCTP-over-USB |
| I2C | Virtual EEPROM / FRU |
| SPI (via ERoT) | PLDM T5 over MCTP/SPI |
| I2C | MCTP/I2C to ERoT |
| GPIO (via IO expander) | Reset / recovery / presence detection |

### 6.2 BMC ↔ HPM SMA (MCU-MB)

| Transport | Purpose |
| --- | --- |
| USB 2.0 (MCTP endpoint) | Direct MCTP/USB — telemetry, FW update, SPDM |
| USB 2.0 (CP2112 emulation) | Virtual I2C bus — GPIO expansion, CPLD access, leak detection |
| USB 2.0 (FLASHROM emulation) | Virtual SPI bus — CPU QSPI access |
| USB 2.0 (CP2108 UART) | Serial console — CPU UART |
| I2C (via IO expander) | GPIO over I2C — CPLD signals |

### 6.3 BMC ↔ CX-9 / IO-Board SMA

| Transport | Purpose |
| --- | --- |
| USB 2.0 (MCTP endpoint) | Direct MCTP/USB to IO-Board SMA |
| USB → SMA → I3C (bridged) | MCTP bridged to CX-9 |
| USB → SMA → I2C (bridged) | MCTP bridged to NVMe |

### 6.4 BMC ↔ Other Devices

| Target | Transport | Purpose |
| --- | --- | --- |
| PDB | I2C | HSC monitoring, VR/ADC, fan controller, temp sensors |
| x86 Host CPU | eSPI | Alert / reset signaling, host communication |
| x86 Host CPU | PECI | Thermal / power telemetry |
| x86 Host CPU | I3C | High-speed sensor protocol |
| x86 Host CPU | USB (via MCU-MB SPI bridge) | SPI flash access |
| x86 Host CPU | UART | Serial Over LAN (console, debug, boot progress) |
| x86 Host CPU | USB (PCIe endpoint) | Redfish / IPMI Host Interface (KVM, Virtual Media) |
| x86 Host CPU | PCIe | BMC PCIe Endpoint (KVM, Redfish, host connectivity) |
| x86 Host CPU | SGPIO | Serial GPIO (drive activity / fault indication) |
| x86 Host CPU | ASD (JTAG) | Intel At-Scale Debug |
| x86 Host CPU | SSIF (SMBus) | IPMI over SMBus (boot progress codes, IPMI commands) |
| x86 Host CPU | PLDM T2 over MCTP (PCIe/VDM or USB) | CPU sensors, effectors, CPER data collection |
| x86 Host CPU | CSWP over USB | CoreSight Wire Protocol for ARM debug (where applicable) |
| BMC ERoT | SPI | MCTP/SPI |
| Host CPU ERoT | USB → MCU-MB → MCTP/SPI | FW update / attestation |
| CPLD | I2C via IO expander | GPIO / register access |
| Boot NVMe SSD | SMBus / MCTP | NVMe-MI for drive management |
| TPM | SPI | TPM interface |
| Front IO | GPIO | Buttons / LEDs |
| BF-4 (when present) | USB.NET → BF4 BMC → Redfish | Redfish |

### 6.5 HMC ↔ Downstream Devices (when HMC present)

| Path | Transport | Purpose |
| --- | --- | --- |
| HMC → USB → MCU-M → I3C → LPU | MCTP / NSM / PLDM T2 | FW update, telemetry, attestation, power limiting, configuration |
| HMC → USB → MCU-M | PLDM T5 / SPDM over MCTP | MCU-M itself: FW update, attestation, health monitoring |
| HMC → USB → MCU-M1 → I3C → FPGA | PLDM T5 / NSM / SPDM over MCTP | FW update, telemetry, attestation |
| HMC → USB → MCU-MB | I2C bridging | HPM-SMA recovery, CPU recovery stage 1, GPIO control |
| HMC → USB | MCTP over USB / USBRCM | Streaming boot, CPU recovery stage 1, PLDM FW update stage 2, DOT |
| HMC → USB | CSWP | At-Scale Debug |
| HMC → USB | POST code read | Boot progress |
| HMC → USB → IO-SMA → I3C → CX-9 | MCTP / PLDM | CX-9 telemetry and FW update |
| HMC → via MCU/SMA bridges → LPU ERoT | SPDM over MCTP | LPU attestation, secure key exchange |
| HMC → via MCTP paths → IRoT (x86 / LPU) | NSM Type 6 | FW update, attestation, DOT |

### 6.6 MCU-M (Per-LPU Management MCU) — Internal Interfaces

| Path | Transport | Purpose |
| --- | --- | --- |
| MCU-M ↔ HMC (upstream) | USB | MCTP over USB — all OOB management bridging |
| MCU-M ↔ LPU | I3C | MCTP / NSM / PLDM T2 (telemetry, SPDM attestation, MCTP bridging, EID management) |
| MCU-M ↔ LPU | SPI | PLDM T5 / ERoT (FW update, secure boot, write protection, background copy) |
| MCU-M ↔ LPU | I2C (TMP452-class) | Direct temp sensor read (fallback) |
| MCU-M ↔ LPU | I2C (CP2112 virtual) | OCP Recovery — LPU recovery stage 1 I2C forwarding |
| MCU-M ↔ LPU | GPIO | Reset control, IRoT error detection, recovery triggering |
| MCU-M ↔ HMC | GPIO (interrupt line) | Event notification — real-time error / event alerts |

---

## 7. Security Chain of Trust

### 7.1 Block Structure (per DCSCM / HPM / LPU Baseboard)

| Block | Components | RoTs |
| --- | --- | --- |
| **DCSCM** | BMC, BMC-side ERoT | BMC ERoT (IRoT anchor) |
| **HPM** | x86 Host CPU, Host CPU ERoT, MCU-MB (SMA-MB) | Host CPU ERoT; MCU-MB IRoT |
| **LPU Baseboard** | LPU modules (8× × 2 LPUs), FPGA boards (2×), MCU-M / MCU-M1 / MCU-C | LPU vRoT via MCU-M; FPGA vRoT via MCU-M1 |

### 7.2 Component RoT Table

| Component | Vendor | Device | RoT Type | Notes |
| --- | --- | --- | --- | --- |
| LPU | NVIDIA | LPU v3 | vRoT via MCU-M | MCU-M anchors LPU FW chain; LPU does not have its own ERoT |
| FPGA | Intel/Altera | Agilex 7 M-series | vRoT via MCU-M1 | MCU-M1 anchors FPGA FW chain |
| MCU-M / MCU-C | NXP | MCXNV556 | IRoT | MCUs are themselves IRoT anchored |
| MCU-M1 | — | MCU | IRoT | FPGA management MCU |
| MCU-MB | — | MCU | IRoT | HPM management MCU |
| BMC | — | — | ERoT (BMC-side) | DCSCM block; IRoT anchor for BMC + x86 chain only — not a comm channel |
| HMC (optional) | Aspeed | AST2600 | ERoT (HMC-side) | When present; IRoT anchor for HMC chain only — not a comm channel; independent from BMC-side ERoT |
| x86 Host CPU | Intel | Granite Rapids 1S | Host CPU ERoT (under DCSCM/HPM chain) | Reached via MCU-MB MCTP/SPI |
| CPLD | — | — | Under BMC ERoT / MCU-MB | — |

### 7.3 Security Capabilities

LPU, FPGA, MCU, x86 host, BMC, HMC (when present), and CPLD all support: **secure boot, secure firmware update, attestation (OOB), secure recovery**.

Additional capabilities specific to LP30:
- **LPU Secure Mode** + **FPGA SDM (IRoT)** enabled.
- **UEFI Secure Boot** for the host OS.

### 7.4 Security Properties

**Provides (baseline equivalency with VR-NVL72 and GB200/300):**

- Baseline OOB security assurances for infra owner around secure boot, update, recovery, and attestation across all devices with mutable firmware.
- **Protects tenant from model-weight exfiltration via LPU debug ports.**
- Platform integrity assurances for both infra owner and tenant.

**Does NOT provide (deferred to Secure AI proposal):**

- Encryption of model weights in transit.
- In-band attestation of LP30 by the tenant.

### 7.5 Hierarchy

- **BMC-side ERoT** is the immutable IRoT anchor for the **BMC + x86 + MCU-MB + BF-4 (when present) + CPLD + TPM + IO-Board SMA + CX-9 + Boot NVMe** chain.
- **HMC-side ERoT** (when HMC is present) is the immutable IRoT anchor for the **HMC + LPU modules + FPGA boards + MCU-M / MCU-M1** chain.
- **The two ERoTs are independent** — not interconnected. Each anchors only its own component's secure boot / FW update / attestation / recovery.
- **BMC ↔ HMC peer attestation** (runtime) flows over the BMC↔HMC USB peer link as standard PLDM/MCTP traffic — not through the ERoTs.
- **MCU-M / MCU-M1** are IRoT anchors that act as **vRoT** for LPU / FPGA respectively.
- **MCU-C is not in the OOB security chain** — control-plane USB→SPI bridge only. MCU-M owns reset and recovery of MCU-C as a hardware sideband.

---

## 8. OOB Telemetry Field Catalog (NUDDs)

Per-component telemetry fields exposed via Redfish on the BMC service root. Fields are surfaced from the device-side (LPU, FPGA, etc.) through the OOB transport chain described in §5.5 and §6.

### 8.1 LPU (16 per tray)

**Processor:** Serial Number, Voltage Bin Number, Boot Status Code, FW Version
**Processor Metrics:** SPI CRC Error Count, Core Clock Speed, Microcontroller Clock Speed, C2C Clock Speed, Single Bit Error Count, Multi Bit Error Count, Activity Monitor, Fault Registers Code, Serdes Link Lock Status, Serdes FEC Error Status

### 8.2 LPU Module (8 per tray)

**Sensors:** Voltage Regulator Sensors, Module Temp Sensors, LPU Die Temp Sensors
**FRU Data:** Module Inventory

### 8.3 Baseboard

**Sensors:** Voltage Regulator Sensors, Board Temp Sensors
**FRU Data:** Baseboard Inventory

### 8.4 FPGA (2 per tray)

**Sensors:** Voltage Regulator Sensors, Board Temp Sensors, FW Version

### 8.5 OSFP (10 per tray)

**Metrics:** Link-lock status per lane (front panel), LOL fault loss-of-link per lane (front panel), Part Number / Serial Number (front panel), SFP board temperature, SFP Voltage, SFP Tx/Rx Power, SFP Bias, SFP board Serial Number

### 8.6 SMA (MCU)

**Processor:** SKU ID / UUID, Last Reset Reason, FW Version

### 8.7 Host CPU

**CPU:** Average Power, Power Cap, Package TDP, OTS Package and Die Temp, CPU Inventory
**DIMM:** TSOD Temp, DIMM Temp, DRAM Energy, Average Power
