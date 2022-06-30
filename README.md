# pillow-heif

![analysis](https://github.com/bigcat88/pillow_heif/actions/workflows/analysis-coverage.yml/badge.svg)
![build](https://github.com/bigcat88/pillow_heif/actions/workflows/create-release-draft.yml/badge.svg)
![wheels test](https://github.com/bigcat88/pillow_heif/actions/workflows/test-wheels.yml/badge.svg)
[![codecov](https://codecov.io/gh/bigcat88/pillow_heif/branch/master/graph/badge.svg?token=JY64F2OL6V)](https://codecov.io/gh/bigcat88/pillow_heif)
![style](https://img.shields.io/badge/code%20style-black-000000.svg)

![PythonVersion](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
![impl](https://img.shields.io/pypi/implementation/pillow_heif)
![pypi](https://img.shields.io/pypi/v/pillow_heif.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/pillow-heif)
[![Downloads](https://static.pepy.tech/personalized-badge/pillow-heif?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/pillow-heif)

![Mac OS](https://img.shields.io/badge/mac%20os-FCC624?style=for-the-badge&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0078D6.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)

### **_v0.4.0_**

Python bindings to [libheif](https://github.com/strukturag/libheif) for working with HEIF images and an add-on for Pillow.

README for versions `0.2 - 0.3` lives [here](https://github.com/bigcat88/pillow_heif/blob/9d2045111d27ff842678097175c7d95b5f1ec212/README.md).

Features:
 * Decoding of `8`, `10`, `12` bit HEIF images.
 * Encoding of `8`, `10`, `12` bit HEIF images.
 * `EXIF`, `XMP`, `IPTC` read & write support.
 * Support of multiple images in one file, e.g **HEIC** files and `PrimaryImage` attribute.
 * HEIF `native thumbnails` support(API for this is still in `alpha` and could be changed).
 * Adding all this features to Pillow in one line of code as a plugin.
 * Includes AVIF(x264) decoder.

## Install
```console
python3 -m pip install pillow-heif
```

## Example of use as a Pillow plugin
```python3
from PIL import Image, ImageSequence
from pillow_heif import register_heif_opener

register_heif_opener()

image = Image.open("images/input.heic")  # do whatever need with a Pillow image
for i, frame in enumerate(ImageSequence.Iterator(image)):
    rotated = frame.rotate(13)
    rotated.save(f"rotated_frame{i}.heic", quality=90)
```

## 16 bit PNG to 10 bit HEIF using OpenCV
```python3
import cv2
import pillow_heif

cv_img = cv2.imread("images/jpeg_gif_png/RGBA_16.png", cv2.IMREAD_UNCHANGED)
heif_file = pillow_heif.from_bytes(
    mode="BGRA;16",
    size=(cv_img.shape[1], cv_img.shape[0]),
    data=bytes(cv_img)
)
heif_file.save("RGBA_10bit.heif", quality=-1)
```

## 8/10/12 bit HEIF to 16 bit PNG using OpenCV
```python3
import numpy as np
import cv2
import pillow_heif

heif_file = pillow_heif.open_heif("images/rgb12.heif", convert_hdr_to_8bit=False)
heif_file[0].convert_to("BGR;16")
np_array = np.asarray(heif_file[0])
cv2.imwrite("rgb16.png", np_array)
```

## Accessing decoded image data
```python3
import pillow_heif

if pillow_heif.is_supported("images/rgb10.heif"):
    heif_file = pillow_heif.open_heif("images/rgb10.heif", convert_hdr_to_8bit=False)
    print("image mode:", heif_file[0].mode)
    print("image data length:", len(heif_file[0].data))
    print("image data stride:", heif_file[0].stride)
    heif_file[0].convert_to("RGB;16")  # convert 10 bit image to RGB 16 bit.
    print("image mode:", heif_file[0].mode)
```

## Get decoded image data as a Numpy array
```python3
import numpy as np
import pillow_heif

if pillow_heif.is_supported("images/rgb8_512_512_1_0.heic"):
    heif_file = pillow_heif.open_heif("images/rgb8_512_512_1_0.heic")
    np_array = np.asarray(heif_file[0])
```

## Scaling and adding thumbnails
```python3
import pillow_heif

if pillow_heif.is_supported("input.heic"):
    heif_file = pillow_heif.open_heif("input.heic")
    for img in heif_file:  # you still can use it without iteration, like before.
        img.scale(1024, 768) # scaling each image in file.
    heif_file.add_thumbnails([768, 512, 256])  # add three new thumbnail boxes.
    # default quality is probably ~77 in x265, set it a bit lower.
    heif_file.save("output.heic", quality=70, save_all=False) # save_all is True by default.
```

## More Information

- [Documentation](https://pillow-heif.readthedocs.io/)
  - [Installation](https://pillow-heif.readthedocs.io/en/latest/installation.html)
  - [Pillow plugin](https://pillow-heif.readthedocs.io/en/latest/pillow-plugin.html)
  - [Using HeifFile](https://pillow-heif.readthedocs.io/en/latest/heif-file.html)
  - [Image modes](https://pillow-heif.readthedocs.io/en/latest/image-modes.html)
  - [Options](https://pillow-heif.readthedocs.io/en/latest/options.html)
  - [Encoding](https://pillow-heif.readthedocs.io/en/latest/encoding.html)
- [Examples](https://github.com/bigcat88/pillow_heif/tree/master/examples)
- [Contribute](https://github.com/bigcat88/pillow_heif/blob/master/.github/CONTRIBUTING.md)
  - [Discussions](https://github.com/bigcat88/pillow_heif/discussions)
  - [Issues](https://github.com/bigcat88/pillow_heif/issues)
- [Changelog](https://github.com/bigcat88/pillow_heif/blob/master/CHANGELOG.md)

## Wheels

| **_Wheels table_** | macOS<br/>Intel | macOS<br/>Silicon | Windows<br/>64bit | musllinux* | manylinux* |
|--------------------|:---------------:|:-----------------:|:-----------------:|:----------:|:----------:|
| CPython 3.6        |       N/A       |        N/A        |        N/A        |     ✅      |     ✅      |
| CPython 3.7        |        ✅        |        N/A        |         ✅         |     ✅      |     ✅      |
| CPython 3.8        |        ✅        |        N/A        |         ✅         |     ✅      |     ✅      |
| CPython 3.9        |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| CPython 3.10       |        ✅        |         ✅         |         ✅         |     ✅      |     ✅      |
| PyPy 3.7 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |
| PyPy 3.8 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |
| PyPy 3.9 v7.3      |        ✅        |        N/A        |        N/A        |    N/A     |     ✅      |

&ast; **i686**, **x86_64**, **aarch64** wheels.

#### **_Versions 0.5.X will be last to support Python 3.6_**
