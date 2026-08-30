# ESP32 Walkie Talkie V2 — build journal

This journal reconstructs the PCB-design work from the dated Codex task history and saved design artifacts. The time for every session is the recorded active task time multiplied by **2×**, as requested, to include the project author's thinking, reviewing and decision time between tool actions.

> [!IMPORTANT]
> Hack Club Blueprint currently prohibits AI-generated journal entries. This reconstruction is an evidence-backed draft, not a substitute for the author's own account. Before submission, the project author should check every entry, correct anything that does not match their experience, and rewrite the explanation in their own words. The images are real PCB screenshots, renders and quote screenshots from the project—not generated project images.

## Time summary

| Date | Recorded active task time | Journal time after 2× adjustment |
|---|---:|---:|
| 2026-08-24 | 3.06 h | 6.12 h |
| 2026-08-25 | 2.47 h | 4.95 h |
| 2026-08-26 | 1.28 h | 2.59 h |
| 2026-08-27 | 1.17 h | 2.33 h |
| **Design and validation total** | **7.98 h** | **15.99 h** |

The short documentation session that converted the repository into this submission draft is listed separately at the end and is not included in the 15.99-hour design subtotal.

---

## 2026-08-24 — Initial electrical design

**Portal summary:** `Built the first complete schematic`  
**Time:** 1.19 h

The first session turned the feature list into an editable KiCad schematic. The design included the ESP32, USB-C programming, Li-ion charging and protection, microphone, speaker amplifier, OLED, controls and diagnostic access. I checked the major component pinouts and produced a JLC-compatible engineering BOM instead of leaving the circuit as a conceptual block diagram.

The first version used an ESP32-WROOM-32UE, a directly assembled OLED panel and an AP7361C 3.2 V LDO. Those choices were electrically connected, but later cost and battery-life checks showed that several needed to change.

![Early PCB copper and placement audit](<Schematics/Journal Images/front-copper-audit.png>)

## 2026-08-24 — Mechanical resize and power redesign

**Portal summary:** `Resized the board and replaced the LDO`  
**Time:** 2.17 h

The enclosure geometry changed from a narrow approximately 35 mm board to a 45 × 100 mm portrait board. I placed the OLED below the speaker region, kept USB-C centered at the bottom, separated BTN5 from the square four-button cluster and moved noise-sensitive microphone circuitry away from the power converter and amplifier.

The speaker was clarified to sit above the PCB, so the top did not need to remain electrically empty. I moved low-profile electronics into that area and replaced the dropout-limited AP7361C with a fixed 3.3 V synchronous buck-boost supply. This used more of the cell's discharge curve and preserved room for ESP32 current transients.

![Intermediate component placement](<Schematics/Journal Images/revision-e-top.png>)

## 2026-08-24 — Routing, manufacturing outputs and first quote

**Portal summary:** `Routed the PCB and generated quote files`  
**Time:** 1.95 h

I routed the two-layer board, added a back copper ground plane, widened the system and amplifier power paths, kept the buck-boost switching loop compact and checked that the microphone was not next to the inductor or Class-D outputs. KiCad reached zero DRC violations and zero required unconnected pads.

I then generated the Gerber ZIP, JLC BOM and CPL so the cost could be tested with a real assembler upload. This was important because a spreadsheet sum of component prices did not include stencil, setup, feeder and Extended-part charges.

![First JLCPCB quote breakdown](<Schematics/Journal Images/jlc-price-quote.png>)

## 2026-08-24 — Cost findings and safety tradeoffs

**Portal summary:** `Investigated why PCBA cost was high`  
**Time:** 0.81 h

The uploaded quote showed that small-run setup and Extended-component fees dominated the price. I compared the quote with individual component costs and identified the display, microphone, ESP32, radio, amplifier and regulator as expensive or stock-sensitive lines.

The resettable fuse, USB ESD protection and Li-ion protection were considered for removal, but the final design retained them because the savings did not justify losing short-circuit, transient, overcharge and overdischarge protection. The directly assembled OLED was a better cost-down target.

![JLC stock and alternate-part review](<Schematics/Journal Images/jlc-stock-review.png>)

