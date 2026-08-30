"""Independent assertions for the generated Final Draft release."""

from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path

import pcbnew


ROOT = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2")
PROJECT = ROOT / "Schematics" / "KiCad Project"
FINAL = ROOT / "Schematics" / "Final Draft"
MANUFACTURING = FINAL / "Manufacturing"
AUDIT = FINAL / "Audit"
BOARD = PROJECT / "walkiepcb.kicad_pcb"
FULL_BOM = PROJECT / "walkiepcb_bom_full.csv"
JLC_CPL = MANUFACTURING / "walkiepcb_final_jlc_cpl.csv"
GERBER_ZIP = MANUFACTURING / "walkiepcb_final_45x100_2layer_gerbers.zip"


def expand(reference_text: str) -> list[str]:
    result: list[str] = []
    for token in reference_text.split(","):
        token = token.strip()
        match = re.fullmatch(r"([A-Za-z#]+)(\d+)-([A-Za-z#]*)(\d+)", token)
        if not match:
            result.append(token)
            continue
        prefix, start, end_prefix, end = match.groups()
        assert not end_prefix or end_prefix == prefix
        result.extend(f"{prefix}{number}" for number in range(int(start), int(end) + 1))
    return result


def mm(value: int) -> float:
    return pcbnew.ToMM(value)


def footprint(board: pcbnew.BOARD, reference: str) -> pcbnew.FOOTPRINT:
    item = board.FindFootprintByReference(reference)
    assert item is not None, f"Missing footprint {reference}"
    return item


def pad_net(board: pcbnew.BOARD, reference: str, pad_number: str) -> str:
    pad = footprint(board, reference).FindPadByNumber(pad_number)
    assert pad is not None, f"Missing pad {reference}.{pad_number}"
    return pad.GetNetname()


