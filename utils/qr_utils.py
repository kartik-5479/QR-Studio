from pathlib import Path

import qrcode


def generate_qr_code(data, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = qrcode.make(data)
    image.save(output_path)
    return output_path