---

## 2026-08-25 — Replaced the assembled OLED

**Portal summary:** `Changed the OLED to four wiring holes`  
**Time:** 0.36 h

The directly soldered OLED was expensive and sometimes unavailable through assembly. I changed the board to four 2.54 mm plated holes for a common commercial SSD1306 I2C module. This lets the OLED be purchased separately and mounted above the main PCB with wires or spacers.

The first replacement footprint accidentally carried a rendered black header, even though only holes were wanted. That was corrected with a project-local holes-only footprint.

![OLED header model that had to be removed](<Schematics/Journal Images/oled-header-review.png>)

## 2026-08-25 — ESP32 and radio architecture decision

**Portal summary:** `Selected separate Wi-Fi and radio modules`  
**Time:** 0.53 h

I compared ESP32-S3, C3, C6 and classic WROOM options. Native USB on an S3 could remove the CH340C circuit, but the selected S3 assembly classification increased the small-run price. The economical design kept an ESP32-WROOM with PCB antenna and CH340C programming.

Long-range communication moved to a separate Ra-01SH/SX1262 module with an I-PEX antenna socket. This kept Wi-Fi/Bluetooth and the 915 MHz link independent and placed the external-radio connector near the top of the board for enclosure access.

![Cost before adding the final ESP32 choice](<Schematics/Journal Images/jlc-cost-before-esp32.png>)

## 2026-08-25 — WROOM plus radio PCB revision

**Portal summary:** `Integrated the ESP32 and SX1262 radio`  
**Time:** 2.89 h

The ESP32 and radio were added to the same PCB and the ESP32 moved into the open middle region underneath the elevated OLED. The radio stayed near the top. I added SPI, BUSY, DIO1 and RESET connections, local radio bulk capacitance and an antenna-access reference.

During routing I discovered that the generated router constraint section was nested incorrectly, so the router silently used 0.20 mm power traces. I fixed the generator, rerouted with the intended 0.40 mm high-current and 0.30 mm 3.3 V classes, removed dangling branches and returned the board to zero DRC violations.

![Middle-region placement review](<Schematics/Journal Images/middle-layout-review.png>)

## 2026-08-25 — Controls, indicators and battery monitoring

**Portal summary:** `Finished controls and battery monitoring`  
**Time:** 1.17 h

I finalized the 2×2 button group, isolated BTN5, microphone location, top-left potentiometer and external LED connections. Basic red LEDs were used for charging and programmable status so they would not add special tooling fees. The raw battery divider remained on GPIO34, allowing firmware to measure actual cell voltage rather than the regulated output.

The external OLED holes were moved upward and later reversed so the component-side order became `SDA`, `SCL`, `3V3`, `GND`. Diagnostic pads expose power, UART, reset, boot, status/GPIO2 and GPIO12.

![Revision before the final mechanical cleanup](<Schematics/Journal Images/revision-e-bottom.png>)

---

## 2026-08-26 — Final routing and repository setup

**Portal summary:** `Finished routing and organized the repository`  
**Time:** 0.72 h

I finished the difficult USB power and Class-D output routes, added ground stitching and verified that the amplifier return joined the main ground network. The KiCad project, manufacturing files, STEP export and engineering notes were copied into a dedicated Git repository instead of remaining scattered in a working directory.

This session also made the project reproducible: the repository copy was opened and checked independently, and the copied Gerber archive was compared to its source by SHA-256.

![Completed Revision E top view](<Schematics/Journal Images/revision-e-top.png>)

## 2026-08-26 — Mounting holes and mechanical cleanup

**Portal summary:** `Added mounting holes and cleared corners`  
**Time:** 1.71 h

Four 3.2 mm M3 mounting holes were added at the corners. To make space, the radio moved inward and the large battery, switch and speaker wire pads were reduced while retaining enough copper and drill diameter for the expected current and hand wiring.

The solder-pad labels were initially too close together. A vertical-label attempt then crossed solder-mask openings, so the labels were returned to staggered horizontal text on the back silkscreen. The OLED connection was flipped, and GPIO2 plus GPIO12 were exposed near the diagnostic pads.

