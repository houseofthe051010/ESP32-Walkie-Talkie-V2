# ESP32 Walkie Talkie V2

This project is submitted to review at forge; And also, I have made a similar ESP32 based walkie talkie in the past. This is an iteration and is significantly different from the old version. It uses a custom PCB, new and different components, communication protocols, radios, and CAD/casing. It is a much needed iteration from my old version which was very difficult to hard wire and prone to several mistakes.


## Why this project exists

I made this projet not because I just wanted a walkie talkie, I wanted a control interface for my other projects. Not only can I use this board as a walkie talkie, I can use it in my other projects for other types of communications as the PCB is basically a built in radio system, which I can connect to another system using uart and use it for several other purposes. It has a LORA SX1262 radio, with 5-10km range, but at the same time has a ESP32 with WIFI+BLUETOOTH. I can use this for IoT long distance, and connect wifi/bluetooth devices and extend their range significantly using the radio. This is different from walkie talkies already out there.

## Features


- Can be used for IOT long distance when paired with the radio
- 5 Buttons to do multiple things 
- Exposed pins to connect pheripherals, such as an IMU
- ICS-43432 I2S microphone, MAX98753A amplifier, SSD1306 0.96" OLED, SX1262 RADIO, ESP32WROOM32-16
- Potentiometer, battery charge detection, TP4056 charging, 2000MAH Lipo, 10H batery life


## Hardware

In the Schematics folder is the GERBER+BOM+CPL file for easy PCBA assembly of this board. The KiCad project is also there.




## Firmware

Not implemented yet. 

## Project BOM

The table is normalized to **one walkie-talkie**. Pack prices are the supplied checkout prices and exclude shipping and tax. The PCBA is deliberately represented as one object with an unknown price; the [engineering BOM](<Schematics/KiCad Project/walkiepcb_bom_full.csv>) remains the component-level assembly list.

| Item | Qty/walkie | Pack | Pack price | Per piece | Cost/walkie | Source / note |
|---|---:|---:|---:|---:|---:|---|
| Assembled walkie-talkie PCB | 1 | 1 | N/A | N/A | **N/A** | PCBA quote pending; use the matched fabrication files under `Schematics` |
| 0.96-inch SSD1306 I2C OLED | 1 | 5 | $8.83 | $1.7660 | $1.7660 | [AliExpress OLED](https://www.aliexpress.us/item/3256805954920554.html); verify the selected four-pin I2C variant and pin order |
| 804050 2000 mAh 3.7 V LiPo | 1 | 4 | $16.60 | $4.1500 | $4.1500 | [AliExpress battery pack](https://www.aliexpress.us/item/3256812605593313.html); verify dimensions, polarity, discharge capability and protection |
| 915 MHz 2 dBi antenna with I-PEX/U.FL lead | 1 | 4 | $5.66 | $1.4150 | $1.4150 | [AliExpress antenna](https://www.aliexpress.us/item/3256805050972049.html); verify 915 MHz tuning and connector compatibility |
| 6 × 6 × 5 mm tactile push button | 5 | 50 | $1.28 | $0.0256 | $0.1280 | [AliExpress button pack](https://www.aliexpress.us/item/3256805859865632.html) |
| 0.5 W ultra-slim speaker | 1 | 5 | $2.43 | $0.4860 | $0.4860 | [AliExpress speaker](https://www.aliexpress.us/item/3256809614775479.html); select a 4–8 Ω option and verify dimensions |
| 20 kΩ panel potentiometer | 1 | 5 | $1.86 | $0.3720 | $0.3720 | [AliExpress potentiometer](https://www.aliexpress.us/item/2255799926052367.html) |
| Printed Casing, Wires, and Screws | 1 Set | 1 | $0 | $0 | $0 | Use available filament, wire and m3 screws or glue. |
| 650 nm 5 mW laser module | 1 | 10 | $2.83 | $0.2830 | $0.2830 | [AliExpress laser module](https://www.aliexpress.us/item/3256806548478140.html) |
| **Complete cost per walkie-talkie** |  |  |  |  | **N/A** | Awaiting the PCBA quote |

Buying every listed AliExpress pack costs **$39.49 before shipping and tax**. The limiting four-battery/four-antenna quantities cover four complete handsets; the fifth OLED, fifth potentiometer, fifth speaker and remaining buttons and laser modules are spares unless more batteries and antennas are purchased.


### What I would do differently in the future / future plans

- I would make it thinner
- Use more dense parts for smaller size (with a stronger budget)
- Make it fully waterproof