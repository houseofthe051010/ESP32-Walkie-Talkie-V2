"""Replace J3 with a compact BTN5/GPIO12 soft-power latch."""

from __future__ import annotations

from pathlib import Path

import pcbnew


BOARD_PATH = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project\walkiepcb.kicad_pcb")
LIBS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
PLACEMENT_ONLY = False


def mm(x, y=None):
    if y is None:
        return pcbnew.FromMM(x)
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def xy(point):
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def add_net(board, name):
    net = board.FindNet(name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
    return net


def add_track(board, net, start, end, width=0.20, layer=pcbnew.F_Cu):
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net)
    track.SetLayer(layer)
    track.SetWidth(mm(width))
    track.SetStart(start)
    track.SetEnd(end)
    board.Add(track)


def path(board, net, points, width=0.20, layer=pcbnew.F_Cu):
    for start, end in zip(points, points[1:]):
        add_track(board, net, start, end, width, layer)


def add_via(board, net, position, diameter=0.60, drill=0.30):
    via = pcbnew.PCB_VIA(board)
    via.SetNet(net)
    via.SetPosition(position)
    via.SetWidth(mm(diameter))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)


def load(library, name):
    footprint = pcbnew.FootprintLoad(str(LIBS / f"{library}.pretty"), name)
    if footprint is None:
        raise RuntimeError(f"Unable to load {library}:{name}")
    return footprint


def add_part(board, reference, value, library, footprint_name, position, angle, fields, pad_nets):
    footprint = load(library, footprint_name)
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(mm(*position))
    footprint.SetOrientationDegrees(angle)
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)
    for graphic in list(footprint.GraphicalItems()):
        if graphic.GetLayer() == pcbnew.F_SilkS:
            footprint.RemoveNative(graphic)
    for name, field_value in fields.items():
        footprint.SetField(name, field_value)
        footprint.GetField(name).SetVisible(False)
    for number, net in pad_nets.items():
        footprint.FindPadByNumber(number).SetNet(net)
    board.Add(footprint)
    return footprint


def remove_track_between(board, net_name, a, b):
    expected = {tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in b)}
    for track in list(board.GetTracks()):
        if isinstance(track, pcbnew.PCB_VIA) or track.GetNetname() != net_name:
            continue
        endpoints = {
            tuple(round(v, 4) for v in xy(track.GetStart())),
            tuple(round(v, 4) for v in xy(track.GetEnd())),
        }
        if endpoints == expected:
            board.RemoveNative(track)
            return
    raise RuntimeError(f"Track {net_name} {a}->{b} not found")


