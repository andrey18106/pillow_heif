import os
from io import BytesIO
from pathlib import Path

import helpers
import pytest

from pillow_heif import open_heif, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()

pytest.importorskip("numpy", reason="NumPy not installed")
if not helpers.hevc_enc():
    pytest.skip("No HEVC encoder.", allow_module_level=True)


def test_primary_convert_to():
    im_heif = open_heif("images/heif/RGB_10.heif", convert_hdr_to_8bit=False)
    im_heif.add_from_heif(im_heif)
    im_heif.convert_to("BGR;16")
    assert im_heif[0].mode == "BGR;16"
    assert im_heif[1].mode == "RGB;10"
    im_heif[0].convert_to("RGB;12")
    assert im_heif.mode == "RGB;12"


def test_convert_to_same_mode():
    im_heif = open_heif(helpers.create_heif())
    assert im_heif.mode == "RGB"
    im_heif.convert_to(im_heif.mode)
    assert im_heif.mode == "RGB"
    # Image should not be loaded, when target mode equal to current.
    assert not getattr(im_heif[0], "_img_data")


@pytest.mark.parametrize(
    "img, bit",
    (
        ("images/heif/RGB_10.heif", 10),
        ("images/heif/RGB_12.heif", 12),
        ("images/heif/L_10.heif", 10),
        ("images/heif/L_12.heif", 12),
    ),
)
@pytest.mark.parametrize("mode", ("RGB;16", "BGR;16"))
def test_rgb_hdr_to_16bit_color_mode(img, mode, bit):
    heif_file = open_heif(Path(img), convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == bit
    heif_file.convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert not heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert not heif_file.has_alpha
    helpers.compare_hashes([Path(img), out_heic], hash_size=8)


@pytest.mark.parametrize("img, bit", (("images/heif/RGBA_10.heif", 10), ("images/heif/RGBA_12.heif", 12)))
@pytest.mark.parametrize("mode", ("RGBA;16", "BGRA;16"))
def test_rgba_hdr_to_16bit_color_mode(img, mode, bit):
    heif_file = open_heif(Path(img), convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == bit
    heif_file.convert_to(mode)
    out_heic = BytesIO()
    heif_file.save(out_heic, quality=-1)
    assert heif_file.bit_depth == 16
    assert heif_file.has_alpha
    heif_file = open_heif(out_heic, convert_hdr_to_8bit=False)
    assert heif_file.bit_depth == 10
    assert heif_file.has_alpha
    helpers.compare_hashes([Path(img), out_heic], hash_size=8, max_difference=1)
