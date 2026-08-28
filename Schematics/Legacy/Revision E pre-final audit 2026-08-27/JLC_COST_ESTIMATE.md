# JLCPCB cost estimate — Revision D WROOM + radio

Estimate date: **2026-08-26**. Board: **45 × 100 mm, two layers**. Quantity basis: five bare PCBs with two assembled boards. Shipping, tax, battery, 915 MHz antenna/pigtail, commercial OLED, speaker, enclosure, buttons, potentiometer, external LED, and external power switch are excluded.

## Why two assembled boards cost much more than two retail BOMs

The quote includes setup, stencil, feeder loading for Extended lines, SMT placement, optional nitrogen reflow, and PCB fabrication. At two boards, those fixed costs dominate. A previous partial live quote was **$69.84**: $4.00 PCB plus $65.84 Economic PCBA, including $8.18 setup, $1.53 stencil, $26.96 components, $27.63 Extended-component fees, $0.69 assembly, and $0.85 nitrogen reflow.

That partial quote did not include the final ESP32/radio combination. Revision D now contains **13 Extended lines**, so individual AliExpress/LCSC retail prices cannot be added together to predict the turnkey assembly total.

## Major two-board component amounts

| Part | JLC # | Qty for two | Current/snapshot unit | Approx. amount |
|---|---:|---:|---:|---:|
| ESP32-WROOM-32D-N16 | C529578 | 2 | $4.7979 | $9.60 |
| Ra-01SH 915 MHz radio | C2764087 | 2 | $4.6299 | $9.26 |
| ICS-43432 microphone | C574021 | 2 | $5.1108 | $10.22 |
| TPS63021DSJR buck-boost | C202140 | 2 | $3.2692 prior snapshot | $6.54 |
| MAX98357AETE+T amplifier | C910544 | 2 | $1.3247 | $2.65 |
| CH340C | C7464026 | 2 | uploader-dependent | approximately $1–3 |
| 3 × 22 µF output capacitors per board | C45783 | 6 | $0.3572 prior snapshot | $2.14 |
| Ra-01SH 2 × 22 µF per board | C45783 | 4 | same BOM line | approximately $1.43 |

The remaining charger, USB-C, protection, ESD, fuse, inductor, transistors, LEDs, and passives add parts cost but generally much less per item. Extended feeder/setup charges, not those small unit prices, are the main reason the total rises.

## Planning range

A realistic planning range for **two fully populated Revision D Economic PCBAs plus five bare boards is approximately $95–$115 before shipping and tax**. This is not a binding quote. It extrapolates from the user's $69.84 partial quote and adds the WROOM, Ra-01SH, CH340C path, their support parts, and likely Extended-line fees.

The exact total can only be obtained by uploading the final Gerber ZIP, `walkiepcb_jlc_bom.csv`, and placement CSV. JLC can change stock, feeder fees, promotional status, and pricing between uploads.

## Cost-down choices for a future variant

- Hand-soldering the ESP32 and Ra-01SH avoids their component and feeder charges, but the exact modules still need to be sourced and aligned carefully.
- The microphone, TPS63021, and MAX98357A are difficult fine-pitch/thermal-pad hand-solder jobs; factory placement is strongly preferred.
- Removing the fuse, ESD, and Li-ion protection saves fees but materially reduces fault protection. They are retained in this electrically safe revision.
- A Basic/low-cost microphone or amplifier replacement would require a new electrical/footprint review, not a BOM-only substitution.
- For a two-board run, changing the design to reduce **unique Extended lines** usually saves more than shaving cents from Basic passives.
