"""Apply the two electrically required pre-production schematic corrections.

This script is intentionally narrow and idempotent:
* run CH340C from the switched 3V3 rail and tie V3 to VCC, as WCH requires
  for 3.3 V operation;
* add the ICS-43432 SD-line 100 kOhm pulldown recommended by TDK.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path


PROJECT = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project")
SCH = PROJECT / "walkiepcb.kicad_sch"


def uid() -> str:
    return str(uuid.uuid4())


def balanced_block(text: str, start: int) -> tuple[str, int]:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start : index + 1], index + 1
    raise ValueError(f"Unbalanced block at {start}")


def schematic_root_uuid(text: str) -> str:
    match = re.search(r'^\s*\(uuid "([^"]+)"\)', text, re.MULTILINE)
    if not match:
        raise ValueError("Root schematic UUID not found")
    return match.group(1)


def property_block(name: str, value: str, x: float, y: float, hidden: bool = True) -> str:
    hidden_line = "\n\t\t\t(hide yes)" if hidden else ""
    return f'''\t\t(property "{name}" "{value}"
\t\t\t(at {x:.2f} {y:.2f} 0){hidden_line}
\t\t\t(effects
\t\t\t\t(font (size 1.27 1.27))
\t\t\t)
\t\t)'''


def label(name: str, x: float, y: float, angle: int) -> str:
    justify = "right bottom" if angle == 0 else "left bottom"
    return f'''\t(label "{name}"
\t\t(at {x:.2f} {y:.2f} {angle})
\t\t(effects
\t\t\t(font (size 0.9 0.9))
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{uid()}")
\t)'''


def resistor_r26(root_uuid: str) -> str:
    x, y = 184.15, 224.79
    props = [
        property_block("Reference", "R26", x - 5.0, y + 5.0, False),
        property_block("Value", "100k", x + 5.0, y + 5.0, False),
        property_block("Footprint", "Resistor_SMD:R_0402_1005Metric", x, y),
        property_block("Manufacturer", "UNI-ROYAL", x, y),
        property_block("MPN", "0402WGF1003TCE", x, y),
        property_block("JLC/LCSC", "C25741", x, y),
        property_block("JLC Classification", "Basic", x, y),
        property_block("Economic Compatible", "YES", x, y),
        property_block("DNP", "NO", x, y),
        property_block("Notes", "ICS-43432 SD pulldown required while microphone output is tri-stated", x, y),
    ]
    return f'''\t(symbol
\t\t(lib_id "Device:R")
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced no)
\t\t(uuid "{uid()}")
{chr(10).join(props)}
\t\t(pin "1" (uuid "{uid()}"))
\t\t(pin "2" (uuid "{uid()}"))
\t\t(instances
\t\t\t(project "ESP32 Walkie-Talkie"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "R26")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def replace_label_at(text: str, old_name: str, x: str, y: str, new_name: str) -> str:
    pattern = re.compile(
        rf'(\(label )"{re.escape(old_name)}"(\s+\(at\s+{re.escape(x)}\s+{re.escape(y)}\s+[^)]+\))'
    )
    text, count = pattern.subn(rf'\1"{new_name}"\2', text, count=1)
    if count != 1:
        raise ValueError(f"Expected exactly one {old_name} label at ({x}, {y}), found {count}")
    return text


def update_u2_notes(text: str) -> str:
    marker = '\n\t(symbol\n\t\t(lib_id "Interface_USB:CH340C")'
    start = text.find(marker)
    if start < 0:
        raise ValueError("Placed CH340C symbol not found")
    block_start = start + 2
    block, end = balanced_block(text, block_start)
    old = 'Crystal-less USB-UART; powered only from USB VBUS'
    new = 'Crystal-less USB-UART; VCC and V3 tied to switched 3V3; main switch must be ON for USB programming'
    if old not in block and new not in block:
        raise ValueError("Unexpected U2 Notes property")
    block = block.replace(old, new)
    return text[:block_start] + block + text[end:]


def main() -> None:
    text = SCH.read_text(encoding="utf-8")
    if '(property "Reference" "R26"' in text:
        raise ValueError("R26 already exists; refusing to duplicate the final-audit correction")

    # U2 pin 4 (V3) and pin 16 (VCC) must share 3V3 for documented 3.3 V use.
    text = replace_label_at(text, "CH340_V3", "388.62", "30.48", "3V3")
    text = replace_label_at(text, "USB_5V", "386.08", "30.48", "3V3")
    # C30 remains the required local bypass capacitor on the same 3V3 net.
    text = replace_label_at(text, "CH340_V3", "368.30", "19.05", "3V3")
    text = update_u2_notes(text)

    insertion = text.index("\n\t(sheet_instances")
    additions = "\n".join(
        (
            resistor_r26(schematic_root_uuid(text)),
            label("MIC_DATA", 184.15, 220.98, 90),
            label("GND", 184.15, 228.60, 270),
        )
    )
    text = text[:insertion] + "\n" + additions + text[insertion:]
    SCH.write_text(text, encoding="utf-8", newline="\n")
    print(f"Updated {SCH}")


if __name__ == "__main__":
    main()
