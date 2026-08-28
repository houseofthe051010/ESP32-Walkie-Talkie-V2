# Walkie-talkie PCB

This project is a two-layer, 45 × 100 mm handheld voice-radio PCB built around an ESP32-WROOM-32D-N16, an Ai-Thinker Ra-01SH/SX1262 915 MHz radio with I-PEX antenna socket, an ICS-43432 digital microphone, and a MAX98357A Class-D speaker amplifier.

The current design is the **Final Draft (2026-08-27)** of Revision E: the mounting/expansion WROOM + CH340C + Ra-01SH board plus a formal pre-production audit. The exact pre-audit state is preserved under `Schematics/Legacy/Revision E pre-final audit 2026-08-27/`. An S3 radio-board variant was discussed but intentionally not built yet.

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

Final Draft machine checks on 2026-08-27:

- ERC: 0 errors, 0 warnings.
- DRC: 0 violations.
- Unconnected pads: 0.
- Board: 45 × 100 mm, two copper layers.

### Revision E mounting, OLED, and expansion update

Four M3 mounting holes were added at the corners, the Ra-01SH moved inward while retaining top-edge coax access, and the high-current wire pads were reduced to 2.6 mm copper around 1.2 mm drills to free mechanical space. The OLED holes were rotated 180° so their physical left-to-right order is `SDA`, `SCL`, `3V3`, `GND`, placing ground on the right. Two nearby DNP probe pads expose the status-LED net (GPIO2) and GPIO12 for optional future hardware. GPIO12 remains a boot-strapping pin and must not be forced to an invalid level during reset.

Revision E was re-routed and machine checked on 2026-08-26: ERC 0 errors (one explained MAX98357A exposed-pad warning), DRC 0 violations, and 0 unconnected pads.

The hand-soldered connector holes were subsequently labeled on `B.Silkscreen`. The labels identify the potentiometer, external LED, battery, speaker, OLED, and system-switch pads while leaving the component-side layout uncluttered. Copper traces underneath do not interfere because the solder mask separates copper from the silkscreen ink.

Back-side branding was added in the open upper-center region: large italic `Verma Industries` lettering with `ESP32 Walkie Talkie V2` beneath it. The artwork uses ordinary white silkscreen and therefore remains compatible with a black solder-mask order.

## Mistakes, failed approaches, and fixes

This section records the parts of the process that did not work cleanly. It is intentionally more candid than a normal release summary so later revisions do not repeat the same mistakes.

### 1. The first mechanical target was too narrow

**Problem:** The original approximately 35 mm-wide target made the five-button controls cramped and left poor routing space around the microphone, USB-C, power converter, and amplifier.

**Why it happened:** Width was treated as a constraint before the actual control geometry and enclosure ergonomics were established.

**Fix:** The preferred board size became 45 × 100 mm. The extra 10 mm was deliberately used for a square 12.5 mm-pitch four-button group, an isolated BTN5, better microphone separation, wider power paths, and RF clearance. The design was not compressed back toward 35 mm merely because it could theoretically fit.

**Lesson:** Place the human-interface and enclosure-critical parts first, then derive the board outline and electrical placement from them.

### 2. The speaker keep-out was initially interpreted too aggressively

**Problem:** A large portion of the top of the PCB was initially left empty because the 40 mm speaker region was treated almost like a complete component keep-out. This crowded the electronics lower on the board.

**Why it happened:** The early requirement described a speaker envelope but did not initially make the vertical arrangement completely clear.

**Fix:** The speaker was clarified to sit above the PCB rather than on it. Low components, the ESP32, and other circuitry may occupy the projected X/Y area as long as the enclosure provides adequate Z-clearance around the speaker basket, magnet, grille, and wiring. The OLED top reference still remains below Y = 47.5 mm.

**Lesson:** A 2D enclosure overlap is not automatically a PCB keep-out. Mechanical requirements need X, Y, and Z clearance definitions.

### 3. The original OLED choice was expensive and frequently unavailable

**Problem:** The first board used a directly assembled QG-2864TMBEG01/SSD1306 display. JLCPCB quoted it as an Extended item, showed shortages, and priced it much higher than common retail OLED modules.

**Fix:** The bare display footprint and its assembly cost were removed. Revision E uses four 2.54 mm plated holes for a separately purchased 0.96-inch SSD1306 I2C module.

**Secondary mistake:** The first replacement footprint rendered a physical black pin header even though only four holes were wanted.

**Secondary fix:** A custom holes-only footprint was created with no header 3D model. The row was later rotated 180° after the desired cable order was clarified. Component-side left-to-right order is now `SDA`, `SCL`, `3V3`, `GND`.

