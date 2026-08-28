# JLC/LCSC part research — Final Draft

Checked **2026-08-27**. Inventory and small-quantity pricing are volatile; the JLC BOM uploader remains the authoritative order-time check. Every selected IC/module currently has a JLC part page that identifies it as compatible with **Economic and Standard** PCBA.

## Main architecture

| Function | Selected part | JLC/LCSC # | Library | Current evidence |
|---|---|---:|---|---|
| Wi-Fi/Bluetooth controller | ESP32-WROOM-32D-N16 | C529578 | Extended | JLC Economic+Standard; 4,024 stock and $4.7979 at qty 1 snapshot |
| 915 MHz radio with I-PEX | Ai-Thinker Ra-01SH / SX1262 | C2764087 | Extended | JLC Economic+Standard; LCSC 1,834 stock and $4.6083 at qty 1 snapshot |
| USB-UART | CH340C | C7464026 | Extended | JLC Economic+Standard page active; exact public JLC stock count not exposed |
| 3.3 V buck-boost | TPS63021DSJR | C202140 | Extended | JLC Economic+Standard; active part page |
| I2S microphone | ICS-43432 | C574021 | Extended | JLC Economic+Standard, high-difficulty; 246 stock and $5.1108 order-time snapshot; older/EOL part |
| I2S Class-D amplifier | MAX98357AETE+T | C910544 | Extended | JLC Economic+Standard; LCSC 15,399 stock and $1.3247 snapshot |

Links: [ESP32-WROOM-32D-N16](https://jlcpcb.com/partdetail/ESP32-WROOM-32D-N16/C529578), [Ra-01SH](https://jlcpcb.com/partdetail/AiThinker-Ra01SH/C2764087), [Ra-01SH stock](https://www.lcsc.com/product-detail/LoRa-Modules_Ai-Thinker-Ra-01SH_C2764087.html), [CH340C](https://jlcpcb.com/partdetail/WCH_Jiangsu_Qin_Heng-CH340C/C7464026), [TPS63021](https://jlcpcb.com/partdetail/TexasInstruments-TPS63021DSJR/C202140), [ICS-43432](https://jlcpcb.com/partdetail/TDKInvenSense-ICS43432/C574021), [MAX98357A](https://jlcpcb.com/partdetail/MaximIntegrated-MAX98357AETET/C910544).

The ESP32 no longer needs an external antenna connector. Its PCB antenna faces a board edge and has a rule-area copper/track/via keepout. The external 915 MHz antenna attaches to U8's I-PEX socket within the board's top radio region.

## Buck-boost implementation

The selected **TPS63021DSJR** is a fixed 3.3 V, synchronous four-switch buck-boost with a 1.8–5.5 V operating range and 25 µA typical quiescent current. It can support the requested ESP32 transient load at VIN = 3.0 V; this design treats the logic rail as a conservative 1 A rail rather than using the headline switch-current rating.

- L1: `MWTC201610S2R2MT`, C6807735, 2.2 µH, 2.3 A RMS, 4.2 A saturation.
- Input: 2 × 10 µF plus 100 nF at VIN/VINA.
- Output: 3 × 22 µF.
- EN follows `SYS_SW`; PS/SYNC is low for automatic power-save mode.
- Approximate datasheet-curve efficiencies near VIN = 3.0 V, VOUT = 3.3 V: 93% at 100 mA, 94% at 300 mA, and 94% at 500 mA. These are graph estimates, not guaranteed minima.

## Radio and voice feasibility

Ra-01SH covers 803–930 MHz, provides up to +22 dBm, and exposes FSK/GFSK/LoRa modulation through SPI. Continuous voice should use GFSK/FSK plus a compressed codec such as Codec2 or low-rate ADPCM. LoRa mode trades data rate for link budget and is unsuitable for ordinary continuous voice. Actual range depends strongly on antenna quality, legal transmit limits, bitrate, terrain, enclosure loss, and interference; no fixed range is guaranteed by the PCB.

## Current assembled BOM shape

- 64 JLC-placed components per PCBA.
- 19 Basic BOM lines / 51 Basic placements.
- 13 Extended BOM lines / 13 Extended placements.
- DNP/hand-soldered: battery, speaker, main switch, potentiometer, external LED, commercial OLED module, five buttons, and probe pads.

The Basic red indicators are KT-0603R, C2286. D2 is status; D3 is the TP4056 charge indicator. They add no Extended line.

R26 is a 100 kΩ 0402 Basic resistor, C25741, added during the final audit as the manufacturer-recommended ICS-43432 SD-line pull-down. It adds no Extended line or feeder charge.

CH340C is configured for 3.3 V operation with V3 tied to VCC/3V3. The switch must be ON while programming; USB charging remains independent of the switched logic rail.

The public CH340C C7464026 page confirms Economic compatibility but does not expose a reliable stock counter. The previous live JLC BOM upload accepted it without a shortage. Recheck that row immediately before ordering and do not approve an automatic replacement unless SOP-16 pinout and CH340C crystal-less behavior match.

## Safety parts retained

The current electrically complete revision retains the 1206L200PR resettable fuse, USBLC6-2SC6 ESD suppressor, DW01A protector, and FS8205A back-to-back MOSFET. Removing them was discussed for cost reduction, but they remain in the released WROOM board because they protect against battery faults, USB transients, overcharge/overdischarge, and accidental shorts. A deliberately unprotected cost-down variant has not been generated.
