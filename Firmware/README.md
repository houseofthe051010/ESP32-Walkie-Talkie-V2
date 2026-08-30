# Firmware status

Application firmware has **not been implemented yet**. This directory is intentionally honest rather than containing a blink sketch presented as finished walkie-talkie firmware.

The planned firmware needs to provide:

1. ESP32 peripheral initialization and power-state handling.
2. Button scanning, potentiometer input, battery ADC calibration and SSD1306 UI.
3. I2S microphone capture from the ICS-43432.
4. Low-rate voice encoding and jitter-buffered decoding.
5. SX1262 GFSK/FSK packet transport using SPI, BUSY, DIO1 and RESET.
6. Push-to-talk arbitration, channel selection, sequence numbers, packet-loss handling and timeouts.
7. I2S speaker playback through MAX98357A with controlled amplifier enable.
8. Low-battery warnings and graceful shutdown behavior.

The authoritative electrical pin mapping is the editable [KiCad schematic](<../Schematics/KiCad Project/walkiepcb.kicad_sch>). Firmware must be added and tested before this project is represented as a completed Hack Club shipment.