def remove_via_at(board, net_name, at):
    expected = tuple(round(v, 4) for v in at)
    for track in list(board.GetTracks()):
        if not isinstance(track, pcbnew.PCB_VIA) or track.GetNetname() != net_name:
            continue
        if tuple(round(v, 4) for v in xy(track.GetPosition())) == expected:
            board.RemoveNative(track)
            return
    raise RuntimeError(f"Via {net_name} at {at} not found")


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    if board.FindFootprintByReference("Q5") is not None:
        raise RuntimeError("Soft-power PCB already present")

    # Keep the existing long BTN5 route as the ESP32 sense line.  Its final
    # segment is replaced by D5, while SW5 itself becomes the raw gate node.
    btn5 = board.FindNet("/BTN5")
    pwr_gate = add_net(board, "/PWR_GATE")
    btn5_sw = add_net(board, "/BTN5_SW")
    u6 = board.FindFootprintByReference("U6")
    remove_track_between(board, "/BTN5", (34.0000, 87.5000), (32.6572, 86.1572))

    pwr_hold = board.FindNet("/GPIO12")
    pwr_hold.SetNetname("/PWR_HOLD")
    board.FindFootprintByReference("TP8").SetValue("PWR_HOLD / GPIO12")
    nets = {
        "SYS_FUSED": board.FindNet("/SYS_FUSED"),
        "SYS_SW": board.FindNet("/SYS_SW"),
        "GND": board.FindNet("/GND"),
        "BTN5": btn5,
        "BTN5_SW": btn5_sw,
        "PWR_HOLD": pwr_hold,
        "PWR_GATE": pwr_gate,
        "PWR_LATCH_BASE": add_net(board, "/PWR_LATCH_BASE"),
    }

    old_switch = board.FindFootprintByReference("J3")
    board.RemoveNative(old_switch)
    # Shift the TX diagnostic pad down to open a compact, accessible soft-latch
    # placement beside the remaining diagnostic pads.
    board.FindFootprintByReference("TP3").SetPosition(mm(16.5, 13.5))
    sw5 = board.FindFootprintByReference("SW5")
    sw5.SetValue("BTN5 POWER / FUNCTION")
    sw5.FindPadByNumber("1").SetNet(btn5_sw)

    common = {"JLC Classification": "Basic", "Economic Compatible": "YES", "DNP": "NO"}
    pmos = common | {"Manufacturer": "Alpha & Omega Semiconductor", "MPN": "AO3401A", "JLC/LCSC": "C15127", "Notes": "Main soft-power high-side P-MOSFET"}
    npn = common | {"Manufacturer": "CJ (Changjiang Electronics Tech)", "MPN": "MMBT3904", "JLC/LCSC": "C20526", "Notes": "Firmware-controlled gate pull-down"}
    resistor = common | {"Manufacturer": "UNI-ROYAL", "MPN": "0402WGF1003TCE", "JLC/LCSC": "C25741", "Notes": "Soft-power latch"}
    diode = common | {"Manufacturer": "Jiangsu Changjing Electronics Technology", "MPN": "1N4148WS", "JLC/LCSC": "C2128", "Notes": "Soft-power button isolation"}

    parts = {}
    parts["Q5"] = add_part(board, "Q5", "AO3401A", "Package_TO_SOT_SMD", "SOT-23", (42.5, 70.7), 90, pmos, {"1": nets["PWR_GATE"], "2": nets["SYS_FUSED"], "3": nets["SYS_SW"]})
    parts["R27"] = add_part(board, "R27", "100k", "Resistor_SMD", "R_0402_1005Metric", (44.0, 74.5), 270, resistor | {"Notes": "Main-gate pull-up"}, {"1": nets["SYS_FUSED"], "2": nets["PWR_GATE"]})
    parts["Q6"] = add_part(board, "Q6", "MMBT3904", "Package_TO_SOT_SMD", "SOT-23", (17.0, 6.0), 180, npn, {"1": nets["PWR_LATCH_BASE"], "2": nets["GND"], "3": nets["PWR_GATE"]})
    parts["R28"] = add_part(board, "R28", "100k", "Resistor_SMD", "R_0402_1005Metric", (14.0, 3.0), 0, resistor | {"Notes": "Latch-base pull-down"}, {"1": nets["PWR_LATCH_BASE"], "2": nets["GND"]})
    parts["R30"] = add_part(board, "R30", "100k", "Resistor_SMD", "R_0402_1005Metric", (17.5, 9.0), 0, resistor | {"Notes": "GPIO12 hold base-current limit"}, {"1": nets["PWR_HOLD"], "2": nets["PWR_LATCH_BASE"]})
    parts["D5"] = add_part(board, "D5", "1N4148WS", "Diode_SMD", "D_SOD-323", (37.0, 84.0), 0, diode | {"Notes": "BTN5 start diode; A=PWR_GATE K=BTN5_SW"}, {"1": nets["BTN5_SW"], "2": nets["PWR_GATE"]})
    parts["D6"] = add_part(board, "D6", "1N4148WS", "Diode_SMD", "D_SOD-323", (35.0, 81.5), 180, diode | {"Notes": "BTN5 sense diode; A=BTN5 K=BTN5_SW"}, {"1": nets["BTN5_SW"], "2": nets["BTN5"]})

    p = lambda ref, number: parts[ref].FindPadByNumber(number).GetPosition()

    if PLACEMENT_ONLY:
        pcbnew.SaveBoard(str(BOARD_PATH), board)
        print(f"Placement-only update {BOARD_PATH}")
        return

    # Move the TX test pad without leaving its original trace stub, then route
    # the nearby radio-reset trace around the new pad location.
    remove_track_between(board, "/UART_TX", (18.0000, 10.0000), (17.5253, 10.4747))
    remove_track_between(board, "/UART_TX", (17.5253, 10.4747), (17.5253, 13.8016))
    path(board, board.FindNet("/UART_TX"), [mm(16.5, 13.5), mm(17.5253, 13.8016)])

    # D5 starts the PMOS from the grounded switch node; D6 independently
    # reports the physical button state on the original BTN5 route.
    btn5_via = mm(33.45, 82.5)
    path(board, nets["BTN5"], [mm(32.6572, 86.1572), btn5_via], layer=pcbnew.B_Cu)
    add_via(board, nets["BTN5"], btn5_via)
    path(board, nets["BTN5"], [btn5_via, p("D6", "2")])
    path(board, nets["BTN5_SW"], [p("D6", "1"), mm(36.05, 83.0), p("D5", "1")])
    path(board, nets["BTN5_SW"], [p("D5", "1"), mm(36.95, 85.0), mm(35.5, 86.5), sw5.FindPadByNumber("1").GetPosition()])

    # Remove the redundant USB_5V loop through the former switch area. D1 pad 2
    # reconnects to Q4 through two short vias, leaving room for the latch PMOS.
    usb_loop = [
        ((43.0, 63.5), (43.0962, 63.5962)),
        ((43.0962, 63.5962), (43.0962, 71.1687)),
        ((43.0962, 71.1687), (42.0569, 72.2080)),
        ((42.0569, 72.2080), (40.5391, 72.2080)),
        ((40.5391, 72.2080), (39.2037, 70.8726)),
        ((39.2037, 70.8726), (39.2037, 69.2660)),
        ((39.2037, 69.2660), (38.3718, 68.4341)),
        ((38.3718, 68.4341), (38.0841, 68.4341)),
        ((38.0841, 68.4341), (37.3290, 67.6790)),
    ]
    for a, b in usb_loop:
        remove_track_between(board, "/USB_5V", a, b)
    for a, b in (
        ((37.3290, 67.6790), (37.3290, 61.3405)),
        ((37.3290, 61.3405), (38.2320, 60.4375)),
    ):
        remove_track_between(board, "/USB_5V", a, b)
    d1_usb = board.FindFootprintByReference("D1").FindPadByNumber("2").GetPosition()
    q4_usb = board.FindFootprintByReference("Q4").FindPadByNumber("1").GetPosition()
    usb_via_a = mm(43.6, 63.5)
    usb_via_b = mm(39.5, 61.5)
    path(board, board.FindNet("/USB_5V"), [d1_usb, usb_via_a], 0.40)
    add_via(board, board.FindNet("/USB_5V"), usb_via_a, 0.80, 0.40)
    path(board, board.FindNet("/USB_5V"), [usb_via_a, mm(43.6, 61.5), usb_via_b], 0.40, pcbnew.B_Cu)
    add_via(board, board.FindNet("/USB_5V"), usb_via_b, 0.80, 0.40)
    path(board, board.FindNet("/USB_5V"), [usb_via_b, q4_usb], 0.40)

    # Replace the obsolete J3 power endpoints with Q5.
    remove_track_between(board, "/SYS_SW", (41.3, 70.5), (40.3589, 69.5589))
    path(board, nets["SYS_SW"], [p("Q5", "3"), mm(41.6, 69.7625), mm(40.3589, 69.5589)], 0.50)
    remove_track_between(board, "/SYS_FUSED", (37.5000, 70.5000), (39.4789, 68.5211))
    remove_track_between(board, "/SYS_FUSED", (39.4789, 68.5211), (41.4000, 68.5211))
    remove_via_at(board, "/SYS_FUSED", (41.4000, 68.5211))
    fused_tap = mm(41.4, 68.5211)
    source_hub = mm(44.0, 71.1)
    path(board, nets["SYS_FUSED"], [p("Q5", "2"), source_hub, mm(44.0, 67.8), fused_tap], 0.50)
    path(board, nets["SYS_FUSED"], [source_hub, p("R27", "1")])
    path(board, nets["PWR_GATE"], [p("Q5", "1"), mm(41.3, 72.4), mm(42.0, 73.1), mm(42.0, 75.01), p("R27", "2")])

    # Q6 base network sits beside the diagnostic pads and taps the already
    # routed PWR_HOLD testpoint trace.
    hold_tap = mm(15.0171, 7.0171)
    path(board, nets["PWR_HOLD"], [hold_tap, mm(15.8, 7.8), p("R30", "1")])
    base_hub = mm(18.5, 9.0)
    path(board, nets["PWR_LATCH_BASE"], [p("Q6", "1"), base_hub, p("R30", "2")])
    path(board, nets["PWR_LATCH_BASE"], [base_hub, mm(19.0, 9.0), mm(19.0, 1.5), mm(13.49, 1.5), p("R28", "1")])
    q6_gnd_via = mm(17.7, 4.0)
    path(board, nets["GND"], [p("Q6", "2"), q6_gnd_via], 0.25)
    add_via(board, nets["GND"], q6_gnd_via)
    r28_gnd_via = mm(15.0, 3.0)
    path(board, nets["GND"], [p("R28", "2"), r28_gnd_via], 0.25)
    add_via(board, nets["GND"], r28_gnd_via)

    # A single low-current gate trunk follows the extreme right edge on B.Cu,
    # linking the top latch transistor, main PMOS, and bottom pushbutton.
    q6_gate_via = mm(16.5, 3.0)
    path(board, nets["PWR_GATE"], [p("Q6", "3"), q6_gate_via])
    add_via(board, nets["PWR_GATE"], q6_gate_via)
    q5_gate_via = mm(41.0, 71.0)
    switch_gate_via = mm(38.0, 83.0)
    path(board, nets["PWR_GATE"], [q6_gate_via, mm(16.5, 2.0), mm(44.4, 2.0), mm(44.4, 70.5), q5_gate_via], layer=pcbnew.B_Cu)
    add_via(board, nets["PWR_GATE"], q5_gate_via)
    path(board, nets["PWR_GATE"], [q5_gate_via, p("Q5", "1")])
    path(board, nets["PWR_GATE"], [mm(44.4, 70.5), mm(44.4, 83.0), switch_gate_via], layer=pcbnew.B_Cu)
    add_via(board, nets["PWR_GATE"], switch_gate_via)
    path(board, nets["PWR_GATE"], [switch_gate_via, p("D5", "2")])

    # Remove obsolete back-silkscreen names for the deleted external switch.
    for drawing in list(board.GetDrawings()):
        if isinstance(drawing, pcbnew.PCB_TEXT) and drawing.GetText() in {"SYS_FUSED", "SYS_SW"}:
            _, y = xy(drawing.GetPosition())
            if 60 < y < 80:
                board.RemoveNative(drawing)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Updated {BOARD_PATH}")


if __name__ == "__main__":
    main()
