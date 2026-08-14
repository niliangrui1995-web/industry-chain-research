# VR-NVL72 — Platform Overview

**Platform:** Vera Rubin NVL72
**Source:** VR NVL72 System Architecture Overview (March 2026) + platform owner input
**Last updated:** 2026-04-14

> All content in this document is sourced directly from platform owners. Do not infer, extrapolate, or carry over details from other platforms. If a detail is not listed here, it is unknown.

---

## 1. Rack Composition

| Item | Count / Value |
| --- | --- |
| GPUs per rack | 72× Rubin GPU |
| Compute trays per rack | 18× (10× full + 8× — see rack elevation) |
| NVLink Switch trays per rack | 9× |
| GPU topology per compute tray | 2× Vera CPU : 4× Rubin GPU |
| HPM boards per compute tray | 2× HPM |
| GPU TGP | 1.8 kW (Max Q) / 2.3 kW (Max P) |
| Cooling | 100% liquid cooled (compute + switch trays); air cooled power shelves |

---

## 2. Compute Tray

### 2.1 Component Inventory

| Component | Device | Vendor | Count / Tray | Notes |
| --- | --- | --- | --- | --- |
| CPU | Vera CPU | NVIDIA | 2× | SOCAMM LPDDR5x memory; 96 Gen6 PCIe lanes; 1× per HPM |
| GPU | Rubin GPU | NVIDIA | 4× | 2× per HPM; 36× NVLink6 ports per GPU |
| E/W NIC | ConnectX-9 (CX9) | NVIDIA | 4× modules | 2× per CX9 Bay; 2× CX9 Bays per tray; 1600G E/W bandwidth per GPU |
| N/S NIC | BF4 DPU | NVIDIA | 1× | 800G; PCIe Gen5 ×8 to CPU0 + ×8 to CPU1 |
| HMC | AST2600 | Aspeed | 1× | Pluggable HMC module; mounted on SMM carrier board |
| BMC (Host BMC) | AST2600 | Aspeed | 1× | On SMM carrier board; reference design |
| ERoT (BMC/HMC) | CEC1736 (Glacier) | Microchip | 1× | IROT; on SMM; protects both BMC and HMC |
| MCU | MCXN556 | NXP | 2× | IROT; 1× per HPM; manages HPM, GPU, CX9; acts as MCTP bridge |
| CPLD | MachXO2 | Lattice | — | Controlled by MCU; MCU owns secure boot/update/recovery/attestation |
| TPM | — | — | 1× | Modular TPM; on compute tray (reference design) |
| Boot drive | E1.S | — | 1× | PCIe Gen5; on SMM extender board |
| PDB | Power Distribution Board | NVIDIA | 1× | Fixed to midplane; NVIDIA manufacturing kit |

### 2.2 System Management Module (SMM)

The SMM occupies the 1U front section of the Center Bay (Bay C) on each compute tray. It is pluggable to Bay C and contains:

- BMC module (Aspeed AST2600)
- HMC module (Aspeed AST2600)
- Carrier board
- Extender board with E1.S boot drive
- TPM board
- Front Panel IO board

The ERoT (CEC1736) is mounted on the SMM and provides immutable root of trust for both the BMC and the HMC.

---

## 3. NVLink Switch Tray

### 3.1 Component Inventory

| Component | Device | Vendor | Count / Switch Tray | Notes |
| --- | --- | --- | --- | --- |
| NVSwitch | NVL6 NVSwitch | NVIDIA | 4× | 72× NVLink6 ports per switch |
| Management CPU | AMD EPYC 3151 | AMD | 1× | COMe form factor; switch tray management |
| BMC | AST2600 | Aspeed | 1× | Switch tray BMC |
| ERoT (BMC + CPU) | CEC1736 | Microchip | 1× | IROT |
| MCU | MCXN556 | NXP | 1× | IROT |
| CPLD | MachXO3D | Lattice | 1× | IROT |
| TPM | ST33KTPM2XDKJ0 | ST Micro | 1× | IROT |

---

## 4. CX9 Module

| Item | Value |
| --- | --- |
| Form factor | 394 mm × 125 mm, ½U |
| CX9 ASICs per module | 2× |
| E1.S SSD per module | 1× |
| Modules per compute tray | 4× (2× per CX9 Bay, 2× Bays per tray) |
| OSFP ports | Co-located on CX9 board (not on HPM) |
| E/W bandwidth | 1600G total per GPU package |

---

## 5. Management Architecture

### 5.1 Ownership Split

| Manager | Devices Managed | Path |
| --- | --- | --- |
| HMC | Vera CPU (SatMC) | Direct MCTP over USB (no bridge) |
| HMC | Rubin GPU | MCTP over USB via GPUMCU (NXP MCXN556) bridge |
| Host BMC | CX9 NICs | MCTP over USB via CX9 bridge |
| Host BMC | SSDs | USB (storage management) |
| Host BMC ↔ HMC | — | USB via USB HUB on compute tray |

**Key facts:**
- Main board-to-board interconnect on the compute tray is **USB**
- HMC has **no FPGA**
- HMC is protected by ERoT (CEC1736) at TTM
- **Vera CPU SatMC** is the sub-component inside the Vera CPU responsible for RAS, eventing, and telemetry. It connects **directly** to HMC via MCTP over USB — no MCU bridge
- **Rubin GPU** connects to HMC via the GPUMCU (NXP MCXN556 acting as MCTP bridge) — not direct
- **CX9** connects to Host BMC via a CX9 bridge — not direct MCTP

