# ESP32 Walkie-Talkie V2 Journal

## 2026-08-24 - Evaluating Project Goals (1.5 hours)

**Time:** 1:24 PM

Earlier this year, I made a walkie-talkie using an ESP32, an INMP441 microphone, a MAX98357A amplifier, a 0.96-inch I2C OLED, buttons, a potentiometer, and an LED. It used ESP-NOW, but it was not the best. It was hardwired, extremely messy, and very difficult to solder. A PCB version was warranted.

I did not just want to make a PCB for the same circuit. I needed to redesign it. I wanted to add an actual radio. At the beginning of my first ESP32 walkie-talkie project, I removed the radio because it became too difficult to solder and space inside the case was limited. A purpose-built PCB would give me room for the radio, greatly reduce the amount of wiring, and make the device much easier to assemble.

Here is the original version:

![The first hand-wired ESP32 walkie-talkie](assets/old-walkie-v1.png)

This is the second iteration I made with thinner wires:

![The second hand-wired iteration with thinner wires](assets/old-walkie-v2-thin-wires.png)

My next goal was to make a PCB and redesign a new CAD enclosure around that PCB.

First, I had to choose what I would use.

I researched JLCPCB assembly and learned about Basic and Extended parts. Extended parts could add an approximately $3 assembly setup fee per unique part number, while Basic parts did not have that fee. After learning this, I realized that I should maximize the number of Basic parts in the design. I went on a part-searching spree.

The biggest choice was the radio. I searched through several radios and compared their frequency, speed, range potential, complexity, and suitability for voice:

| Radio | Frequency and modulation | Maximum specified raw data rate | Advantages for this project | Disadvantages / decision |
|---|---|---:|---|---|
| nRF24L01+ | 2.4 GHz GFSK | 1 or 2 Mbps | Very inexpensive, simple SPI interface, and far more bandwidth than compressed voice needs | The standard IC is limited to 0 dBm and uses the crowded 2.4 GHz band, so it did not offer the sub-GHz range improvement I wanted |
| SX1262 | 150–960 MHz LoRa and (G)FSK; usable at 915 MHz | Up to 62.5 kbps LoRa or 300 kbps FSK | Up to +22 dBm, excellent receiver sensitivity, strong link budget, sub-GHz propagation, and modules are available with an I-PEX/U.FL antenna connector | LoRa's slow long-range modes cannot carry ordinary uncompressed audio; the firmware needs compressed voice and a suitable faster LoRa or FSK configuration. I chose this radio because it offered the best range-focused tradeoff |
| SX1280 | 2.4 GHz LoRa, FLRC, and (G)FSK | Programmable high-rate modes | LoRa/FLRC provide robust packet options with much more voice bandwidth than slow sub-GHz LoRa modes | It is still a 2.4 GHz radio, has a lower maximum transmit power of +12.5 dBm, and did not give me the 915 MHz system I wanted |
| CC1101 | 300–348, 387–464, and 779–928 MHz using FSK/GFSK/MSK/OOK | 0.6–600 kbps | Sub-GHz operation and enough bandwidth for compressed or even higher-rate voice links | It provides up to +12 dBm without an external range extender and would require more custom radio and packet work, so I preferred the SX1262 module |

These are radio-layer maximum rates, not guaranteed application payload rates. Packet headers, error checking, retransmission, and legal operating limits all reduce the bandwidth available to voice. My conclusion was that the SX1262 could support voice, but only if I treated audio compression and packet timing as real design requirements instead of assuming that every LoRa setting would work.

Reference material used for the comparison:

- [Nordic Semiconductor nRF24L01 product specification](https://devzone.nordicsemi.com/cfs-file/__key/support-attachments/beef5d1b77644c448dabff31668f3a47-aad1a46f307945a7b0204fd969e86bdf/content.pdf)
- [Semtech SX1262 product information](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262)
- [Semtech SX1280 product information](https://www.semtech.com/products/wireless-rf/lora-connect/sx1280)
- [Texas Instruments CC1101 product information](https://www.ti.com/product/CC1101)

The main worry with the SX1262 choice was the external antenna. The 5 dBi antenna I found was approximately 20 cm long, which is very long for a handheld device. A shorter 6 cm antenna was also available, but it was rated at 2 dBi, so I would be trading physical convenience for lower antenna gain.

For the MCU, my initial plan was to use an ESP32-S3. It had built-in USB support and could avoid a separate USB-to-UART converter. I was also thinking about changing the button layout and removing the dedicated push-to-talk system. For the first power-stage concept, I considered an AP7361C 3.2 V LDO.

I was most likely going to use JLCPCB assembly so the surface-mount parts would arrive assembled instead of recreating the wiring problem by hand.
