# Final electrical and PCB verification

Checked with **KiCad 10** on **2026-08-27** for the order-candidate Final Draft.

## Machine-check results

- ERC: **0 errors, 0 warnings**.
- PCB DRC: **0 violations**.
- Required unconnected pads: **0**.
- Footprint errors: **0**.
- BOM/CPL parity: **64 installed references in both files**.

The earlier MAX98357A warning was not suppressed. Its exposed pad pin 17 was correctly retyped as a power input in the embedded schematic symbol; it remains connected to GND as required.

## Corrections made during the final audit

- CH340C VCC and V3 now both use the switched regulated `3V3` rail. This prevents a 5 V UART output from reaching the ESP32 and prevents USB from back-powering the switched-off controller. The main power switch must be ON while programming.
- R26, 100 kΩ, now pulls `MIC_DATA` to GND as recommended for the ICS-43432 SD output when it is tri-stated.
- The PCB was updated for both changes, the affected routes were rebuilt, the ground zone was refilled, and native KiCad ERC/DRC were rerun.
- U6's JLC CPL value has a deliberate +90° library-datum correction. The released CPL lists U6 at 180° so the ESP32 antenna faces the **left** edge in JLC's assembly preview.

## Verified electrical architecture

- ESP32-WROOM-32D-N16 is powered by regulated `3V3`; EN has a 10 kΩ pull-up and 1 µF startup capacitor.
- CH340C runs at 3.3 V and DTR/RTS drives the standard two-transistor EN/GPIO0 automatic-programming network.
- USB-C has independent 5.1 kΩ CC1/CC2 sink resistors. D+/D− pass through USBLC6-2SC6 and 22 Ω series resistors.
- TP4056 charges the protected 1S cell at approximately 500 mA and remains powered from USB even when the main switch is off.
- DW01A and FS8205A provide low-side cell protection; `BAT_SENSE` measures raw `BAT_CELL`, not the regulated rail.
- The TPS63021 fixed 3.3 V buck-boost has 2 × 10 µF input, 100 nF VINA bypass, 2.2 µH inductor, and 3 × 22 µF output support.
- Ra-01SH uses regulated `3V3`, SPI, BUSY, DIO1, and RESET. TXEN, RXEN, DIO2, and DIO3 are intentionally unused for this module/application.
- ICS-43432 has local 100 nF bypass, grounded L/R select, shared I2S WS/BCLK, and the new 100 kΩ SD pull-down.
- MAX98357A stays on `SYS_SW` with 10 µF + 1 µF + 100 nF local bypassing. Its speaker output is differential; neither output is GND.
- The external OLED interface is exactly GND/3V3/SCL/SDA with 4.7 kΩ I2C pull-ups to 3V3.
- Buttons switch their GPIOs to GND and require firmware pull-ups.
- All deliberately unused IC/module pins are explicit no-connects.

Final reports are in `Final Draft/Audit/walkiepcb_final_erc.rpt` and `walkiepcb_final_drc.rpt`.