**Lesson:** For commodity modules, compare turnkey PCBA pricing with a hand-installed retail module before committing to a specialized assembled footprint.

### 4. The original 3.2 V LDO wasted usable battery capacity

**Problem:** The AP7361C LDO could no longer regulate when a loaded single-cell Li-ion battery approached the mid-3 V range, even though the cell still contained useful energy.

**Why it happened:** The first design focused on generating a logic rail without fully considering dropout across the complete battery-discharge curve and ESP32 current transients.

**Fix:** The LDO was removed and replaced by a fixed 3.3 V TPS63021 synchronous buck-boost. It bucks above 3.3 V, transitions near 3.3 V, and boosts below it. The MAX98357A remains on `SYS_SW` so the regulator does not carry speaker-amplifier current.

**Lesson:** A battery-powered regulator must be evaluated at minimum cell voltage and peak load, not just nominal battery voltage and average current.

### 5. Early cost estimates did not match the JLCPCB checkout price

**Problem:** An early two-board estimate was close to $90, while an actual JLCPCB quote was around $40–$43 before later changes. At the same time, individual parts such as the ESP32, microphone, amplifier, and OLED appeared surprisingly expensive in the uploader.

**Why it happened:** Small-run PCBA pricing mixes component quantity, minimum purchase quantity, setup, stencil, Extended-part feeder fees, assembly class, and stock substitutions. A simple sum of distributor unit prices did not reproduce JLCPCB's quoting model.

**Fix:** Cost estimates were changed to planning ranges rather than false precision. Actual BOM and CPL files were uploaded to obtain the real quote. Expensive or unavailable modules were reconsidered, especially the OLED and ESP32 variant.

**Lesson:** For a two- or five-board PCBA, the uploaded quote is the authoritative cost test. Component retail prices alone are not enough.

### 6. JLCPCB stock and assembly classification changed design decisions

**Problem:** Several initially selected parts appeared as Extended, Standard-only, overpriced, or out of stock during quoting. A technically compatible part was not always an economically buildable part.

**Fix:** The design process began checking LCSC/JLC codes, package matches, stock, and Economic-PCBA eligibility before treating a part as final. The engineering BOM preserves manufacturer and JLC identifiers, while the manufacturing BOM contains only installed parts.

**Limitation:** Stock is time-dependent. A part that was available while Revision E was prepared may be unavailable when the next order is placed.

**Lesson:** Electrical compatibility, footprint compatibility, live stock, and assembly classification are four separate checks.

### 7. The ESP32 antenna requirement was solving the wrong radio problem

**Problem:** Early ESP32 candidates were constrained to modules with U.FL connectors, but the desired external antenna was really needed for the long-range voice link rather than Wi-Fi/Bluetooth.

**Fix:** The ESP32 now uses its ordinary onboard 2.4 GHz PCB antenna. A separate Ra-01SH/SX1262 module provides the 915 MHz link and its own I-PEX/U.FL-compatible connector.

**Lesson:** Keep the control/firmware radio and the long-range communications radio requirements separate.

### 8. The ESP32-S3 native-USB option was electrically attractive but economically poor

**Problem:** An ESP32-S3 could eliminate the CH340C and use native USB, but the desired S3 assembly option changed the order from Economic to Standard and increased the small-run price substantially.

**Fix:** Revision E uses the Economic-compatible ESP32-WROOM-32D-N16 plus one CH340C USB-UART IC and its automatic-programming transistors. An S3 version remains a possible future variant but was intentionally not mixed into this release.

**Lesson:** Removing one IC does not save money if the replacement changes the assembly service class for the entire board.

### 9. The ESP32 appeared rotated incorrectly in the JLCPCB preview

**Problem:** KiCad showed the WROOM antenna facing the intended left edge, but the JLCPCB assembly preview showed the module approximately 90° wrong with the antenna facing downward.

**Why it happened:** JLCPCB's library orientation datum for the ESP32 module differs from KiCad's footprint orientation datum.

**Fix:** The JLC CPL generator applies a U6-specific +90° rotation correction. The released CPL lists U6 at 180°. The final assembly preview must still be checked visually before ordering.

**Lesson:** A correct PCB footprint rotation does not guarantee a correct pick-and-place rotation. Always inspect the assembler's final preview.

### 10. Mounting holes were added too late

**Problem:** The routed board originally had no enclosure mounting holes, and top connectors and the radio occupied corner space needed by screws.

**Fix:** Four 3.2 mm NPTH M3 holes were added at `(4,4)`, `(41,4)`, `(4,96)`, and `(41,96)`. The radio moved inward, top wiring pads moved, and the battery/speaker/switch wire pads were reduced to 2.6 mm copper around 1.2 mm drills.