![Top-corner and mounting-hole review](<Schematics/Journal Images/mounting-layout-review.png>)

## 2026-08-26 — Branding and assembler orientation discovery

**Portal summary:** `Added branding and found the CPL rotation bug`  
**Time:** 0.16 h

I added `Verma Industries` and `ESP32 Walkie Talkie V2` as white back silkscreen for the planned black solder mask. This is ordinary silkscreen artwork and does not require copper engraving.

A JLC preview then showed the ESP32 rotated by 90 degrees with its antenna pointing downward. At this stage I attributed it to JLC's library zero-angle convention and added a U6-specific 90-degree correction. A later real upload showed that diagnosis was incomplete: the CPL and Gerbers used different Y-coordinate origins, and the extra U6 rotation made the preview worse.

![JLC preview showing the incorrect ESP32 rotation](<Schematics/Journal Images/jlc-esp32-orientation-error.png>)

---

## 2026-08-27 — Restored and resumed interrupted work

**Portal summary:** `Recovered the saved PCB work`  
**Time:** 0.16 h

The computer and task session had been interrupted. I verified that the KiCad sources and journal changes had already been saved, restored the project from the repository state and continued from the known-clean routed board instead of rebuilding it from scratch.

![Saved back-side branding and routing](<Schematics/Journal Images/back-branding-layout.png>)

## 2026-08-27 — Production electrical audit

**Portal summary:** `Audited and fixed final electrical issues`  
**Time:** 2.06 h

The pre-production audit found a real voltage-domain problem: CH340C had been powered from USB 5 V while its UART output connected directly to a 3.3 V ESP32 input. I moved CH340C VCC and V3 to switched 3.3 V, preventing a 5 V UART level and reducing off-state phantom-power risk.

I also added the ICS-43432 manufacturer's recommended 100 kΩ data pulldown and corrected the MAX98357A exposed-pad symbol type so the final ERC report could be genuinely warning-free. A first broad reroute created 76 DRC errors, so I discarded it, restored the clean checkpoint and made only surgical route changes. The final result returned to zero violations.

![Final top-side PCB after electrical audit](<Schematics/Journal Images/final-top.png>)

## 2026-08-27 — Final manufacturing release

**Portal summary:** `Built and validated the Final Draft release`  
**Time:** 0.11 h

I generated a locked Final Draft package from the corrected KiCad files. The build produced matched Gerbers, BOM, raw CPL, JLC-corrected CPL, schematic PDF, PCB renders, ERC/DRC reports and SHA-256 checksums.

The independent release validator confirmed a 45 × 100 mm two-layer outline, four M3 holes, 64 installed references in both BOM and CPL, exact Gerber/drill contents, zero ERC warnings/errors and zero DRC violations/unconnected pads. The later JLC upload review superseded the original 180-degree U6 assumption; the corrected native row is documented in the 2026-08-29 entry.

![Final isometric PCB render](<Schematics/Journal Images/final-isometric.png>)

## 2026-08-27 — Hack Club shipping documentation draft

**Portal summary:** `Organized the Hack Club submission files`  
**Time:** 0.52 h

I reorganized the public-facing documentation around Hack Club's shipping checklist: a root readme with motivation, usage, design views, build steps and BOM; a root CSV BOM; an assembly guide; a submission checklist; and this dated image-backed journal. Historical working documents remain local and ignored, while the journal's required images are tracked under `Schematics/Journal Images/`.

This check also identified two honest blockers rather than hiding them: the current STEP file is a PCB export rather than a full enclosure assembly, and the application firmware has not been implemented. Both must be completed before representing the project as a finished Blueprint submission.

![Final PCB back and silkscreen](<Schematics/Journal Images/final-bottom.png>)

## 2026-08-29 — Fixed JLC placement origin and USB-C mechanical model

**Portal summary:** `Matched CPL coordinates to Gerbers and verified USB overhang`  
**Time:** 1.00 h

