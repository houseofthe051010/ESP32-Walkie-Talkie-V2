from machine import Pin, SPI, I2S
from time import sleep_ms, ticks_ms, ticks_diff
from array import array

power = Pin(12, Pin.OUT)
power.value(1)

button = Pin(4, Pin.IN, Pin.PULL_UP)

amp = Pin(15, Pin.OUT)
amp.value(1)

nss = Pin(5, Pin.OUT)
reset = Pin(17, Pin.OUT)
busy = Pin(36, Pin.IN)

nss.value(1)

spi = SPI(
    2,
    baudrate=4000000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(23),
    miso=Pin(19)
)

speaker = I2S(
    0,
    sck=Pin(26),
    ws=Pin(25),
    sd=Pin(22),
    mode=I2S.TX,
    bits=16,
    format=I2S.STEREO,
    rate=8000,
    ibuf=8000
)


def beep():
    sound = array("h")

    for i in range(1600):
        if i % 8 < 4:
            value = 8000
        else:
            value = -8000

        sound.append(value)
        sound.append(value)

    speaker.write(sound)


def wait_radio():
    while busy.value():
        sleep_ms(1)


def send_command(command, data=b""):
    wait_radio()

    nss.value(0)
    spi.write(bytes([command]) + data)
    nss.value(1)

    wait_radio()


def read_command(command, amount):
    wait_radio()

    nss.value(0)
    spi.write(bytes([command, 0]))
    data = spi.read(amount)
    nss.value(1)

    wait_radio()

    return data


def write_buffer(data):
    wait_radio()

    nss.value(0)
    spi.write(bytes([0x0E, 0]) + data)
    nss.value(1)

    wait_radio()


def read_buffer(start, amount):
    wait_radio()

    nss.value(0)
    spi.write(bytes([0x1E, start, 0]))
    data = spi.read(amount)
    nss.value(1)

    wait_radio()

    return data


def packet_size(size):
    send_command(
        0x8C,
        bytes([
            0, 8,
            0,
            size,
            1,
            0
        ])
    )


def clear_irq():
    send_command(0x02, b"\xFF\xFF")


def get_irq():
    data = read_command(0x12, 2)
    return (data[0] << 8) | data[1]


def receive_mode():
    send_command(0x80, b"\x00")
    packet_size(255)
    clear_irq()
    send_command(0x82, b"\xFF\xFF\xFF")


def setup_radio():
    reset.value(0)
    sleep_ms(10)

    reset.value(1)
    sleep_ms(20)

    send_command(0x80, b"\x00")
    send_command(0x96, b"\x00")
    send_command(0x9D, b"\x01")
    send_command(0x8A, b"\x01")
    send_command(0x98, b"\xE1\xE9")

    frequency = 915000000
    number = frequency * (1 << 25) // 32000000

    send_command(
        0x86,
        bytes([
            (number >> 24) & 255,
            (number >> 16) & 255,
            (number >> 8) & 255,
            number & 255
        ])
    )

    send_command(0x8B, b"\x07\x04\x01\x00")
    send_command(0x95, b"\x04\x07\x00\x01")
    send_command(0x8E, b"\x0A\x04")
    send_command(0x8F, b"\x00\x00")

    receive_mode()


def send_signal():
    message = b"BEEP"

    send_command(0x80, b"\x00")
    clear_irq()

    write_buffer(message)
    packet_size(len(message))

    send_command(0x83, b"\x00\x00\x00")

    start = ticks_ms()

    while not get_irq() & 1:
        if ticks_diff(ticks_ms(), start) > 2000:
            break

        sleep_ms(5)

    print("Signal sent")

    receive_mode()


def check_radio():
    irq = get_irq()

    if irq & 2:
        info = read_command(0x13, 2)

        size = info[0]
        start = info[1]

        message = read_buffer(start, size)

        receive_mode()

        if message == b"BEEP":
            print("Signal received")
            beep()


setup_radio()

print("Ready")

last_button = 1

while True:
    check_radio()

    current_button = button.value()

    if current_button == 0 and last_button == 1:
        send_signal()

    last_button = current_button

    sleep_ms(10)