### 5.2 Management Topology Diagram

```
                    +-----------------------------------------------+
                    |           Compute Tray (per tray)             |
                    |                                               |
  +--------+        |  +-----+   USB    +-----+                    |
  |  Host  |        |  | BMC | -------- | HUB | --- CX9 (x4)       |
  |  BMC   | -------|--+     |          |     | --- SSD             |
  +--------+ (USB)  |  +--+--+          +-----+                    |
                    |     |                                         |
                    |     | USB                                     |
                    |     |                                         |
                    |  +--+--+   USB    +-----+                    |
                    |  | HMC | -------- | HUB | --- GPUMCU --- Rubin GPU (x2, HPM0)
                    |  |     |          |     | --- GPUMCU --- Rubin GPU (x2, HPM1)
                    |  +-----+          |     | --- SatMC (Vera CPU 0, direct)
                    |                   |     | --- SatMC (Vera CPU 1, direct)
                    |                   +-----+                    |
                    +-----------------------------------------------+

  Note: GPUMCU = NXP MCXN556 acting as MCTP bridge
        SatMC   = Sub-component inside Vera CPU (RAS/telemetry/eventing)
        SatMC connects directly to HMC — no MCU intermediary
```

### 5.3 Endpoint Scale (per rack)

| Device | Path | Endpoints/Tray | Endpoints/Rack (18 trays) |
| --- | --- | --- | --- |
| Vera CPU SatMC | HMC → direct USB | 2 | 36 |
| Rubin GPU | HMC → GPUMCU → GPU | 4 | 72 |
| CX9 NIC | BMC → CX9 bridge | 4 modules | 72 modules |
| E1.S SSD | BMC → USB | 4+ | — |

---

## 6. MCTP Transport Map

| Source | Destination | Transport | Bridge/Intermediary | Notes |
| --- | --- | --- | --- | --- |
| HMC | Vera CPU SatMC | MCTP over USB | None (direct) | SatMC is the RAS/telemetry/eventing component inside Vera CPU |
| HMC | Rubin GPU | MCTP over USB | GPUMCU (NXP MCXN556) | MCU is the MCTP bridge |
| BMC | CX9 | MCTP over USB | CX9 bridge | Bridge details TBD |
| BMC | SSD | USB | — | Storage management |
| BMC ↔ HMC | — | USB | USB HUB | BMC and HMC interconnect via USB HUB on compute tray |

> ⚠️ Specific MCTP USB daemon names, EID assignments, and USB protocol framing (vendor/product IDs) for each path are NOT defined in this document — confirm with NvBMC Platform Team before specifying in any SADD or design document.

---

## 7. Security Chain of Trust

| Component | Vendor | Device | ROT Type | Notes |
| --- | --- | --- | --- | --- |
| Rubin GPU | NVIDIA | Rubin | IROT | — |
| Vera CPU | NVIDIA | Vera | IROT | — |
| CX9 NIC | NVIDIA | CX-9 | IROT | — |
| BMC (Host BMC) | Aspeed | AST2600 | EROT | Reference design; on SMM carrier board |
| HMC | Aspeed | AST2600 | EROT | Pluggable module; on SMM carrier board |
| ERoT (BMC/HMC) | Microchip | CEC1736 (Glacier) | IROT | On SMM; immutable RoT for both BMC and HMC |
| MCU (HPM/GPU/CX9) | NXP | MCXN556 | IROT | 2× per compute tray (1× per HPM) |
| CPLD | Lattice | MachXO2 | Controlled by MCU | MCU owns secure boot, update, recovery, attestation of CPLD |
| TPM | — | — | — | Modular; on compute tray (reference design) |

**Security hierarchy:**
- ERoT (CEC1736) is the immutable anchor for the BMC/HMC chain
- MCU (MCXN556) is the IROT anchor for HPM, GPU, and CX9; also controls CPLD
- Device-side IRoTs (Rubin, Vera, CX9) are independent per-device roots of trust

---

## 8. NvBMC Software Stack Notes

The following constraints apply when developing NvBMC features for VR-NVL72:

- **MCTP in-kernel stack** — the platform uses the Linux in-kernel MCTP stack (`drivers/net/mctp/mctp-usb.c`). Kernel interfaces are named `mctpusb<N>`. There is no userspace MCTP demux daemon (libmctp/demux approach is not used on this platform).
- **mctpd** (`au.com.codeconstruct.MCTP1`) handles endpoint discovery only. It is NOT in the data path. Consumers (pldmd, nsmd, etc.) use AF_MCTP sockets directly.
- **LSTP does not apply** — LSTP is specific to LPU V3. Vera CPU SatMC uses MCTP over USB (DSP0283 framing). Do not use "LSTP" in any SADD for this platform.
- **HMC has no FPGA** — do not specify FPGA-based MCTP bridges or SMA on the HMC path.
- **Two SatMC endpoints per compute tray** — 1 per Vera CPU, 2 Vera CPUs per tray → 36 SatMC MCTP endpoints per full rack.
- See `docs/nvidia-sdl/MCTP-Architecture.md` for the authoritative NvBMC MCTP stack description.
- See `docs/nvidia-sdl/System-Dump-Architecture.md` for the authoritative bmcweb↔PDC dump flow.