A real JLCPCB BOM/CPL upload triggered automatic alignment and produced visibly wrong placements. I compared the files numerically and found the Gerber outline at `X = 0…45`, `Y = 0…-100 mm`, while the release CPL had independently flipped every Y coordinate positive. This was the root of the global offset. The previous U6-only +90-degree workaround also made the ESP32 face downward in the new preview.

I changed the release generator to preserve KiCad's native negative-Y coordinates and native rotations. U6 is now `(16.000, -49.500)`, top, 90 degrees; J1 is `(22.500, -95.850)`. Automated validation rejects future CPL rows outside the exact Gerber coordinate bounds, preventing this mismatch from returning.

The USB-C concern exposed a second mistake. The earlier Fusion STEP used a similar GCT connector because KiCad's HRO model filename was unavailable. It was unsuitable for enclosure decisions. I obtained the exact C165948 / TYPE-C-31-M-12 STEP model, made it project-local and rendered it against the real footprint. The exact shell already extends beyond the PCB edge for cable insertion, so I did not disturb the routed footprint or USB differential pair.

The lesson was to treat real assembler previews as evidence, not merely a renderer quirk: CPL coordinates must remain in the Gerber coordinate system, and mechanical clearance must be checked with the exact purchased component model.

## 2026-08-29 — Repository cleanup and real external-parts BOM

**Portal summary:** `Normalized repository names and added purchase-pack pricing`  
**Time:** 0.75 h

I renamed the public root files to `readme.md`, `journal.md`, and `bom.csv`, then updated the release generator and internal links. The bulky local `docs/` history and `Schematics/Legacy/` checkpoint were added to `.gitignore` and removed only from Git's index, not from the computer. Since ignoring `docs/` would otherwise break the journal images on GitHub, the submission-relevant PNG files were copied into the tracked `Schematics/Journal Images/` folder.

The placeholder purchasing estimate was replaced with the actual pack prices supplied for OLEDs, 2000 mAh batteries, long and short 915 MHz antennas, and tactile buttons. Every pack now shows its per-piece calculation. A single walkie uses one OLED at $1.766, one battery at $4.15, five buttons at $0.128 total, and one antenna. Averaging the $2.88 long and $1.57 short antenna choices gives $2.225, making the known non-PCB subtotal $8.269. The complete cost deliberately remains N/A until the PCBA quote, speaker, potentiometer, switch, LED, wiring, hardware, and enclosure prices are known.

## 2026-08-29 — CAD extraction and Git LFS cleanup

**Portal summary:** `Made the large CAD assembly GitHub-safe and separated printable parts`  
**Time:** 1.00 h

The full Fusion assembly had grown to 126.5 MB, beyond GitHub's ordinary 100 MB file limit. I configured repository-local Git LFS tracking for Fusion archives and assembly STEP files, installed the repository pre-push hook, and staged both the native `.f3z` assembly and the 22 MB assembly STEP as LFS pointers. This preserves the editable assembly without shrinking or splitting it manually.

The assembly STEP contained exact named `MANIFOLD_SOLID_BREP` solids matching the printable STL names: `Button Pad`, `Button Press`, `Case Bottom`, and `Case Lid`. I extracted each native solid and its dependency graph into a standalone STEP file, then checked that every output had one product, one solid, a valid STEP terminator, and no dangling entity references. This avoided converting the triangular STL meshes back into low-quality faceted solids.

I also removed the redundant `Schematics/Final Draft/` copy, KiCad prose notes/reports, Gerber-folder readmes/reports, and stale PCB render snapshots from Git's index while leaving every local file untouched. The active KiCad schematic, PCB, project tables, custom footprints, 3D models, engineering BOMs, and the explicitly useful `audit-plots/` reference folder remain tracked.

## Current next steps

1. Design the complete enclosure and export both its editable source and a full-assembly STEP file.
2. Write and test the ESP32 voice firmware, including audio buffering, codec, SX1262 packet transport and push-to-talk behavior.
3. Order the smallest PCBA batch and complete the first-power-up checklist.
4. Record real photos of assembly, enclosure fit, RF testing and failures in new journal entries.
5. Replace this reconstructed wording with the author's own account before Hack Club submission.
