# ESP32-WROOM and radio pin assignments — Revision E

Controller: **ESP32-WROOM-32D-N16**, JLC **C529578**, powered from the fixed 3.3 V TPS63021 rail. The ESP32 uses its onboard 2.4 GHz PCB antenna. Long-range voice data uses the separate **Ra-01SH / SX1262 915 MHz** module and its I-PEX/U.FL-compatible antenna socket.

| ESP32 GPIO | Module pin | Net | Function / notes |
|---:|---:|---|---|
| GPIO36 / SENSOR_VP | 4 | `RADIO_BUSY` | Input-only; SX1262 BUSY |
| GPIO39 / SENSOR_VN | 5 | `RADIO_DIO1` | Input-only; SX1262 interrupt |
| GPIO34 / ADC1_CH6 | 6 | `BAT_SENSE` | Raw-cell 100 kΩ/100 kΩ divider plus 100 nF filter |
| GPIO35 / ADC1_CH7 | 7 | `POT_ADC` | Potentiometer wiper plus 100 nF filter |
| GPIO32 | 8 | `BTN5` | Isolated fifth button; firmware pull-up |
| GPIO33 | 9 | `MIC_DATA` | ICS-43432 I2S data into ESP32 |
| GPIO25 | 10 | `I2S_WS` | Shared microphone/amplifier word select |
| GPIO26 | 11 | `I2S_BCLK` | Shared microphone/amplifier bit clock |
| GPIO27 | 12 | `BTN4` | Firmware pull-up; switch to GND |
| GPIO14 | 13 | `OLED_SCL` | SSD1306 I2C clock; 4.7 kΩ pull-up |
| GPIO12 | 14 | `GPIO12` | Optional expansion pad TP8; boot strapping pin, use cautiously |
| GPIO13 | 16 | `BTN2` | Firmware pull-up; switch to GND |
| GPIO15 | 23 | `AMP_ENABLE` | Controls MAX98357A shutdown/mode network |
| GPIO2 | 24 | `LED_STATUS` | Drives D2 through 330 Ω and expansion pad TP7; also an ESP32 strapping pin |
| GPIO0 | 25 | `GPIO0` | Boot strap and CH340C auto-programming |
| GPIO4 | 26 | `BTN1` | Firmware pull-up; switch to GND |
| GPIO16 | 27 | `BTN3` | Firmware pull-up; switch to GND |
| GPIO17 | 28 | `RADIO_RST` | SX1262 reset |
| GPIO5 | 29 | `RADIO_NSS` | SX1262 SPI chip select; also an ESP32 strapping pin |
| GPIO18 | 30 | `RADIO_SCK` | SX1262 SPI clock |
| GPIO19 | 31 | `RADIO_MISO` | SX1262 SPI MISO |
| GPIO21 | 33 | `OLED_SDA` | SSD1306 I2C data; 4.7 kΩ pull-up |
| GPIO3 / RXD0 | 34 | `UART_RX` | From CH340C TXD; test pad TP4 |
| GPIO1 / TXD0 | 35 | `UART_TX` | To CH340C RXD; test pad TP3 |
| GPIO22 | 36 | `AMP_DATA` | I2S audio data to MAX98357A |
| GPIO23 | 37 | `RADIO_MOSI` | SX1262 SPI MOSI |

Module pins 1, 15, 38, and 39 are GND; pin 2 is 3V3; pin 3 is EN. GPIO12 is now physically exposed at TP8 but otherwise unloaded because it is a flash-voltage strapping pin. The module's flash-interface pins are explicit no-connects.

## Ra-01SH interface

| Ra-01SH pin | Net | Function |
|---:|---|---|
| 3 | `3V3` | Regulated supply |
| 2, 9, 16 | `GND` | Module ground |
| 4 | `RADIO_RST` | Reset |
| 6 | `RADIO_DIO1` | Interrupt |
| 10 | `RADIO_BUSY` | Busy indication |
| 12 | `RADIO_SCK` | SPI clock |
| 13 | `RADIO_MISO` | SPI MISO |
| 14 | `RADIO_MOSI` | SPI MOSI |
| 15 | `RADIO_NSS` | SPI chip select |

The module's unused control/castellated antenna pins are explicit no-connects because the selected Ra-01SH uses its on-module I-PEX socket.

## Firmware notes

- Configure BTN1–BTN5 with internal pull-ups.
- Keep the amplifier disabled until I2S clocks are stable.
- Initialize the purchased SSD1306 I2C module at its actual address, commonly `0x3C`.
- CH340C DTR/RTS drives the standard two-transistor EN/GPIO0 automatic-programming circuit. CH340C VCC and V3 are on switched `3V3`, so turn the main switch ON for USB programming.
- `MIC_DATA` has an external 100 kΩ pull-down (R26) so the line is defined when the ICS-43432 output is tri-stated.
- `BAT_SENSE` is half the raw cell voltage: a 4.2 V cell is approximately 2.1 V at GPIO34. Calibrate in firmware.
- For real-time voice over SX1262, use packetized GFSK/FSK and a low-bit-rate codec. LoRa modulation is intended for range and telemetry, not continuous high-quality voice streaming.
- GPIO2, GPIO5, and GPIO12 are boot strapping pins. TP7 shares GPIO2 with the status LED, so attached hardware and the LED are driven together. Do not attach hardware that forces an invalid startup level or exceeds the ESP32 GPIO current/voltage limits.
