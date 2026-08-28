# ERC and PCB connectivity verification — Revision D

Checked with **KiCad 10** on **2026-08-26**.

## Machine-check results

- ERC: **0 errors, 1 warning**.
- PCB DRC: **0 violations**.
- Required unconnected pads: **0**.
- Footprint errors: **0**.

The only ERC warning comes from KiCad's stock `Audio:MAX98357A` symbol. Exposed pad pin 17 is typed `Unspecified` while the connected GND pins are `Power input`. Pin 17 is intentionally grounded as required by the part. The warning is retained visibly instead of suppressing the entire ERC category.

## Verified electrical architecture

- ESP32-WROOM-32D-N16 is powered by regulated `3V3` and uses its edge-facing PCB antenna.
- CH340C is powered only from `USB_5V`; DTR/RTS drives the standard two-transistor EN/GPIO0 automatic-program circuit.
- USB-C is a 5.1 kΩ CC sink/device. D+/D− pass through USBLC6-2SC6 and 22 Ω series resistors to CH340C.
- Ra-01SH is powered from `3V3`, uses SPI plus BUSY/DIO1/RESET, and exposes its on-module I-PEX antenna socket.
- TPS63021 VIN/VINA/EN use `SYS_SW`; fixed output is `3V3`; PS/SYNC is grounded; FB is tied to VOUT.
- TPS63021 support is 2.2 µH, 2 × 10 µF input, 100 nF VINA bypass, and 3 × 22 µF output.
- ESP32, Ra-01SH, ICS-43432, OLED header, I2C pull-ups, and logic use regulated `3V3`.
- MAX98357A remains on raw `SYS_SW` with local 10 µF + 1 µF + 100 nF bypassing.
- `BAT_SENSE` measures raw `BAT_CELL` through 100 kΩ/100 kΩ and 100 nF. It does not measure regulated 3V3.
- J7 provides only GND/3V3/SCL/SDA for a commercial SSD1306 module.
- D2 is an ESP32 status LED; D3 is connected to TP4056 `/CHRG` and lights while charging.
- DW01A, FS8205A, USB ESD, and resettable fuse remain installed in this safety-preserving revision.
- All intentional unused IC/module pins are explicit no-connects.

Final reports: `walkiepcb_erc.rpt` and `walkiepcb_drc.rpt`.