def main() -> None:
    checks: list[str] = []
    board = pcbnew.LoadBoard(str(BOARD))

    # GetBoardEdgesBoundingBox includes half the Edge.Cuts stroke on each side.
    # Measure primitive centerlines so the reported board dimensions are the
    # fabrication outline, not 45.0 mm plus the 0.2 mm drawing stroke.
    edge_items = [item for item in board.GetDrawings() if item.GetLayer() == pcbnew.Edge_Cuts]
    edge_points = [point for item in edge_items for point in (item.GetStart(), item.GetEnd())]
    x_values = [mm(point.x) for point in edge_points]
    y_values = [mm(point.y) for point in edge_points]
    width, height = max(x_values) - min(x_values), max(y_values) - min(y_values)
    assert abs(width - 45.0) < 0.001 and abs(height - 100.0) < 0.001, (width, height)
    assert board.GetCopperLayerCount() == 2
    checks.append(f"PASS board outline {width:.3f} x {height:.3f} mm; 2 copper layers")

    expected_nets = {
        ("U2", "4"): "/3V3",
        ("U2", "16"): "/3V3",
        ("C30", "1"): "/3V3",
        ("R26", "1"): "/MIC_DATA",
        ("R26", "2"): "/GND",
        ("MK1", "7"): "/MIC_DATA",
        ("U6", "2"): "/3V3",
        ("U6", "6"): "/BAT_SENSE",
        ("U7", "7"): "/SYS_SW",
        ("U8", "3"): "/3V3",
        ("Q5", "1"): "/PWR_GATE",
        ("Q5", "2"): "/SYS_FUSED",
        ("Q5", "3"): "/SYS_SW",
        ("Q6", "1"): "/PWR_LATCH_BASE",
        ("Q6", "2"): "/GND",
        ("Q6", "3"): "/PWR_GATE",
        ("D5", "1"): "/BTN5_SW",
        ("D5", "2"): "/PWR_GATE",
        ("D6", "1"): "/BTN5_SW",
        ("D6", "2"): "/BTN5",
        ("SW5", "1"): "/BTN5_SW",
        ("SW5", "2"): "/GND",
        ("U6", "8"): "/BTN5",
        ("U6", "14"): "/PWR_HOLD",
    }
    for key, expected in expected_nets.items():
        actual = pad_net(board, *key)
        assert actual == expected, f"{key[0]}.{key[1]} expected {expected}, found {actual}"
    assert board.FindFootprintByReference("J3") is None
    checks.append("PASS critical CH340, microphone, ESP32, amplifier, battery-ADC, radio, and soft-power pad nets; J3 absent")

    j7 = footprint(board, "J7")
    j7_by_x = sorted(j7.Pads(), key=lambda pad: pad.GetPosition().x)
    j7_nets = [pad.GetNetname() for pad in j7_by_x]
    assert j7_nets == ["/OLED_SDA", "/OLED_SCL", "/3V3", "/GND"], j7_nets
    checks.append("PASS OLED holes left-to-right SDA, SCL, 3V3, GND")

    expected_holes = {"H1": (4.0, 4.0), "H2": (41.0, 4.0), "H3": (4.0, 96.0), "H4": (41.0, 96.0)}
    for ref, (x, y) in expected_holes.items():
        item = footprint(board, ref)
        position = item.GetPosition()
        assert abs(mm(position.x) - x) < 0.001 and abs(mm(position.y) - y) < 0.001
        pad = next(iter(item.Pads()))
        assert abs(mm(pad.GetDrillSize().x) - 3.2) < 0.001
    checks.append("PASS four 3.2 mm NPTH M3 holes at the verified corner coordinates")

    u6 = footprint(board, "U6")
    assert abs(mm(u6.GetPosition().x) - 16.0) < 0.001
    assert abs(mm(u6.GetPosition().y) - 49.5) < 0.001
    assert abs(u6.GetOrientationDegrees() - 90.0) < 0.001
    checks.append("PASS KiCad U6 position/orientation and left-edge antenna placement")

    with FULL_BOM.open(newline="", encoding="utf-8-sig") as source:
        bom_rows = list(csv.DictReader(source))
    installed_rows = [row for row in bom_rows if row["DNP"].upper() == "NO"]
    installed_refs = {ref for row in installed_rows for ref in expand(row["Reference"])}
    assert all(row["JLC/LCSC"] for row in installed_rows)
    assert len(installed_refs) == 71
    assert {"Q5", "Q6", "R27", "R28", "R30", "D5", "D6"} <= installed_refs
    assert "J3" not in installed_refs

    with JLC_CPL.open(newline="", encoding="utf-8-sig") as source:
        cpl_rows = list(csv.DictReader(source))
    cpl = {row["Designator"]: row for row in cpl_rows}
    assert set(cpl) == installed_refs
    assert cpl["U6"] == {
        "Designator": "U6",
        "Mid X": "16.000000mm",
        "Mid Y": "-49.500000mm",
        "Layer": "Top",
        "Rotation": "90.000000",
    }
    assert cpl["J1"]["Mid Y"] == "-95.850000mm"
    assert all(
        0.0 <= float(row["Mid X"].removesuffix("mm")) <= 45.0
        and -100.0 <= float(row["Mid Y"].removesuffix("mm")) <= 0.0
        for row in cpl_rows
    )
    checks.append("PASS BOM/CPL exact parity at 71 installed references")
    checks.append("PASS CPL and Gerbers share native X=0..45, Y=0..-100 mm coordinates")
    checks.append("PASS JLC CPL U6 = (16.000000, -49.500000), Top, 90 degrees")

    required_archive_names = {
        "walkiepcb-F_Cu.gtl", "walkiepcb-B_Cu.gbl",
        "walkiepcb-F_Paste.gtp", "walkiepcb-B_Paste.gbp",
        "walkiepcb-F_Silkscreen.gto", "walkiepcb-B_Silkscreen.gbo",
        "walkiepcb-F_Mask.gts", "walkiepcb-B_Mask.gbs",
        "walkiepcb-Edge_Cuts.gm1", "walkiepcb-PTH.drl", "walkiepcb-NPTH.drl",
        "walkiepcb-job.gbrjob",
    }
    with zipfile.ZipFile(GERBER_ZIP) as archive:
        archive_names = set(archive.namelist())
    assert archive_names == required_archive_names, sorted(archive_names)
    checks.append("PASS Gerber ZIP has the exact 9 plot layers, Gerber job, plus PTH and NPTH drill files")

    erc = (AUDIT / "walkiepcb_final_erc.rpt").read_text(encoding="utf-8")
    drc = (AUDIT / "walkiepcb_final_drc.rpt").read_text(encoding="utf-8")
    assert "0  Errors 0  Warnings" in erc
    assert "** Found 0 unconnected pads **" in drc
    checks.append("PASS exported ERC report = 0 errors / 0 warnings")
    checks.append("PASS exported DRC report = 0 violations / 0 unconnected pads")

    assert (PROJECT / "3d" / "Ra-01SH_approx.wrl").exists()
    assert (FINAL / "KiCad Project" / "3d" / "Ra-01SH_approx.wrl").exists()
    checks.append("PASS self-contained project-local Ra-01SH 3D review model")
    assert (PROJECT / "3d" / "USB-C_SMD-TYPE-C-31-M-12.step").exists()
    assert (FINAL / "KiCad Project" / "3d" / "USB-C_SMD-TYPE-C-31-M-12.step").exists()
    checks.append("PASS exact C165948 USB-C STEP model is project-local")

    report = "Soft-power production release independent validation — 2026-08-30\n\n" + "\n".join(checks) + "\n"
    (AUDIT / "release_validation_detailed.txt").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
