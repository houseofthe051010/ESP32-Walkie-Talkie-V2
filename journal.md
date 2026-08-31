## 2026-08-24 - Evaluating Project Goals (1.5 hours)

**Time: 1:24 PM**

Earlier this year, I made a walkie talkie using an esp32, a INMP441 mic, MAX9857A amp, I2C OLED 0.96", buttons, pot, led. It used ESPNOW, but it wasn't the best. It was hardwired, messy (extremely messy and hard to solder) and a PCB version was warranted.

I didn't just want to make a PCB for it. I needed to redesign it. I needed to add an actual radio. In the beginning of my esp32 walkie talkie project, I removed a radio because it got way too hard to solder and space was limited, but my new PCB will have space for a radio. It will feature little wires and be much better.

Here is how the old version was:

![The old version](assets/old-walkie-v1.png)

This is the 2nd iteration I made with thinner wires:

![The 2nd iteration with thinner wires](assets/old-walkie-v2-thin-wires.png)

Now, I need to make a PCB, and redesign NEW cad casing around that pcb.

First, I had to choose what I'll use:

I researched, and found out about JLBPCB extended and basic parts. Extended parts costed around 3 dollar tooling fee. Basic didn't have a tooling fee. After learning this, I realized I should maximize basic parts. I went on a searching spree.

What radio was I going to use? I searched up a list of radios and evaluated them. In the end I choose a LORA sx1262 because it was cheap and long range.

Here is the table of radios:

| Radio | Frequency | Modulation |
|---|---|---|
| NRF24L01 | 2.4 GHz | GFSK |
| SX1262 | 150–960 MHz | LoRa, FSK, GFSK |
| SX1280 | 2.4 GHz | LoRa, FLRC, FSK, GFSK |
| CC1101 | 300–348 MHz, 387–464 MHz, 779–928 MHz | FSK, GFSK, MSK, ASK, OOK |

The only worry with my choice was that the 5DBI antenna was 20CM long, which is very long. A shorter 6cm 2dbi antenna was available too but with lower power.

For my MCU, I was going to go with ESP32 S3. It had built in USB and didn't require a UART converter. For my buttons, I was going to remove the PTT system. For the power stage, I was thinking of using a AP7361C 3.2 V LDO.

I was most likely going to be using JLBPCBA so it comes assembled.
