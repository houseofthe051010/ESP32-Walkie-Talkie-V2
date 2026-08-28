"""Apply and route the final pre-production electrical corrections on the PCB."""

from __future__ import annotations

from pathlib import Path

import pcbnew


PROJECT = Path(r"C:\Users\rshan\Documents\ESP32-Walkie-Talkie-V2\Schematics\KiCad Project")
BOARD_PATH = PROJECT / "walkiepcb.kicad_pcb"
RESISTOR_LIBRARY = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Resistor_SMD.pretty")


def mm(x: float, y: float | None = None):
    if y is None:
        return pcbnew.FromMM(x)
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def add_track(
    board: pcbnew.BOARD,
    net: pcbnew.NETINFO_ITEM,
    start: pcbnew.VECTOR2I,
    end: pcbnew.VECTOR2I,
    width: float = 0.20,
    layer: int = pcbnew.F_Cu,
) -> pcbnew.PCB_TRACK:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net)
    track.SetLayer(layer)
    track.SetWidth(mm(width))
    track.SetStart(start)
    track.SetEnd(end)
    board.Add(track)
    return track


def add_via(
    board: pcbnew.BOARD,
    net: pcbnew.NETINFO_ITEM,
    position: pcbnew.VECTOR2I,
    diameter: float = 0.60,
    drill: float = 0.30,
) -> pcbnew.PCB_VIA:
    via = pcbnew.PCB_VIA(board)
    via.SetNet(net)
    via.SetPosition(position)
    via.SetWidth(mm(diameter))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)
    return via


def reroute_usb5_away_from_u2_vcc(board: pcbnew.BOARD) -> None:
    """Delete the U2 VCC spur and move the nearby USB5 corner away from pad 16."""
    pad16 = board.FindFootprintByReference("U2").FindPadByNumber("16")
    corner = mm(34.2004, 49.8796)
    old_segments = [
        item
        for item in board.GetTracks()
        if not isinstance(item, pcbnew.PCB_VIA)
        and item.GetNetname() == "/USB_5V"
        and (
            pad16.HitTest(item.GetStart())
            or pad16.HitTest(item.GetEnd())
            or pcbnew.ToMM((item.GetStart() - corner).EuclideanNorm()) < 0.01
            or pcbnew.ToMM((item.GetEnd() - corner).EuclideanNorm()) < 0.01
        )
    ]
    if len(old_segments) != 3:
        raise RuntimeError(f"Expected three USB_5V segments at the old U2 corner, found {len(old_segments)}")
    for segment in old_segments:
        board.RemoveNative(segment)

    add_track(
        board,
        board.FindNet("/USB_5V"),
        mm(33.8157, 50.2643),
        mm(33.7053, 49.3845),
        0.40,
    )


def configure_ch340_for_3v3(board: pcbnew.BOARD) -> None:
    net_3v3 = board.FindNet("/3V3")
    net_gnd = board.FindNet("/GND")
    u2 = board.FindFootprintByReference("U2")
    c30 = board.FindFootprintByReference("C30")

    for pad in (u2.FindPadByNumber("4"), u2.FindPadByNumber("16"), c30.FindPadByNumber("1")):
        pad.SetNet(net_3v3)
    c30.FindPadByNumber("2").SetNet(net_gnd)

    # Preserve the already-DRC-clean V3-to-C30 routing, including its two vias,
    # and merge that former private net into 3V3.
    for item in board.GetTracks():
        if item.GetNetname() == "/CH340_V3":
            item.SetNet(net_3v3)
    add_track(board, net_3v3, mm(37.2470, 57.1810), mm(37.9130, 57.1810), 0.20, pcbnew.B_Cu)

    # Pin 16 reaches the same back-layer 3V3 trunk through a small via under
    # the SOIC body.  The dogleg stays between the existing UART_RX/TX routes.
    vcc_via = mm(34.900, 50.000)
    add_track(board, net_3v3, u2.FindPadByNumber("16").GetPosition(), vcc_via, 0.20)
    add_via(board, net_3v3, vcc_via, 0.50, 0.20)
    add_track(board, net_3v3, vcc_via, mm(36.300, 51.400), 0.20, pcbnew.B_Cu)
    add_track(board, net_3v3, mm(36.300, 51.400), mm(36.300, 52.200), 0.20, pcbnew.B_Cu)
    add_track(board, net_3v3, mm(36.300, 52.200), mm(37.913, 52.200), 0.20, pcbnew.B_Cu)


def add_microphone_pulldown(board: pcbnew.BOARD) -> None:
    if board.FindFootprintByReference("R26") is not None:
        raise RuntimeError("R26 already exists; refusing to duplicate it")
    net_data = board.FindNet("/MIC_DATA")
    net_gnd = board.FindNet("/GND")
    mic = board.FindFootprintByReference("MK1")

    resistor = pcbnew.FootprintLoad(str(RESISTOR_LIBRARY), "R_0402_1005Metric")
    if resistor is None:
        raise RuntimeError("Could not load the KiCad 0603 resistor footprint")
    resistor.SetReference("R26")
    resistor.SetValue("100k")
    resistor.SetPosition(mm(33.80, 77.30))
    resistor.SetOrientationDegrees(270.0)
    for field_name, field_value in {
        "Manufacturer": "UNI-ROYAL",
        "MPN": "0402WGF1003TCE",
        "JLC/LCSC": "C25741",
        "JLC Classification": "Basic",
        "Economic Compatible": "YES",
        "DNP": "NO",
        "Notes": "ICS-43432 SD pulldown",
    }.items():
        resistor.SetField(field_name, field_value)
        resistor.GetField(field_name).SetVisible(False)
    resistor.FindPadByNumber("1").SetNet(net_data)
    resistor.FindPadByNumber("2").SetNet(net_gnd)
    resistor.Reference().SetVisible(False)
    resistor.Value().SetVisible(False)
    for graphic in list(resistor.GraphicalItems()):
        if graphic.GetLayer() == pcbnew.F_SilkS:
            resistor.RemoveNative(graphic)
    board.Add(resistor)

    data_via = mm(33.792, 76.036)
    add_track(board, net_data, data_via, resistor.FindPadByNumber("1").GetPosition(), 0.15)
    ground_via = mm(33.80, 79.00)
    add_track(board, net_gnd, resistor.FindPadByNumber("2").GetPosition(), ground_via, 0.20)
    add_via(board, net_gnd, ground_via)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    reroute_usb5_away_from_u2_vcc(board)
    configure_ch340_for_3v3(board)
    add_microphone_pulldown(board)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Updated {BOARD_PATH}")


if __name__ == "__main__":
    main()
