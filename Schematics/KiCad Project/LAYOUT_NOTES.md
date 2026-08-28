# Final PCB layout and enclosure coordinates — Revision E WROOM + 915 MHz radio

The finished board is a **45.000 mm × 100.000 mm**, two-copper-layer portrait PCB. The nominal manufacturing outline runs from X = 0 to 45 mm and Y = 0 to 100 mm when viewed from the component/front side. X increases to the right and Y increases downward.

The 40 mm speaker is mounted above the PCB in the enclosure, not soldered to the PCB. Components may occupy its projected X/Y area, but the enclosure must provide enough Z-clearance over those components and their wiring.

## Mechanical coordinates

| Feature | Center X (mm) | Center Y (mm) | Notes |
|---|---:|---:|---|
| 40 mm speaker reference circle | 22.500 | 21.000 | Diameter 40.000 on `Dwgs.User`; not an edge cut |
| OLED active-area enclosure reference | 22.500 | 57.250 | 25.5 × 14.5 mm reference rectangle |
| OLED mechanical/reference top | — | 50.000 | 2.5 mm below the mandatory Y = 47.5 mm limit |
| OLED visible/reference top | — | 50.000 | Final purchased module must be checked against enclosure CAD |
| OLED four-hole row center | 22.500 | 64.000 | J7 pin centers span X = 18.690–26.310 |
| BTN1 / SW1 | 9.000 | 75.000 | Upper-left of 2×2 cluster |
| BTN2 / SW2 | 21.500 | 75.000 | Upper-right of 2×2 cluster |
| BTN3 / SW3 | 9.000 | 87.500 | Lower-left of 2×2 cluster |
| BTN4 / SW4 | 21.500 | 87.500 | Lower-right of 2×2 cluster |
| Four-button cluster center | 15.250 | 81.250 | Symmetric square; 12.500 mm X/Y pitch |
| Microphone acoustic opening | 36.500 | 74.500 | MK1 bottom port / grounded plated opening |
| BTN5 / SW5 | 36.500 | 87.500 | 15.000 mm right of BTN4 |
| USB-C / J1 | 22.500 | 95.850 | Horizontally centered at bottom edge |
| Status LED / D2 | 15.000 | 94.000 | Basic red 0603 near USB-C |
| Charge LED / D3 | 2.000 | 88.000 | Basic red 0603 driven by TP4056 `/CHRG` |
| M3 mounting hole H1 | 4.000 | 4.000 | 3.2 mm NPTH, top-left |
| M3 mounting hole H2 | 41.000 | 4.000 | 3.2 mm NPTH, top-right |
| M3 mounting hole H3 | 4.000 | 96.000 | 3.2 mm NPTH, bottom-left |
| M3 mounting hole H4 | 41.000 | 96.000 | 3.2 mm NPTH, bottom-right |

**Verified: OLED reference top Y = 50.000 mm, therefore OLED TOP ≥ 47.500 mm from the PCB top.** The margin is 2.500 mm. Because the OLED is a separately purchased, elevated module connected to four holes, the enclosure—not the PCB footprint—sets the final glass and visible-area position.

The four-button cluster is square and symmetric. The microphone is directly above BTN5 by 13.000 mm, and BTN5 remains clearly separate from the four-button cluster.

## User wiring and RF placement