**Lesson:** Mounting holes, screw-head envelopes, and connector access should be locked before detailed routing.

### 11. GPIO expansion was considered only after routing

**Problem:** GPIO12 was left unexposed, and the status-LED GPIO could not conveniently be reused for experiments.

**Fix:** TP7 exposes `LED_STATUS`/GPIO2 and TP8 exposes GPIO12 beside the programming pads. Both are DNP copper pads and do not add assembly cost.

**Caution:** GPIO2 and GPIO12 are boot-strapping pins. External hardware must not force invalid levels during reset. TP7 also shares the status LED load, so driving the LED and an external device are not electrically independent.

**Lesson:** Reserve expansion/test access early, but document boot-strap and shared-load behavior clearly.

### 12. Autorouting did not produce a finished board by itself

**Problem:** Freerouting completed most connections but one version hung during optimization, another returned three unfinished connections, and its imported result contained awkward ground spurs.

**Fix:** The optimizer was disabled temporarily to recover a session, then the result was imported and manually completed. The remaining microphone 3V3 path, `SPK-`, left-edge potentiometer/LED routes, and ground stitching were repaired manually. A redundant radio-ground spur that produced a dangling-track warning was removed rather than suppressing the warning.

**Lesson:** Autorouter completion is only a starting point. Every imported route still needs visual review, net-class review, zone refill, and native KiCad DRC.

### 13. Ground and noise-sensitive routing required several iterations

**Problem:** The microphone, Class-D amplifier, buck-boost, battery ADC, and radio all compete for limited two-layer routing space. Early routing attempts risked isolated ground sections or long/noisy return paths.

**Fix:** Additional ground stitching vias were added, the amplifier return was tied explicitly into the main ground network, the buck-boost switch nodes were kept local, and the microphone region was kept away from the inductor and Class-D outputs. High-current nets use wider trunks with only short package-clearance neck-downs.

**Lesson:** A filled plane does not automatically guarantee a good return path. Connectivity and current-loop geometry must both be examined.

### 14. The first solder-pad label layouts failed DRC

**Problem:** The first back-silkscreen labels were horizontal and close enough that neighboring words overlapped. Rotating every label vertically fixed word-to-word overlap but caused text to cross solder-mask openings, where JLCPCB would clip it.

**Fix:** The labels were returned to horizontal orientation and staggered vertically. They use 1.0 mm character height and 0.15 mm strokes and now remain clear of each other and exposed pads. DRC returned to zero violations.

**Lesson:** Silkscreen can safely cross masked copper traces, but it cannot cross exposed pads or solder-mask openings and still be expected to print completely.

### 15. Manufacturing exports had to be regenerated after every visible PCB change

**Problem:** Updating the KiCad board does not update an already-created Gerber ZIP, BOM, CPL, or render. It is easy to accidentally quote an older revision.

**Fix:** After the OLED reversal, mounting changes, pad labels, and branding, the Gerbers and ZIP were regenerated. BOM/CPL parity was checked at 63 installed references, and the copied repository ZIP was verified against the source using SHA-256.

**Lesson:** Treat manufacturing outputs as disposable build artifacts generated from a tagged PCB revision, not as files that update themselves.

### 16. The USB-UART voltage was electrically unsafe in the pre-final schematic

**Problem:** CH340C VCC was connected to raw `USB_5V`, while its TX output went directly to the ESP32's 3.3 V UART input. That could drive the ESP32 above its allowed input range. It also created an avoidable risk that USB power would feed signals into an otherwise switched-off controller.

**Why it happened:** The CH340C supports both 5 V and 3.3 V operation, and the earlier design treated USB power as the simplest supply without tracing the actual UART logic-high voltage all the way to the ESP32 pin.

**Fix:** CH340C VCC pin 16 and V3 pin 4 were tied together and moved to the switched regulated `3V3` rail, following WCH's 3.3 V configuration. C30 remains the 100 nF local bypass. The consequence is intentional and documented: the main switch must be ON for programming, while TP4056 charging still works with it OFF.

**Lesson:** “Compatible with 3.3 V and 5 V” does not mean the output is automatically level-shifted. Always verify which supply controls each output-high level.

### 17. The digital microphone data line was missing its recommended pull-down

**Problem:** The ICS-43432 tri-states its SD output outside its active channel period. The manufacturer's application guidance calls for a 100 kΩ pull-down so the line does not float, but the earlier schematic had none.

**Fix:** R26, 100 kΩ, was added from `MIC_DATA` to GND close to MK1. A Basic 0402 part (C25741) was chosen, so the correction does not create another Extended feeder line.

