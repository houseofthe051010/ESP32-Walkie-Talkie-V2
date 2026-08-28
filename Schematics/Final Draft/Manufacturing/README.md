# JLCPCB upload package

Upload the Gerber ZIP, JLC BOM, and corrected JLC CPL from this directory as one matched set.

- `walkiepcb_final_45x100_2layer_gerbers.zip` — PCB fabrication archive.
- `walkiepcb_final_jlc_bom.csv` — 32 grouped lines / 64 installed references.
- `walkiepcb_final_jlc_cpl.csv` — assembler-ready placements, including the U6 ESP32 rotation correction.
- `walkiepcb_final_cpl_raw.csv` — audit only; **do not upload**.
- `Gerbers/` — uncompressed plot and drill files.
- `SHA256SUMS.txt` — generated file checksums.

After upload, visually confirm U6's antenna faces the left edge and U8 matches the supplied top render, with its I-PEX connector on the module's board-interior/lower side.
