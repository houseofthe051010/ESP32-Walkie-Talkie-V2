# Walkie-talkie Final Draft — 2026-08-27

This folder is the order-candidate release. Its KiCad source, Gerbers, BOM, CPL, and audit reports were generated from the same corrected design.

## Upload these three files to JLCPCB

From `Manufacturing/`:

1. `walkiepcb_final_45x100_2layer_gerbers.zip`
2. `walkiepcb_final_jlc_bom.csv`
3. `walkiepcb_final_jlc_cpl.csv`

Do **not** upload `walkiepcb_final_cpl_raw.csv`; it does not contain the JLC-specific ESP32 rotation correction.

## Release checks

- Board: 45.000 × 100.000 mm, 2 layers.
- ERC: 0 errors, 0 warnings.
- DRC: 0 violations, 0 unconnected pads.
- BOM/CPL: 64 installed references in each.
- U6 in corrected CPL: X 16.000 mm, Y 49.500 mm, top, 180°.
- JLC preview: ESP32 antenna must face left; Ra-01SH must match the supplied top render, with its I-PEX connector on the module's board-interior/lower side.

Read `KiCad Project/ORDER_READINESS_REPORT.md` before ordering and use `KiCad Project/FIRST_POWER_UP_CHECKLIST.md` on the first assembled board.