- J5, top-left: `3V3`, `POT_ADC`, `GND` at X = 2.000, 4.540, 7.080 mm and Y = 10.000 mm.
- J6, top-left: `LED+`, `LED-` at X = 2.000, 4.540 mm and Y = 16.000 mm.
- J7, OLED, physical left-to-right: `SDA`, `SCL`, `3V3`, `GND` at X = 18.690, 21.230, 23.770, 26.310 mm and Y = 64.000 mm. This is the requested 180° reversal with GND on the right; it remains four bare plated holes with no header 3D model.
- U8 Ra-01SH center: `(28.500, 10.000)`. Its on-module I-PEX/U.FL-compatible socket remains accessible near the top edge; the module was moved inward to clear the top-right mounting corner.
- U6 ESP32-WROOM-32D-N16 center: `(16.000, 49.500)`, rotated 90°. Its PCB antenna faces the left edge with a copper/track/via/zone keepout.
- J2 battery pads: `BAT_CELL` `(14.500,18.000)` and `CELL_NEG` `(18.300,18.000)`.
- J3 switch pads: `SYS_FUSED` `(37.500,70.500)` and `SYS_SW` `(41.300,70.500)`.
- J4 speaker pads: `SPK+` `(37.500,22.500)` and `SPK-` `(41.300,22.500)`. The Class-D output is differential; neither speaker wire is ground.
- J2/J3/J4 use compact 2.6 mm copper pads, 1.2 mm drills, and 3.8 mm pitch. Use properly strain-relieved soldered wire.
- Diagnostic/expansion pads: TP1 3V3 `(10,10)`, TP2 GND `(14,10)`, TP3 UART_TX `(18,10)`, TP4 UART_RX `(10,14)`, TP5 EN `(14,14)`, TP6 GPIO0 `(10,18)`, TP7 LED_STATUS/GPIO2 `(10,6)`, and TP8 GPIO12 `(14,6)`.
- Final-audit microphone pull-down R26 center: `(33.800, 77.300)`, approximately 3.9 mm from MK1 and outside its acoustic opening.
- J2–J7 hand-soldered electrical holes have compact 1.0 mm-high, 0.15 mm-stroke labels on `B.Silkscreen`. They are mirrored for normal reading while viewing/soldering the back of the PCB and are positioned outside solder-mask openings.
- Back branding is centered at X = 22.500 mm: italic `Verma Industries` at Y = 31.500 mm and `ESP32 Walkie Talkie V2` at Y = 35.500 mm, both on `B.Silkscreen` and mirrored for normal back-side reading.

## Noise and power routing

- Buck-boost U5 center `(10.500,25.000)` to microphone separation: approximately **55.9 mm**.
- Inductor L1 center `(10.500,28.500)` to microphone separation: approximately **52.8 mm**.
- Class-D amplifier U7 center `(40.000,27.500)` to microphone separation: approximately **47.1 mm**.
- The TPS63021, inductor, input capacitors, and output bank form a compact upper-left cluster. `BB_SW1` and `BB_SW2` remain short and local.
- The microphone region has no buck-boost switch-node or Class-D output copper immediately around its acoustic opening.
- `BAT_CELL`, `SYS_RAW`, and `SYS_FUSED` use 0.40 mm routing. `SYS_SW` is primarily 0.40 mm with package-clearance necks. `3V3` is primarily 0.30 mm.
- `USB_5V` is primarily 0.40 mm. A short 0.20 mm section passes the external-switch connector at the right edge; J3 uses 3.0 mm copper pads around 1.5 mm drills.
- `SPK+` and `SPK-` are primarily 0.40 mm with short 0.20/0.25 mm TQFN pad escapes.
- B.Cu contains the filled GND plane. C18 has an explicit ground connection routed past the dense amplifier area to C14/main ground.

## Final validation

- ERC: **0 errors, 0 warnings**.
- DRC: **0 violations**.
- Required unconnected pads: **0**.
- USB-C centerline error: **0.000 mm**.
- OLED reference centerline error: **0.000 mm**.
- Copper layers: **2** (`F.Cu` and `B.Cu`).
- Installed BOM/CPL parity: **64 references in each**.
- Corrected JLC CPL U6 position/orientation: `(16.000, 49.500)`, top, **180°**; assembly preview antenna must face left.

Before releasing the enclosure, print `Dwgs.User` 1:1 and verify the actual OLED module outline/pin order, button actuator geometry, microphone gasket and acoustic channel, USB shell depth, speaker magnet height, ESP32 antenna clearance, and I-PEX cable bend radius.
