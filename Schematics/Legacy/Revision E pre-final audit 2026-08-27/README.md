# Walkie-talkie PCB

This project is a two-layer, 45 × 100 mm handheld voice-radio PCB built around an ESP32-WROOM-32D-N16, an Ai-Thinker Ra-01SH/SX1262 915 MHz radio with I-PEX antenna socket, an ICS-43432 digital microphone, and a MAX98357A Class-D speaker amplifier.

The current design is **Revision E: mounting and expansion revision of the WROOM + CH340C + Ra-01SH board**. Revision D is preserved in `legacy/revision_d_wroom_radio_before_mounting_2026-08-26/`; the earlier pre-radio/S3 design is in `legacy/revision_c_s3_2026-08-24/`. An S3 radio-board variant was discussed but intentionally not built yet.

## Current features

- ESP32-WROOM-32D-N16 with 16 MB flash and onboard 2.4 GHz PCB antenna.
- Ra-01SH / SX1262 803–930 MHz radio, intended for 915 MHz operation, with on-module I-PEX/U.FL-compatible connector.
- CH340C USB-UART with DTR/RTS automatic programming.
- USB-C charging/programming port centered at the bottom.
- TP4056 charger set for approximately 500 mA.
- TPS63021 fixed 3.3 V synchronous buck-boost, allowing regulated operation as a 1S Li-ion cell moves above and below 3.3 V.
- Raw-battery ADC on GPIO34 using a 100 kΩ/100 kΩ divider and 100 nF filter.
- ICS-43432 bottom-port I2S microphone.
- MAX98357A I2S Class-D amplifier powered from `SYS_SW`.
- Four-hole wired interface for a commercial SSD1306 I2C OLED; no soldered bare OLED panel or header model.
- Five hand-soldered buttons: symmetric 2×2 cluster plus isolated BTN5.
- Top-left potentiometer and external LED wiring holes.
- Basic red charging and status LEDs near USB-C.
- Four M3 mounting holes, one in each cleared corner.
- Probe/expansion pads for 3V3, GND, UART TX/RX, EN, GPIO0, LED_STATUS/GPIO2, and GPIO12.
- DW01A + FS8205A cell protection, USB ESD protection, and resettable system fuse retained.

Real-time voice firmware should use compressed, packetized audio over SX1262 GFSK/FSK. LoRa mode is useful for low-rate, long-range data but is not suitable for ordinary continuous voice bandwidth.

## Design journal

### Initial design

The project began as a compact ESP32 walkie-talkie with USB-C charging/programming, a directly soldered OLED, I2S microphone and speaker amplifier, five controls, Li-ion charging/protection, and a regulated logic rail. The original narrow-board target was about 35 mm.

### Mechanical resize and speaker clarification

The enclosure target changed to approximately 100 mm tall × 45 mm wide. The wider board was used to improve button ergonomics, microphone separation, current routing, USB routing, and RF clearance. A 40 mm speaker occupies the upper enclosure region, but the speaker is mounted above the PCB. Therefore short components and RF/power circuitry are allowed underneath its X/Y projection as long as enclosure Z-clearance is verified. The OLED reference still obeys the hard rule that its top must be at least 47.5 mm below the PCB top; the final reference top is Y = 50.0 mm.

### Power-supply redesign

The AP7361C 3.2 V LDO was removed because a linear regulator would fall out of regulation while a 1S cell still had useful energy. It was replaced with a fixed 3.3 V TPS63021 synchronous buck-boost using the manufacturer's inductor/capacitor arrangement. MAX98357A stayed on the raw switched rail.

### Cost and assembly review

JLC's two-board price was much higher than the sum of retail component prices because setup, stencil, Extended-line feeder fees, and difficult packages dominate very small runs. The bare OLED was also overpriced and sometimes unavailable. The design changed to four bare 2.54 mm holes for a separately purchased SSD1306 I2C OLED module.

Several safety parts were examined as cost-down candidates: the resettable fuse, USB ESD device, DW01A, and FS8205A. They remain in Revision D because they provide fault, transient, overcharge, and overdischarge protection. A deliberately unprotected variant was not released.

### ESP32 and long-range radio decision

