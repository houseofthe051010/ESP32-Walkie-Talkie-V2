# ESP32 Walkie Talkie V2

ESP32 Walkie Talkie V2 is a custom handheld digital voice-radio board. It combines an ESP32, a dedicated 915 MHz SX1262 radio, digital microphone, Class-D speaker amplifier, battery charging, battery monitoring, USB-C programming, controls, and an external OLED connection on one 45 × 100 mm PCB.

The goal is to build a pair of rechargeable handheld radios that can exchange compressed voice without depending on Wi-Fi, cellular service, or an internet connection. The separate sub-GHz radio provides the long-range link while the ESP32 handles audio capture, compression, controls, display updates, and packet management.

> [!IMPORTANT]
> **Current status: production-candidate PCB design, not a completed physical build.** The PCB has passed ERC/DRC and manufacturing-file validation, but the enclosure and application firmware are not finished and no assembled prototype has been bench-tested yet. See [Hack Club submission status](HACK_CLUB_SUBMISSION.md) before submitting this repository for funding.

## Why this project exists

The project started as an attempt to make a longer-range, customizable alternative to a Wi-Fi-only ESP32 intercom. Designing the complete board also made it possible to choose the controls, audio path, battery monitoring and enclosure geometry instead of stacking several development boards together. A major part of the design process became learning how electrical choices affect real small-run assembly cost, stock availability, mechanical fit and manufacturability.

## What it does

- Captures digital audio with an ICS-43432 I2S microphone.
- Uses the ESP32 to process and eventually compress voice audio.
- Sends packetized audio over an Ai-Thinker Ra-01SH/SX1262 915 MHz radio.
- Drives a 4–8 Ω speaker through a MAX98357A I2S Class-D amplifier.
- Displays channel, battery, and radio state on a hand-wired SSD1306 I2C OLED.
- Provides five buttons, a potentiometer input, status LED, charging LED, and battery-voltage monitoring.
- Charges a single-cell Li-ion/LiPo battery through USB-C.

The intended voice mode is SX1262 GFSK/FSK with a low-rate codec and packet-loss handling. Ordinary LoRa modulation is useful for low-rate telemetry, but it does not provide enough continuous bandwidth for normal real-time voice.

## Hardware

| Subsystem | Part | Purpose |
|---|---|---|
| Controller | ESP32-WROOM-32D-N16 | Audio processing, controls, display and packet handling |
| Long-range radio | Ai-Thinker Ra-01SH / SX1262 | 803–930 MHz radio with I-PEX/U.FL-compatible antenna socket |
| Microphone | ICS-43432 | Bottom-port I2S digital microphone |
| Speaker amplifier | MAX98357A | I2S Class-D differential speaker output |
| Power regulator | TPS63021 | Fixed 3.3 V synchronous buck-boost supply |
| Charger | TP4056 | Approximately 500 mA single-cell Li-ion charging |
| Battery protection | DW01A + FS8205A | Cell overcharge, overdischarge and fault protection |
| USB programming | CH340C | USB-to-UART with automatic boot/reset control |
| Display | External SSD1306 module | Four hand-wired I2C holes: `SDA`, `SCL`, `3V3`, `GND` |

The KiCad board is exactly **45.000 × 100.000 mm**, uses **two copper layers**, and includes four 3.2 mm M3 mounting holes. The OLED is mounted above the main PCB on wires or spacers, and the enclosure-mounted 40 mm speaker sits over the upper component region with its Z-clearance checked during enclosure design.

The repository contains a [PCB STEP export](<Schematics/Mechanical/walkiepcb_final_exact_usb.step>) under `Schematics`. Current-design PCB render snapshots are intentionally excluded from Git so that they cannot be mistaken for the latest editable KiCad revision.

## How the system connects

```text
Li-ion cell -> charger/protection -> power switch -> 3.3 V buck-boost -> ESP32
                                                       |            |
                                                       |            +-> OLED / controls
                                                       +-> microphone / SX1262 radio

Li-ion switched rail -------------------------------------> MAX98357A -> speaker
USB-C -> charging
USB-C -> CH340C -> ESP32 programming UART
Ra-01SH I-PEX socket -> tuned 915 MHz antenna
```

The full circuit is documented by the editable [KiCad schematic](<Schematics/KiCad Project/walkiepcb.kicad_sch>). Off-board wiring and mechanical assembly are described in [ASSEMBLY.md](ASSEMBLY.md).

## Intended use

Once the firmware is implemented, a user will charge each handset through USB-C, attach the correct 915 MHz antenna, turn on the side power switch, select a channel with the controls, and hold the push-to-talk button while speaking. The receiving handset will decode the packets and play the voice through its speaker.

The main switch must be on for USB programming because the CH340C intentionally runs from switched 3.3 V. Charging remains available while the switch is off. Never transmit without an antenna, and use only frequencies and power levels permitted in the operating region.

## Building the project

