# ESP32 Walkie Talkie V2

ESP32-based handheld digital walkie-talkie hardware with a dedicated 915 MHz long-range radio, digital microphone, Class-D speaker amplifier, USB-C charging/programming, battery monitoring, and support for an external SSD1306 OLED.

The current hardware is the **Final Draft (2026-08-27)** derived from Revision E. The PCB is a two-layer, 45 × 100 mm board designed around an ESP32-WROOM-32D-N16 and an Ai-Thinker Ra-01SH/SX1262 radio with an I-PEX/U.FL-compatible external-antenna connector.

## Hardware features

- ESP32-WROOM-32D-N16 with onboard 2.4 GHz PCB antenna
- Ra-01SH / SX1262 915 MHz radio with external-antenna connector
- CH340C USB-to-UART programming with automatic EN/GPIO0 control
- USB-C charging and programming
- TP4056 single-cell Li-ion charger
- TPS63021 fixed 3.3 V synchronous buck-boost supply
- Raw battery-voltage measurement on GPIO34
- ICS-43432 digital I2S microphone
- MAX98357A I2S Class-D speaker amplifier
- Four-hole I2C interface for an external SSD1306 OLED module
- Five-button input arrangement
- Potentiometer and external LED connections
- Charge and programmable status LEDs
- Four M3 mounting holes
- Back-side solder-pad labels and `Verma Industries` branding

## Repository layout

- [`Schematics/KiCad Project`](<Schematics/KiCad Project>) — editable KiCad schematic, routed PCB, project libraries, engineering BOM, and design notes
- [`Schematics/Final Draft`](<Schematics/Final Draft>) — locked order-candidate KiCad source, matching Gerbers/BOM/CPL, audit reports, and renders
- [`Schematics/Gerber, BOM, CPL files for JLBPCB`](<Schematics/Gerber, BOM, CPL files for JLBPCB>) — older Revision E exports retained for history; do not mix them with Final Draft files
- [`CAD`](CAD) — PCB STEP model for enclosure development
- [`Firmware`](Firmware) — reserved for walkie-talkie firmware
- [`DESIGN_JOURNAL.md`](DESIGN_JOURNAL.md) — design history and major engineering decisions

## Manufacturing

The `Schematics/Final Draft/Manufacturing` package contains the matching Gerber ZIP, JLCPCB BOM, and corrected component placement file. Before ordering:

1. Upload all three manufacturing files together.
2. Select a **two-layer, 45 × 100 mm PCB**.
3. Select **black solder mask** for the intended appearance; the back silkscreen will print in white.
4. Confirm the JLCPCB assembly preview shows the ESP32 PCB antenna facing the left board edge and the Ra-01SH antenna connector near the top.
5. Recheck live component stock and package mappings before payment.

Latest machine verification: **DRC 0 violations, 0 unconnected pads; ERC 0 errors and 0 warnings; BOM/CPL parity 64/64.**

## Important notes

- The external OLED is hand-soldered. Its component-side left-to-right connection order is `SDA`, `SCL`, `3V3`, `GND`.
- Turn the main switch ON for USB programming; the CH340C intentionally runs from the switched 3.3 V rail. USB charging still works with the switch OFF.
- The speaker output is differential: neither `SPK+` nor `SPK-` is ground.
- The 915 MHz radio requires an appropriate legal-band antenna and firmware settings for the operating region.
- Real-time voice should use compressed, packetized audio with SX1262 GFSK/FSK rather than ordinary LoRa modulation.
- Treat the battery protection circuitry as a safety backup, not a substitute for a suitable protected cell, safe charging practices, and mechanical battery protection.
