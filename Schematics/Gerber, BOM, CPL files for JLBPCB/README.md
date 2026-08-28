# Revision E manufacturing package

This is the 45.000 × 100.000 mm, two-layer WROOM + CH340C + Ra-01SH board with four M3 mounting holes, compact high-current wire pads, reversed OLED holes, and TP7/TP8 expansion pads.

Upload these three files to JLCPCB:

- `walkiepcb_revE_45x100_2layer_gerbers.zip`
- `walkiepcb_revE_jlc_bom.csv`
- `walkiepcb_revE_jlc_cpl.csv`

The BOM and CPL contain the same 63 installed references. Hand-soldered connectors/buttons, the OLED holes, all test pads, and mounting holes are excluded from assembly. The U6 rotation in the CPL includes a +90° JLC-specific correction; in the assembly preview, the ESP32 PCB antenna must face the left board edge. U8 remains at rotation 0° with its I-PEX socket toward the top.

OLED J7 physical order when viewing the component/front side, left to right, is `SDA`, `SCL`, `3V3`, `GND`.

The back silkscreen labels the J2–J7 hand-soldered pads. `walkiepcb_revE_bottom.png` shows their final readable orientation and spacing.

The back also carries centered white-silkscreen branding: italic `Verma Industries` with `ESP32 Walkie Talkie V2` below. Select **black solder mask** in the PCB ordering form; solder-mask color is an order option and is not encoded in the Gerbers.

Machine verification:

- DRC: 0 violations and 0 unconnected pads.
- ERC: 0 errors and 1 known MAX98357A exposed-pad symbol warning.
- Copper layers: F.Cu and B.Cu only.

Always recheck live stock, package mapping, polarity, and the JLC assembly preview before ordering.