1. Order the matched Gerber, BOM and corrected CPL files from `Schematics/Gerber, BOM, CPL files for JLBPCB/`.
2. In the assembler preview, confirm that the ESP32 antenna faces the left board edge and the Ra-01SH matches the supplied render.
3. Inspect and electrically bring up one board carefully before connecting the battery or speaker.
4. Hand-solder the OLED, five buttons, potentiometer, speaker, battery, external LED and power switch according to [ASSEMBLY.md](ASSEMBLY.md).
5. Design and print/machine an enclosure that secures the PCB, speaker, battery, display, antenna cable and controls.
6. Flash and test the application firmware before installing the battery permanently.

The editable source is in `Schematics/KiCad Project/`, and the current manufacturing exports are in `Schematics/Gerber, BOM, CPL files for JLBPCB/`. Generated reports and redundant final-draft snapshots are kept locally but intentionally excluded from Git.

## Repository map

- [`Schematics/KiCad Project`](<Schematics/KiCad Project>) — editable KiCad schematic, PCB, libraries, 3D models, audit plots, and engineering BOMs
- [`Schematics/Gerber, BOM, CPL files for JLBPCB`](<Schematics/Gerber, BOM, CPL files for JLBPCB>) — fabrication Gerbers, BOM, and CPL
- [`Schematics/Mechanical`](<Schematics/Mechanical>) — PCB-generated STEP export using the exact USB-C model
- [`Firmware`](Firmware) — firmware status and planned architecture
- [`journal.md`](journal.md) — dated Hack Club-style build journal
- [`Schematics/Journal Images`](<Schematics/Journal Images>) — tracked build-history images used by the journal
- [`bom.csv`](bom.csv) — root project-level funding BOM
- [`ASSEMBLY.md`](ASSEMBLY.md) — off-board wiring and build plan
- [`HACK_CLUB_SUBMISSION.md`](HACK_CLUB_SUBMISSION.md) — submission checklist and known blockers

## Project BOM

The table is normalized to **one walkie-talkie**. Pack prices are the supplied checkout prices and exclude shipping and tax. The PCBA is deliberately represented as one object with an unknown price; the [engineering BOM](<Schematics/KiCad Project/walkiepcb_bom_full.csv>) remains the component-level assembly list.

| Item | Qty/walkie | Pack | Pack price | Per piece | Cost/walkie | Source / note |
|---|---:|---:|---:|---:|---:|---|
| Assembled walkie-talkie PCB | 1 | 1 | N/A | N/A | **N/A** | PCBA quote pending; use the matched fabrication files under `Schematics` |
| 0.96-inch SSD1306 I2C OLED | 1 | 5 | $8.83 | $1.7660 | $1.7660 | [AliExpress OLED](https://www.aliexpress.us/item/3256805954920554.html); verify the selected four-pin I2C variant and pin order |
| 804050 2000 mAh 3.7 V LiPo | 1 | 4 | $16.60 | $4.1500 | $4.1500 | [AliExpress battery pack](https://www.aliexpress.us/item/3256812605593313.html); verify dimensions, polarity, discharge capability and protection |
| Long 915 MHz antenna option, 20 cm, claimed 5 dBi | 1 | 2 | $5.76 | $2.8800 | Option | [AliExpress long antenna](https://www.aliexpress.us/item/3256808481689716.html) |
| Short 915 MHz antenna option, 6 cm, claimed 2 dBi | 1 | 2 | $3.14 | $1.5700 | Option | [AliExpress short antenna](https://www.aliexpress.us/item/3256810442579041.html) |
| Antenna allowance used for estimating | 1 | — | — | $2.2250 average | $2.2250 | Average of the long and short antenna unit prices; only one antenna is installed |
| 6 × 6 × 5 mm tactile push button | 5 | 50 | $1.28 | $0.0256 | $0.1280 | [AliExpress button pack](https://www.aliexpress.us/item/3256805859865632.html) |
| 40 mm, 4–8 Ω speaker | 1 | TBD | TBD | TBD | TBD | Source pending |
| 10 kΩ linear potentiometer | 1 | TBD | TBD | TBD | TBD | Source pending |
| SPST power switch rated above 2 A DC | 1 | TBD | TBD | TBD | TBD | Source pending |
| 5 mm external LED | 1 | TBD | TBD | TBD | TBD | Source pending; PCB includes its series resistor |
| Wire, heat-shrink, M3 hardware and enclosure | 1 set | TBD | TBD | TBD | TBD | Mechanical purchasing pending |
| **Known subtotal excluding PCB and unresolved items** |  |  |  |  | **$8.2690** | Uses the average antenna allowance |
| **Complete cost per walkie-talkie** |  |  |  |  | **N/A** | Awaiting the PCBA quote and remaining external-part prices |

Buying every listed AliExpress pack costs **$35.61 before shipping and tax**. The limiting four-battery/four-antenna quantities cover four complete handsets; the fifth OLED and remaining buttons are spares unless more batteries and antennas are purchased.
