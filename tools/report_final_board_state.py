"""Print concise, machine-checkable placement and critical-net audit data."""

from __future__ import annotations

from pathlib import Path

import pcbnew


BOARD_PATH = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project\walkiepcb.kicad_pcb")


def pos(item: pcbnew.BOARD_ITEM) -> str:
    point = item.GetPosition()
    return f"({pcbnew.ToMM(point.x):.3f},{pcbnew.ToMM(point.y):.3f})"


board = pcbnew.LoadBoard(str(BOARD_PATH))
print("CRITICAL FOOTPRINTS")
for ref in ("U2", "C30", "U6", "U8", "MK1", "C15", "J1"):
    fp = board.FindFootprintByReference(ref)
    print(f"{ref:4} pos={pos(fp)} rot={fp.GetOrientationDegrees():.1f} side={fp.GetLayerName()}")
    for pad in fp.Pads():
        print(f"  pad {pad.GetNumber():>3} {pos(pad):>17} net={pad.GetNetname()}")

print("\nNEAR MICROPHONE (within 7 mm)")
mic = board.FindFootprintByReference("MK1").GetPosition()
for fp in board.GetFootprints():
    distance = pcbnew.ToMM((fp.GetPosition() - mic).EuclideanNorm())
    if distance <= 7.0:
        print(f"{fp.GetReference():4} {pos(fp)} d={distance:.2f} rot={fp.GetOrientationDegrees():.1f}")

print("\nNEAR CH340/C30 (within 8 mm of U2)")
u2 = board.FindFootprintByReference("U2").GetPosition()
for fp in board.GetFootprints():
    distance = pcbnew.ToMM((fp.GetPosition() - u2).EuclideanNorm())
    if distance <= 8.0:
        print(f"{fp.GetReference():4} {pos(fp)} d={distance:.2f} rot={fp.GetOrientationDegrees():.1f}")

print("\nTRACKS TOUCHING U2 VCC/V3 OR C30.1")
targets = [
    board.FindFootprintByReference("U2").FindPadByNumber("16"),
    board.FindFootprintByReference("U2").FindPadByNumber("4"),
    board.FindFootprintByReference("C30").FindPadByNumber("1"),
]
for track in board.GetTracks():
    if isinstance(track, pcbnew.PCB_VIA):
        continue
    for target in targets:
        if target.HitTest(track.GetStart()) or target.HitTest(track.GetEnd()):
            print(
                f"{track.GetNetname():12} layer={track.GetLayerName():5} "
                f"start=({pcbnew.ToMM(track.GetStart().x):.3f},{pcbnew.ToMM(track.GetStart().y):.3f}) "
                f"end=({pcbnew.ToMM(track.GetEnd().x):.3f},{pcbnew.ToMM(track.GetEnd().y):.3f}) "
                f"width={pcbnew.ToMM(track.GetWidth()):.3f}"
            )
            break