**Lesson:** Digital interfaces still have analog states such as high impedance. Datasheet “recommended application” resistors must be audited even when ERC shows a connected digital net.

### 18. The first final-audit reroute damaged a previously clean layout

**Problem:** The first attempt to incorporate the CH340 power change and microphone pull-down produced 76 DRC violations. The edit moved too much existing routing and created overlapping or clearance-breaking geometry.

**Fix:** That attempt was discarded. The PCB was restored from the preserved pre-final-audit snapshot, and only the affected nets were changed: U2 VCC/V3/C30 to 3V3, a short USB_5V reroute, and the new R26 connection. The result returned to 0 violations and 0 unconnected pads.

**Lesson:** A late-stage board should be repaired surgically. Preserve a known-clean checkpoint before modifying power nets, and restore it immediately if a broad reroute creates cascading errors.

### 19. A new footprint's metadata accidentally became silkscreen artwork

**Problem:** The first R26 PCB footprint included visible custom fields for manufacturer, MPN, classification, and notes. Those fields produced 29 silkscreen clearance/overlap warnings even though the electrical placement was correct.

**Fix:** Reference/value/custom fields were hidden on the compact resistor footprint, and unnecessary local silkscreen strokes were removed. The engineering data remains in the schematic and BOM where it belongs. DRC returned to zero.

**Lesson:** BOM metadata and fabrication graphics serve different purposes. Custom fields should default to hidden on dense production footprints.

### 20. A symbol-library warning was fixed instead of merely explained

**Problem:** Earlier releases accepted one ERC warning because MAX98357A exposed pad 17 was typed `Unspecified` in the embedded symbol while being correctly tied to GND. The connection was electrically right, but leaving a permanent warning made it easier to overlook a future real warning.

**Fix:** Pin 17 was retyped as a power input. It remains grounded, and final ERC now reports 0 errors and 0 warnings without exclusions or per-item suppression.

**Lesson:** A zero-warning release is valuable when achieved by correcting metadata rather than hiding checks.

### 21. The radio looked absent in the copied repository render

**Problem:** The Ra-01SH footprint referenced `${KIPRJMOD}/3d/Ra-01SH_approx.wrl`, but the copied repository lacked the `3d` asset. Pads and routing were present, yet KiCad's 3D viewer showed an empty module site, which made orientation review harder.

**Fix:** The existing approximate radio model was copied into the active project and added to the Final Draft source package. This is a visualization fix only; the manufacturing footprint and CPL were already present.

**Lesson:** A self-contained KiCad release must include project-local footprint and 3D-model dependencies, not only the `.kicad_sch` and `.kicad_pcb` files.

### 22. The raw placement CSV and assembler-ready CPL are deliberately different

**Problem:** KiCad's U6 rotation is correct for the PCB, but JLC's ESP32 library datum is offset by 90°. Uploading the raw KiCad position CSV would reproduce the user's earlier preview with the antenna facing downward.

**Fix:** The Final Draft build script generates both files but applies a U6-only +90° correction to `walkiepcb_final_jlc_cpl.csv`. It asserts that U6 is at `(16.000, 49.500)` with 180° rotation and refuses release if BOM/CPL references differ. The raw file is retained only for audit and is explicitly labeled not for upload.

**Lesson:** Assembly orientation is a library-contract problem, not just a PCB rotation number. Automate known corrections and still inspect the assembler's final preview.

## Known risks and work still requiring physical validation

The Final Draft passes machine electrical checks, but it has not yet been proven by assembled-hardware testing. The following items remain validation tasks rather than completed facts:

- Confirm the exact purchased OLED module pin order, outline, mounting height, and I2C address before applying power.
- Verify speaker basket/magnet Z-clearance over the upper PCB components and the external antenna cable bend radius.
- Confirm charging current and TP4056 thermal performance with the intended cell and enclosure ventilation.
- Measure the 3.3 V rail during ESP32 transmit bursts and near the intended low-battery cutoff.
- Measure microphone noise while the buck-boost, Wi-Fi, SX1262, and Class-D amplifier are active.
- Verify amplifier stability, speaker impedance, volume, and acoustic feedback in the real enclosure.
- Validate SX1262 GFSK/FSK voice bitrate, packet loss behavior, legal regional settings, antenna matching, and real-world range.
- Confirm every JLCPCB part is still in stock and that the final DFM/assembly preview matches the intended orientation.
- Select black solder mask in the order form; Gerbers encode mask openings, not mask color.
- Write and test firmware. The current release is hardware documentation, not a completed end-to-end walkie-talkie product.

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
