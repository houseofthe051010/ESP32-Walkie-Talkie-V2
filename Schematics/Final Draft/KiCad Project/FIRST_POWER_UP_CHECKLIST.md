# First assembled-board bring-up

Use the first board as an engineering prototype. Do not begin with an unprotected LiPo and a full-power radio transmission.

1. Photograph both sides before connecting power. Inspect polarity marks, QFN/VSON exposed pads, the ESP32 antenna direction, Ra-01SH direction, solder bridges, and the microphone port.
2. With no battery or USB attached, measure resistance from `3V3` to GND and from `SYS_SW` to GND. Investigate a near-short before applying power.
3. Connect a current-limited bench supply as the cell source: 3.7 V, 100 mA limit initially. Keep the external switch OFF and verify no unexpected current.
4. Turn the switch ON. Confirm `3V3` rises to approximately 3.3 V without current limiting. Increase the limit gradually only after this passes.
5. Verify ESP32 EN is high, GPIO0 is high, and the ESP32 boots. Check serial output at 115200 baud if firmware is present.
6. Connect USB-C with the switch ON. Confirm CH340C enumeration and automatic flashing. The CH340C intentionally does not run with the switch OFF.
7. With the switch OFF, verify USB charging still works and D3 illuminates while the cell is charging. Confirm the TP4056 and cell remain within safe temperature.
8. Calibrate `BAT_SENSE`: the ADC pin should read approximately half the measured cell voltage.
9. Test the OLED at 3.3 V only after confirming the purchased module's physical pin order is `SDA`, `SCL`, `3V3`, `GND` from PCB left to right.
10. Test each button with the GPIO internal pull-up enabled. Confirm the status LED and its shared GPIO2 pad do not interfere with boot.
11. Capture microphone samples before enabling the amplifier or radio. Verify the acoustic opening and R26 pull-down behavior.
12. Attach the intended 4–8 Ω speaker. Start the MAX98357A at low digital volume; remember neither speaker output is ground.
13. Attach a tuned 915 MHz antenna to the I-PEX connector before enabling RF output. Begin at low transmit power and verify SPI, BUSY, DIO1, and RESET.
14. Stress-test 3V3 during simultaneous ESP32 activity, radio bursts, audio capture, and display updates, including at a 3.0 V simulated cell input.
15. Only after the electrical tests pass, repeat with the intended protected Li-ion/LiPo cell and enclosure.