An ESP32-S3 with native USB was considered, including a separate S3 version. Economy/standard classification made the small-run price unattractive. The current board instead uses the Economic-compatible ESP32-WROOM-32D-N16 plus CH340C.

The ESP32 no longer needs an external antenna connector. A separate Ra-01SH/SX1262 915 MHz module supplies the long-range link and the I-PEX connector. The radio is near the top edge for coax access. The ESP32 moved downward into the previously empty middle area beneath the elevated OLED, with its PCB antenna facing the left board edge.

### Control and indicator revision

The OLED connector moved upward by 5 mm and was changed to a custom holes-only footprint. The four-button cluster was expanded to 12.5 mm pitch, BTN5 stayed isolated, and the microphone moved directly above BTN5. The POT and external LED holes moved to the top-left. Basic C2286 red LEDs were added for charge and status indication near USB-C.

### Final routing and verification

The board was routed as two layers with 0.40 mm high-current trunks, 0.30 mm 3V3 routing, short package neck-downs, and a B.Cu ground plane. The final difficult connections were the right-edge USB power path and the Class-D negative output. The switch connector pads were normalized to 3.0 mm around 1.5 mm drills so a short 0.20 mm USB edge neck could maintain clearance. The amplifier ground was explicitly carried into the main ground network.

Final machine checks on 2026-08-26:

- ERC: 0 errors, 1 explained MAX98357A exposed-pad symbol warning.
- DRC: 0 violations.
- Unconnected pads: 0.
- Board: 45 × 100 mm, two copper layers.

### Revision E mounting, OLED, and expansion update

Four M3 mounting holes were added at the corners, the Ra-01SH moved inward while retaining top-edge coax access, and the high-current wire pads were reduced to 2.6 mm copper around 1.2 mm drills to free mechanical space. The OLED holes were rotated 180° so their physical left-to-right order is `SDA`, `SCL`, `3V3`, `GND`, placing ground on the right. Two nearby DNP probe pads expose the status-LED net (GPIO2) and GPIO12 for optional future hardware. GPIO12 remains a boot-strapping pin and must not be forced to an invalid level during reset.

Revision E was re-routed and machine checked on 2026-08-26: ERC 0 errors (one explained MAX98357A exposed-pad warning), DRC 0 violations, and 0 unconnected pads.

The hand-soldered connector holes were subsequently labeled on `B.Silkscreen`. The labels identify the potentiometer, external LED, battery, speaker, OLED, and system-switch pads while leaving the component-side layout uncluttered. Copper traces underneath do not interfere because the solder mask separates copper from the silkscreen ink.

Back-side branding was added in the open upper-center region: large italic `Verma Industries` lettering with `ESP32 Walkie Talkie V2` beneath it. The artwork uses ordinary white silkscreen and therefore remains compatible with a black solder-mask order.

The expanded mistakes, failed approaches, fixes, and remaining physical-validation tasks are maintained in the repository-level [`DESIGN_JOURNAL.md`](../../DESIGN_JOURNAL.md). That document is the canonical project history; this file remains the compact hardware overview stored beside the KiCad source.

## Key files

- `walkiepcb.kicad_sch` — current schematic.
- `walkiepcb.kicad_pcb` — current routed PCB.
- `walkiepcb_jlc_bom.csv` — four-column, upload-ready JLC BOM with DNP parts excluded.
- `walkiepcb_bom_full.csv` — engineering BOM with fields for installed and hand-soldered parts.
- `PIN_ASSIGNMENTS.md` — firmware pin map.
- `LAYOUT_NOTES.md` — enclosure coordinates and routing notes.
- `JLC_PART_RESEARCH.md` — part selection and current Economic/stock evidence.
- `JLC_COST_ESTIMATE.md` — small-run cost explanation and planning range.
- `ERC_NOTES.md` — electrical verification record.
- `legacy/revision_c_s3_2026-08-24/` — preserved earlier design.

## Before ordering

Upload the Gerber ZIP, BOM, and CPL together. Recheck every Extended row for stock and package match, especially the ICS-43432, TPS63021, CH340C, ESP32-WROOM, MAX98357A, and Ra-01SH. Verify the purchased OLED module pin order and enclosure geometry before manufacturing the enclosure.
