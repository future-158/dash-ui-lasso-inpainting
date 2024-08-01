import base64
from hashlib import md5
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np

# from dash.dependencies import Input, Output, State
from PIL import Image
from typing import Union


def image_to_canny(image):
    return Image.fromarray(cv2.Canny(np.array(image.convert("L")), 100, 200)).convert(
        "RGB"
    )


def export_image(
    image: Image.Image, out_dir: Union[Path, str] = "./tmp", suffix=".png"
) -> str:
    """save image to out_dir with unique name and return the path"""
    stem = md5(image.tobytes()).hexdigest()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = (out_dir / stem).with_suffix(suffix)
    image.save(dest)
    return dest.absolute().as_posix()


def unmake_image_grid(image: Image.Image, nrow: int, ncol: int, row_major=True):
    slice_width = image.width // ncol
    slice_height = image.height // nrow

    patches = []
    for h_start in range(0, image.height, slice_height):
        for w_start in range(0, image.width, slice_width):
            h_end = h_start + slice_height
            w_end = w_start + slice_width
            patch = image.crop((w_start, h_start, w_end, h_end))
            patches.append(patch)
    return patches


def figure_to_pil(figure_data) -> Image.Image:
    # Decode plotly figure to an pillow image
    url = figure_data["data"][0]["source"]
    encoded_image = url.split(";base64,")[-1]
    return Image.open(BytesIO(base64.b64decode(encoded_image)))
