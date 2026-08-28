# Order-readiness report — Final Draft

Audit date: **2026-08-27**  
Target service: **JLCPCB Economic PCBA**  
Board: **45.000 mm × 100.000 mm, two copper layers**

## Disposition

The design is ready to upload as a **prototype order candidate**. All discovered schematic and PCB faults were corrected, manufacturing files were regenerated from the corrected KiCad source, and machine validation is clean.

This is not a claim that an unbuilt mixed-signal/RF design is guaranteed to work perfectly on its first physical build. ERC/DRC cannot validate solder quality, enclosure acoustics, antenna performance, battery quality, firmware, thermal behavior, or JLC's final feeder rotation. Order a small first run and complete the bring-up checklist before committing to a larger quantity.

## Final corrections

| Finding | Risk | Final correction |
|---|---|---|
| ESP32 looked 90° wrong in JLC preview | Module antenna could face downward and violate RF clearance | Final CPL applies U6-specific +90° datum correction; U6 is `180°` at `(16.000, 49.500)` |
| CH340C originally ran from USB 5 V | 5 V UART level into a 3.3 V ESP32 and possible off-state phantom power | CH340C VCC and V3 tied to switched `3V3`; C30 retained as 100 nF bypass |
| ICS-43432 SD line lacked its recommended pull-down | Floating `MIC_DATA` when the microphone output is tri-stated | Added R26, 100 kΩ to GND, JLC Basic C25741 |
| MAX98357A exposed pad was typed `Unspecified` | Persistent ERC warning hid the difference between a real warning and a library issue | Pin 17 retyped as a grounded power input; ERC is now fully clean |
| First reroute attempt caused many DRC errors | Late edits could have damaged a previously clean board | Restored the preserved pre-audit PCB and rerouted only the affected nets; final DRC is zero |

## Schematic review result

| Subsystem | Result |
|---|---|
| USB-C and programming | Correct 5.1 kΩ CC resistors, ESD, 22 Ω USB series resistors, 3.3 V CH340C, DTR/RTS auto-program network |
| Battery charging/protection | TP4056 1S charger, approximately 500 mA program current, DW01A + FS8205A protection, protected system ground |
| Power-path and regulation | USB/battery source selection, resettable fuse, external series switch, TPS63021 fixed 3.3 V buck-boost |
| Battery measurement | GPIO34 reads half of raw cell voltage through 100 kΩ/100 kΩ with 100 nF filtering |
| Controller | ESP32-WROOM-32D-N16 at 3.3 V with EN/boot support and left-edge PCB-antenna keepout |
| Long-range radio | Ra-01SH/SX1262 at 3.3 V with SPI, BUSY, DIO1, RESET, local 44 µF + 100 nF bypass, and I-PEX antenna |
| Microphone | ICS-43432 I2S, bottom acoustic port, local bypass, grounded channel select, 100 kΩ SD pull-down |
| Speaker path | MAX98357A on `SYS_SW`, local bulk/HF bypass, GPIO-controlled shutdown, differential speaker pads |
| OLED and controls | Four bare OLED holes with 3.3 V I2C, five active-low buttons, potentiometer ADC, charge/status LEDs |

## Manufacturing validation

- ERC: **0 errors, 0 warnings**.
- DRC: **0 violations, 0 unconnected pads**.
- BOM: **64 installed references**, 32 grouped lines.
- CPL: **64 installed references**, exact parity with BOM.
- Basic: **51 placements across 19 grouped BOM lines**.
- Extended: **13 placements across 13 grouped BOM lines**.
- JLC/LCSC code: present on every installed BOM line.
- Gerbers: front/back copper, solder mask, silkscreen, paste, Edge.Cuts, PTH drill, and NPTH drill.
- Board outline: closed 45 × 100 mm rectangle; four 3.2 mm NPTH M3 mounting holes.
- OLED top reference: Y = 50.000 mm, satisfying `OLED_TOP >= 47.5 mm`.

## Mandatory checks in the JLC uploader

1. Select **2 layers**, 45 × 100 mm, and the intended black solder mask.
2. Use the Gerber ZIP, JLC BOM, and **corrected** JLC CPL from the same `Final Draft/Manufacturing` folder.
3. Confirm U6's ESP32 PCB antenna faces the **left board edge**, never downward.
4. Confirm U8 occupies the top radio footprint and its I-PEX connector is visible on the board-interior/lower side of the module, matching the supplied top render.
5. Confirm U2 pin-1 dot, U3 pin-1 mark, U5 pin-1 mark, U7 pin-1 mark, Q3 orientation, and MK1 acoustic-port orientation match the assembly drawing/PCB pads.
6. Do not accept an automatic part substitute merely because the package looks similar. Pinout, exact MPN, voltage, and exposed-pad layout must match.
7. Recheck live availability for every Extended line, particularly U6, U8, U5, U7, MK1, and U2. Inventory can change after this audit.

## Known prototype risks

- ESP32-WROOM-32D-N16 is an older/NRND module but was retained because the selected JLC code is Economic-compatible and available for this prototype.
- ICS-43432 is an older/EOL microphone with finite stock. If unavailable, a substitute requires a schematic, footprint, acoustic-port, and I2S timing review.
- Real-time voice requires firmware: packetized GFSK/FSK plus a low-rate codec and packet-loss handling. LoRa mode itself is not suitable for ordinary continuous voice.
- Speaker/microphone echo, regulator noise, RF range, TP4056 temperature, and low-cell transient behavior require measurement on assembled hardware.
- The main switch must be ON for CH340C programming. USB charging remains available with it OFF.
- Connect a suitable 915 MHz antenna before radio transmission and obey local frequency/power rules.

Use `FIRST_POWER_UP_CHECKLIST.md` for the first assembled board.
