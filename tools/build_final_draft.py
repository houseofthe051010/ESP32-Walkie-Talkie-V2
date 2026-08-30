"""Build the reproducible JLCPCB/JLCPCBA Final Draft release.

The script deliberately regenerates all manufacturing data from the audited
KiCad source.  It does not trust older Gerber, BOM, or CPL exports.
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2")
PROJECT = ROOT / "Schematics" / "KiCad Project"
BOARD = PROJECT / "walkiepcb.kicad_pcb"
SCHEMATIC = PROJECT / "walkiepcb.kicad_sch"
FINAL = ROOT / "Schematics" / "Final Draft"
FINAL_PROJECT = FINAL / "KiCad Project"
MANUFACTURING = FINAL / "Manufacturing"
GERBERS = MANUFACTURING / "Gerbers"
AUDIT = FINAL / "Audit"
CLI = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")

FULL_BOM = PROJECT / "walkiepcb_bom_full.csv"
JLC_BOM = MANUFACTURING / "walkiepcb_final_jlc_bom.csv"
RAW_CPL = MANUFACTURING / "walkiepcb_final_cpl_raw.csv"
JLC_CPL = MANUFACTURING / "walkiepcb_final_jlc_cpl.csv"
GERBER_ZIP = MANUFACTURING / "walkiepcb_final_45x100_2layer_gerbers.zip"


def run(*arguments: str) -> None:
    print("RUN", " ".join(arguments))
    subprocess.run(arguments, check=True)


def expand_references(reference_text: str) -> list[str]:
    references: list[str] = []
    for token in reference_text.split(","):
        token = token.strip()
        match = re.fullmatch(r"([A-Za-z#]+)(\d+)-([A-Za-z#]*)(\d+)", token)
        if not match:
            references.append(token)
            continue
        first_prefix, first_number, second_prefix, second_number = match.groups()
        if second_prefix and second_prefix != first_prefix:
            raise ValueError(f"Unsupported mixed-prefix range: {token}")
        references.extend(
            f"{first_prefix}{number}"
            for number in range(int(first_number), int(second_number) + 1)
        )
    return references


def clean_generated_outputs() -> None:
    for directory in (FINAL_PROJECT, MANUFACTURING, AUDIT):
        directory.mkdir(parents=True, exist_ok=True)
    for path in GERBERS.glob("*") if GERBERS.exists() else ():
        if path.is_file():
            path.unlink()
    GERBERS.mkdir(parents=True, exist_ok=True)
    for path in (
        JLC_BOM,
        RAW_CPL,
        JLC_CPL,
        GERBER_ZIP,
        MANUFACTURING / "SHA256SUMS.txt",
    ):
        if path.exists():
            path.unlink()


def run_kicad_checks_and_exports() -> None:
    erc = AUDIT / "walkiepcb_final_erc.rpt"
    drc = AUDIT / "walkiepcb_final_drc.rpt"
    run(str(CLI), "sch", "erc", "--exit-code-violations", "--severity-all", "--output", str(erc), str(SCHEMATIC))
    run(str(CLI), "pcb", "drc", "--exit-code-violations", "--severity-all", "--output", str(drc), str(BOARD))

    fields = "Reference,Value,Footprint,Manufacturer,MPN,JLC/LCSC,JLC Classification,Economic Compatible,DNP,Notes,QUANTITY"
    groups = "Value,Footprint,Manufacturer,MPN,JLC/LCSC,JLC Classification,Economic Compatible,DNP"
    run(
        str(CLI), "sch", "export", "bom",
        "--output", str(FULL_BOM),
        "--fields", fields,
        "--labels", fields,
        "--group-by", groups,
        "--sort-field", "Reference",
        "--ref-range-delimiter", "-",
        str(SCHEMATIC),
    )
    run(str(CLI), "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "--output", str(RAW_CPL), str(BOARD))
    run(
        str(CLI), "pcb", "export", "gerbers",
        "--output", str(GERBERS),
        "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
        "--check-zones",
        str(BOARD),
    )
    run(
        str(CLI), "pcb", "export", "drill",
        "--output", str(GERBERS),
        "--format", "excellon",
        "--excellon-units", "mm",
        "--excellon-separate-th",
        "--generate-report",
        "--report-path", str(AUDIT / "walkiepcb_final_drill_report.txt"),
        str(BOARD),
    )
    run(str(CLI), "sch", "export", "pdf", "--output", str(AUDIT / "walkiepcb_final_schematic.pdf"), str(SCHEMATIC))
    run(str(CLI), "sch", "export", "netlist", "--format", "kicadxml", "--output", str(AUDIT / "walkiepcb_final_netlist.xml"), str(SCHEMATIC))
    run(str(CLI), "pcb", "render", "--output", str(AUDIT / "walkiepcb_final_top.png"), "--width", "1200", "--height", "2200", "--side", "top", "--quality", "high", "--background", "opaque", str(BOARD))
    run(str(CLI), "pcb", "render", "--output", str(AUDIT / "walkiepcb_final_bottom.png"), "--width", "1200", "--height", "2200", "--side", "bottom", "--quality", "high", "--background", "opaque", str(BOARD))
    run(str(CLI), "pcb", "render", "--output", str(AUDIT / "walkiepcb_final_isometric.png"), "--width", "1600", "--height", "1800", "--side", "top", "--quality", "high", "--background", "opaque", "--perspective", "--rotate", "-35,0,35", str(BOARD))


def generate_jlc_files() -> tuple[set[str], set[str]]:
    with FULL_BOM.open(newline="", encoding="utf-8-sig") as source:
        source_bom_rows = list(csv.DictReader(source))

    installed_rows = [row for row in source_bom_rows if row["DNP"].upper() == "NO"]
    installed_references = {
        reference
        for row in installed_rows
        for reference in expand_references(row["Reference"])
    }
    missing_codes = [row["Reference"] for row in installed_rows if not row["JLC/LCSC"]]
    if missing_codes:
        raise ValueError(f"Installed BOM rows lack JLC/LCSC codes: {missing_codes}")

    with JLC_BOM.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=("Comment", "Designator", "Footprint", "LCSC Part #"),
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        for row in installed_rows:
            writer.writerow(
                {
                    "Comment": row["Value"],
                    "Designator": ",".join(expand_references(row["Reference"])),
                    "Footprint": row["Footprint"],
                    "LCSC Part #": row["JLC/LCSC"],
                }
            )

    cpl_references: set[str] = set()
    with RAW_CPL.open(newline="", encoding="utf-8-sig") as source, JLC_CPL.open(
        "w", newline="", encoding="utf-8"
    ) as output:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(
            output,
            fieldnames=("Designator", "Mid X", "Mid Y", "Layer", "Rotation"),
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        for row in reader:
            reference = row["Ref"]
            if reference not in installed_references:
                continue
            rotation = float(row["Rot"])
            writer.writerow(
                {
                    "Designator": reference,
                    "Mid X": f'{float(row["PosX"]):.6f}mm',
                    # Preserve KiCad's native coordinate system. The Gerbers
                    # use Y=0 at the PCB top and Y=-100 at the bottom; flipping
                    # this positive makes JLC's importer invoke auto-alignment.
                    "Mid Y": f'{float(row["PosY"]):.6f}mm',
                    "Layer": "Top" if row["Side"].lower() == "top" else "Bottom",
                    "Rotation": f"{rotation:.6f}",
                }
            )
            cpl_references.add(reference)

    if installed_references != cpl_references:
        raise ValueError(
            "BOM/CPL reference mismatch: "
            f"missing from CPL={sorted(installed_references - cpl_references)}, "
            f"extra in CPL={sorted(cpl_references - installed_references)}"
        )

    with JLC_CPL.open(newline="", encoding="utf-8-sig") as source:
        cpl = {row["Designator"]: row for row in csv.DictReader(source)}
    expected_u6 = {
        "Mid X": "16.000000mm",
        "Mid Y": "-49.500000mm",
        "Layer": "Top",
        "Rotation": "90.000000",
    }
    if {key: cpl["U6"][key] for key in expected_u6} != expected_u6:
        raise ValueError(f"ESP32 CPL placement is not the verified native value: {cpl['U6']}")
    for reference, row in cpl.items():
        x = float(row["Mid X"].removesuffix("mm"))
        y = float(row["Mid Y"].removesuffix("mm"))
        if not (0.0 <= x <= 45.0 and -100.0 <= y <= 0.0):
            raise ValueError(f"{reference} CPL coordinate does not match Gerber origin: {row}")
    if cpl["J1"]["Mid Y"] != "-95.850000mm":
        raise ValueError(f"USB-C CPL coordinate is not the verified native value: {cpl['J1']}")
    return installed_references, cpl_references


def package_outputs(installed_references: set[str]) -> None:
    gerber_files = sorted(path for path in GERBERS.iterdir() if path.is_file())
    if not gerber_files:
        raise ValueError("No Gerber/drill files were generated")
    with zipfile.ZipFile(GERBER_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in gerber_files:
            archive.write(path, path.name)

    source_names = (
        "walkiepcb.kicad_sch",
        "walkiepcb.kicad_pcb",
        "walkiepcb.kicad_pro",
        "walkiepcb.kicad_prl",
        "walkiepcb.kicad_sym",
        "sym-lib-table",
        "fp-lib-table",
        "README.md",
        "ERC_NOTES.md",
        "JLC_COST_ESTIMATE.md",
        "JLC_PART_RESEARCH.md",
        "LAYOUT_NOTES.md",
        "PIN_ASSIGNMENTS.md",
        "ORDER_READINESS_REPORT.md",
        "ASSEMBLY_ORIENTATION_CHECK.md",
        "FIRST_POWER_UP_CHECKLIST.md",
        "walkiepcb_bom_full.csv",
    )
    for name in source_names:
        source = PROJECT / name
        if source.exists():
            shutil.copy2(source, FINAL_PROJECT / name)
    footprint_source = PROJECT / "walkiepcb.pretty"
    footprint_destination = FINAL_PROJECT / "walkiepcb.pretty"
    if footprint_destination.exists():
        shutil.rmtree(footprint_destination)
    shutil.copytree(footprint_source, footprint_destination)
    model_source = PROJECT / "3d"
    model_destination = FINAL_PROJECT / "3d"
    if model_destination.exists():
        shutil.rmtree(model_destination)
    if model_source.exists():
        shutil.copytree(model_source, model_destination)
    project_readme = (ROOT / "readme.md").read_text(encoding="utf-8")
    project_readme = project_readme.replace(
        "<Schematics/Final Draft/Mechanical/walkiepcb_final_exact_usb.step>",
        "<Mechanical/walkiepcb_final_exact_usb.step>",
    ).replace(
        "[`Schematics/Final Draft/Mechanical`](<Schematics/Final Draft/Mechanical>)",
        "[`Mechanical`](Mechanical)",
    ).replace(
        "<Schematics/Final Draft/Audit/", "<Audit/",
    ).replace(
        "](journal.md)", "](../../journal.md)",
    ).replace(
        "](bom.csv)", "](../../bom.csv)",
    )
    (FINAL / "PROJECT_README.md").write_text(project_readme, encoding="utf-8")
    release_journal = (ROOT / "journal.md").read_text(encoding="utf-8").replace(
        "<Schematics/Journal Images/", "<../Journal Images/"
    )
    (FINAL / "journal.md").write_text(release_journal, encoding="utf-8")

    summary = AUDIT / "release_validation.txt"
    summary.write_text(
        "Walkie-talkie soft-power production release validation\n"
        "Date: 2026-08-30\n"
        "Board: 45.0 mm x 100.0 mm, 2 copper layers\n"
        "ERC: 0 errors, 0 warnings\n"
        "DRC: 0 violations, 0 unconnected pads\n"
        f"Installed references in BOM/CPL: {len(installed_references)}\n"
        "CPL/Gerber coordinates share the native origin: X=0..45 mm, Y=0..-100 mm\n"
        "ESP32 U6 JLC CPL: X=16.000000 mm, Y=-49.500000 mm, rotation=90 degrees\n"
        "Expected JLC preview: ESP32 PCB antenna faces the LEFT board edge.\n"
        "Expected JLC preview: Ra-01SH occupies the TOP footprint and its I-PEX connector is on the board-interior/lower side of the module.\n",
        encoding="utf-8",
    )

    hash_targets = [GERBER_ZIP, JLC_BOM, JLC_CPL, RAW_CPL, *gerber_files]
    checksum_text = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in hash_targets
    )
    (MANUFACTURING / "SHA256SUMS.txt").write_text(checksum_text, encoding="utf-8")


def main() -> None:
    if not CLI.exists():
        raise FileNotFoundError(CLI)
    if not KICAD_PYTHON.exists():
        raise FileNotFoundError(KICAD_PYTHON)
    clean_generated_outputs()
    run_kicad_checks_and_exports()
    installed_references, _ = generate_jlc_files()
    package_outputs(installed_references)
    # The validator imports pcbnew, which is available in KiCad's bundled
    # Python but not necessarily in the user's system Python.
    run(str(KICAD_PYTHON), str(ROOT / "tools" / "validate_final_release.py"))
    print(f"Final Draft built at {FINAL}")
    print(f"Installed references: {len(installed_references)}")
    print("ESP32 U6 CPL: native 90 degrees; CPL origin matches Gerbers")


if __name__ == "__main__":
    main()
