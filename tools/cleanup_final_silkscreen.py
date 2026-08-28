"""Remove only silkscreen features that collide with copper or board edges."""

from __future__ import annotations

from pathlib import Path

import pcbnew


BOARD_PATH = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project\walkiepcb.kicad_pcb")


board = pcbnew.LoadBoard(str(BOARD_PATH))

# R26 is a very small production pulldown.  Its reference and two body-end
# strokes add no assembly value and collide with the nearby microphone routes.
r26 = board.FindFootprintByReference("R26")
r26.Reference().SetVisible(False)
r26.Value().SetVisible(False)
for field_name in (
    "Manufacturer",
    "MPN",
    "JLC/LCSC",
    "JLC Classification",
    "Economic Compatible",
    "DNP",
    "Notes",
):
    if r26.HasField(field_name):
        r26.GetField(field_name).SetVisible(False)
for graphic in list(r26.GraphicalItems()):
    if graphic.GetLayer() == pcbnew.F_SilkS:
        r26.RemoveNative(graphic)

pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Cleaned final silkscreen in {BOARD_PATH}")
