import logging
import re
from PIL import Image
from printer import BluetoothTransport, PrinterClient, SerialTransport



def process_and_print(model, conn, addr, density, rotate, image_path, verbose):
    logging.basicConfig(
        level="DEBUG" if verbose else "INFO",
        format="%(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
    )

    if conn == "bluetooth":
        assert conn is not None, "--addr argument required for bluetooth connection"
        addr = addr.upper()
        assert re.fullmatch(r"([0-9A-F]{2}:){5}([0-9A-F]{2})", addr), "Bad MAC address"
        transport = BluetoothTransport(addr)
    if conn == "usb":
        port = addr if addr is not None else "auto"
        transport = SerialTransport(port=port)

    if model in ("b1", "b18", "b21"):
        max_width_px = 400
    if model in ("d11", "d110"):
        max_width_px = 96

    if model in ("b18", "d11", "d110") and density > 3:
        logging.warning(f"{model.upper()} only supports density up to 3")
        density = 3

    image = Image.open(image_path)
    if rotate != "0":
        # PIL library rotates counter clockwise, so we need to multiply by -1
        image = image.rotate(-int(rotate), expand=True)
    # assert image.width <= max_width_px, f"Image width too big for {model.upper()}"

    printer = PrinterClient(transport)
    printer.print_image(image, density=density)


if __name__ == "__main__":
    process_and_print()


