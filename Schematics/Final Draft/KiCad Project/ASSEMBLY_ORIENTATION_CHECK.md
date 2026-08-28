# Assembly orientation check

This sheet is the human check that accompanies the CPL. JLC library zero-angle conventions are not guaranteed to match KiCad footprint zero angles.

## Critical orientation

| Ref | Part | PCB center | KiCad rotation | Final JLC CPL rotation | What the JLC preview must show |
|---|---|---:|---:|---:|---|
| U6 | ESP32-WROOM-32D-N16 | (16.000, 49.500) | 90° | **180°** | PCB antenna points to the **left board edge** |
| U8 | Ra-01SH | (28.500, 10.000) | 0° | 0° | Module occupies the top footprint; I-PEX appears on its board-interior/lower side as in the supplied render |
| U2 | CH340C SOP-16 | (39.000, 52.000) | 90° | 90° | Pin-1 dot matches the PCB pin-1 marker |
| U3 | TP4056 ESOP-8 | (10.000, 20.500) | 90° | 90° | Exposed pad and pin-1 mark match |
| U5 | TPS63021 VSON-14 | (10.500, 25.000) | 0° | 0° | Pin-1 mark matches the PCB marker |
| U7 | MAX98357A TQFN-16 | (40.000, 27.500) | 0° | 0° | Pin-1 mark matches; exposed pad centered |
| MK1 | ICS-43432 | (36.500, 74.500) | 0° | 0° | Bottom acoustic port aligns with the PCB opening |

U6 is the only deliberate CPL rotation exception. The generator adds 90° to its raw KiCad angle. Do not upload `walkiepcb_final_cpl_raw.csv` as the JLC placement file; upload `walkiepcb_final_jlc_cpl.csv`.

If the JLC preview does not match this table, stop and correct the affected CPL row before ordering.
