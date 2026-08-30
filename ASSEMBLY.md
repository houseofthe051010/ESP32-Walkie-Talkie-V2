# Assembly plan

This document covers the off-board parts that are not installed by JLCPCB. It does not replace the schematic or the first-power-up procedure.

## Before assembly

1. Order only the matched Final Draft Gerber, BOM and corrected CPL set.
2. Verify all component rotations in the JLC preview, especially the ESP32 antenna direction.
3. Bring up one bare PCBA with a current-limited bench supply before attaching the battery, speaker, or external controls.
4. Do not attach a LiPo, speaker or RF antenna until the power rails and shorts have been checked.

## Off-board wiring

| PCB connection | External part | Wiring |
|---|---|---|
| `BAT_CELL`, `CELL_NEG` | Protected 1S LiPo | Battery positive to `BAT_CELL`; negative to `CELL_NEG`. Confirm polarity before soldering. |
| `SW_PWR_IN`, `SW_PWR_OUT` | SPST power switch | Two wires only. The external switch is in series with the system supply. |
| `SPK+`, `SPK-` | 4–8 Ω speaker | Differential output. Do not connect either speaker lead to ground. |
| `3V3`, `POT_ADC`, `GND` | 10 kΩ linear potentiometer | Ends to 3V3/GND and wiper to `POT_ADC`. |
| `LED+`, `LED-` | External 5 mm LED | Observe LED polarity. The current-limiting resistor is on the PCB. |
| `SDA`, `SCL`, `3V3`, `GND` | SSD1306 I2C OLED | Read the PCB labels and OLED labels individually; wire by signal name, not assumed module order. |
| Ra-01SH I-PEX | 915 MHz antenna | Snap the matching micro-coax connector straight down without twisting. Never transmit without the antenna. |

## Mechanical assembly

- Secure the PCB through its four 3.2 mm M3 holes using non-conductive spacers where needed.
- Mount the 40 mm speaker above the upper PCB region without allowing its basket or magnet to touch components.
- Support the OLED above the PCB so its wiring cannot pull on the plated holes.
- Keep the antenna and coax away from the speaker magnet, battery and sharp enclosure edges.
- Secure the battery against puncture, crushing and movement. Do not rely on soldered wires as mechanical restraint.
- Provide access to USB-C, the power switch and the radio antenna connector.
- Confirm the microphone acoustic hole is unobstructed and not sealed by adhesive or enclosure plastic.

The complete enclosure CAD is still pending. Final spacer heights, speaker clearance and battery retention must be established in that model before ordering enclosure parts.

## Software and testing sequence

1. Flash hardware-diagnostic firmware with the main switch on.
2. Verify battery ADC, buttons, status LED and OLED.
3. Record microphone samples with the amplifier and radio disabled.
4. Test speaker playback at low volume.
5. Attach the correct antenna and test SX1262 register access at low RF power.
6. Test packetized data before attempting compressed voice.
7. Measure the 3.3 V rail during simultaneous ESP32, radio and audio activity.
8. Only then install the board and battery in the enclosure.
