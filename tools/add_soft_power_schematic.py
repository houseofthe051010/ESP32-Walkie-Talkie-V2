"""Replace the external series switch with a compact BTN5 power latch.

Operation:
* pressing BTN5 directly pulls the main P-MOS gate low and wakes the board;
* firmware only asserts GPIO12/PWR_HOLD after BTN5 has remained held for 2 s;
* while running, firmware releases PWR_HOLD after a 2 s BTN5 shutdown hold;
* D5 pulls the PMOS gate down from the button node, while D6 lets GPIO32
  sense that node without exposing an unpowered ESP32 to the cell.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path


SCH = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project\walkiepcb.kicad_sch")


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
                return text[start:index + 1], index + 1
    raise ValueError(f"Unbalanced s-expression at {start}")


def symbol_block(text: str, reference: str) -> tuple[int, int, str]:
    marker = f'(property "Reference" "{reference}"'
    marker_at = text.find(marker)
    if marker_at < 0:
        raise ValueError(f"Placed symbol {reference} not found")
    start = text.rfind("\n\t(symbol", 0, marker_at) + 2
    block, end = balanced_block(text, start)
    return start, end, block


def set_property(block: str, name: str, value: str) -> str:
    pattern = re.compile(rf'(\(property "{re.escape(name)}" )"[^"]*"')
    block, count = pattern.subn(lambda match: f'{match.group(1)}"{value}"', block, count=1)
    if count != 1:
        raise ValueError(f"Property {name} missing from cloned symbol")
    return block


def clone_symbol(
    text: str,
    source_ref: str,
    new_ref: str,
    x: float,
    y: float,
    angle: int,
    properties: dict[str, str],
) -> str:
    _, _, block = symbol_block(text, source_ref)
    block = re.sub(
        r'(\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+)[^)]+(\))',
        lambda match: f"{match.group(1)}{x:.2f} {y:.2f} {angle}{match.group(2)}",
        block,
        count=1,
    )
    block = set_property(block, "Reference", new_ref)
    block = re.sub(
        rf'(\(reference )"{re.escape(source_ref)}"',
        lambda match: f'{match.group(1)}"{new_ref}"',
        block,
        count=1,
    )
    for name, value in properties.items():
        block = set_property(block, name, value)
    return re.sub(r'\(uuid "[^"]+"\)', lambda _: f'(uuid "{uid()}")', block)


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    justify = "right bottom" if angle in (0, 270) else "left bottom"
    return f'''\t(label "{name}"
\t\t(at {x:.2f} {y:.2f} {angle})
\t\t(effects
\t\t\t(font (size 0.9 0.9))
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{uid()}")
\t)'''


def note(message: str, x: float, y: float) -> str:
    message = message.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'''\t(text "{message}"
\t\t(exclude_from_sim no)
\t\t(at {x:.2f} {y:.2f} 0)
\t\t(effects
\t\t\t(font (size 1.0 1.0))
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)'''


def replace_label_at(text: str, old: str, x: str, y: str, new: str) -> str:
    pattern = re.compile(
        rf'(\(label )"{re.escape(old)}"(\s+\(at\s+{re.escape(x)}\s+{re.escape(y)}\s+[^)]+\))'
    )
    text, count = pattern.subn(rf'\1"{new}"\2', text, count=1)
    if count != 1:
        raise ValueError(f"Expected one {old} label at {x},{y}; found {count}")
    return text


def remove_label_at(text: str, name: str, x: str, y: str) -> str:
    marker = f'(label "{name}"\n\t\t(at {x} {y} '
    marker_at = text.find(marker)
    if marker_at < 0:
        raise ValueError(f"Label {name} at {x},{y} not found")
    start = marker_at
    block, end = balanced_block(text, start)
    return text[:start] + text[end:]


def main() -> None:
    text = SCH.read_text(encoding="utf-8")
    if '(property "Reference" "Q5"' in text:
        raise ValueError("Soft-power schematic already present")

    # Remove the obsolete two-hole external power-switch symbol and labels.
    start, end, _ = symbol_block(text, "J3")
    text = text[:start] + text[end:]
    text = remove_label_at(text, "SYS_FUSED", "312.42", "111.76")
    text = remove_label_at(text, "SYS_SW", "312.42", "114.3")

    # BTN5 grounds a separate switch node. D5 uses that node to start the PMOS;
    # D6 reports the physical button state to GPIO32 independently of Q6.
    text = replace_label_at(text, "BTN5", "339.09", "306.07", "BTN5_SW")
    start, end, sw5 = symbol_block(text, "SW5")
    sw5 = set_property(sw5, "Value", "BTN5 POWER / FUNCTION")
    sw5 = set_property(sw5, "Notes", "Hold 2 s for firmware-validated power on/off; pulls PWR_GATE low")
    text = text[:start] + sw5 + text[end:]

    # GPIO12 becomes the hold output. TP8 remains a useful diagnostic pad.
    text = replace_label_at(text, "GPIO12", "81.28", "207.01", "PWR_HOLD")
    text = replace_label_at(text, "GPIO12", "276.86", "331.47", "PWR_HOLD")
    start, end, tp8 = symbol_block(text, "TP8")
    tp8 = set_property(tp8, "Value", "PWR_HOLD / GPIO12")
    tp8 = set_property(tp8, "Notes", "Soft-power hold output and diagnostic pad; GPIO12 boot strap")
    text = text[:start] + tp8 + text[end:]

    common = {
        "JLC Classification": "Basic",
        "Economic Compatible": "YES",
        "DNP": "NO",
    }
    pmos = common | {
        "Value": "AO3401A",
        "Footprint": "Package_TO_SOT_SMD:SOT-23",
        "Manufacturer": "Alpha & Omega Semiconductor",
        "MPN": "AO3401A",
        "JLC/LCSC": "C15127",
        "Notes": "Main soft-power high-side P-MOSFET; S=SYS_FUSED D=SYS_SW",
    }
    npn = common | {
        "Value": "MMBT3904",
        "Footprint": "Package_TO_SOT_SMD:SOT-23",
        "Manufacturer": "CJ (Changjiang Electronics Tech)",
        "MPN": "MMBT3904",
        "JLC/LCSC": "C20526",
        "Notes": "Firmware-controlled main-gate pull-down",
    }
    r100 = common | {
        "Value": "100k",
        "Footprint": "Resistor_SMD:R_0402_1005Metric",
        "Manufacturer": "UNI-ROYAL",
        "MPN": "0402WGF1003TCE",
        "JLC/LCSC": "C25741",
        "Notes": "Soft-power latch",
    }
    diode = common | {
        "Value": "1N4148WS",
        "Footprint": "Diode_SMD:D_SOD-323",
        "Manufacturer": "Jiangsu Changjing Electronics Technology",
        "MPN": "1N4148WS",
        "JLC/LCSC": "C2128",
        "Notes": "Soft-power button isolation diode",
    }

    additions = [
        clone_symbol(text, "Q4", "Q5", 302.26, 137.16, 0, pmos),
        clone_symbol(text, "Q1", "Q6", 322.58, 137.16, 0, npn),
        clone_symbol(text, "R13", "R27", 297.18, 157.48, 0, r100 | {"Notes": "Main P-MOS gate pull-up"}),
        clone_symbol(text, "R13", "R28", 312.42, 157.48, 0, r100 | {"Notes": "Latch-transistor base pull-down"}),
        clone_symbol(text, "R13", "R30", 327.66, 157.48, 0, r100 | {"Notes": "GPIO12 hold base-current limit"}),
        clone_symbol(text, "D1", "D5", 345.44, 157.48, 0, diode | {"Notes": "BTN5 start diode; A=PWR_GATE K=BTN5_SW"}),
        clone_symbol(text, "D1", "D6", 365.76, 157.48, 0, diode | {"Notes": "BTN5 sense diode; A=BTN5 K=BTN5_SW"}),
        # Q5: G, S, D.
        label("PWR_GATE", 297.18, 137.16, 180),
        label("SYS_FUSED", 304.80, 132.08, 90),
        label("SYS_SW", 304.80, 142.24, 270),
        # Q6: B, E, C.
        label("PWR_LATCH_BASE", 317.50, 137.16, 180),
        label("GND", 325.12, 132.08, 90),
        label("PWR_GATE", 325.12, 142.24, 270),
        # Vertical resistor pins at y +/- 3.81 mm.
        label("SYS_FUSED", 297.18, 153.67, 90),
        label("PWR_GATE", 297.18, 161.29, 270),
        label("PWR_LATCH_BASE", 312.42, 153.67, 90),
        label("GND", 312.42, 161.29, 270),
        label("PWR_HOLD", 327.66, 153.67, 90),
        label("PWR_LATCH_BASE", 327.66, 161.29, 270),
        # D_Schottky-compatible graphic: pin 1/K left, pin 2/A right.
        label("BTN5_SW", 341.63, 157.48, 180),
        label("PWR_GATE", 349.25, 157.48, 0),
        label("BTN5_SW", 361.95, 157.48, 180),
        label("BTN5", 369.57, 157.48, 0),
        note(
            "SOFT POWER: hold BTN5 for 2 s. A press immediately wakes hardware; firmware must assert GPIO12/PWR_HOLD only after validating the full 2 s startup hold. While running, release PWR_HOLD after a 2 s shutdown hold; power drops when BTN5 is released. Typical OFF leakage target <2 uA; verify prototypes over temperature.",
            294.64,
            172.72,
        ),
    ]

    insertion = text.index("\n\t(sheet_instances")
    text = text[:insertion] + "\n" + "\n".join(additions) + text[insertion:]
    SCH.write_text(text, encoding="utf-8", newline="\n")
    print(f"Updated {SCH}")


if __name__ == "__main__":
    main()
