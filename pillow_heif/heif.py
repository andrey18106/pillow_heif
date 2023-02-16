"""
Functions and classes for heif images to read and write.
"""

from copy import deepcopy
from io import SEEK_SET
from typing import List

from _pillow_heif import lib_info, load_file
from PIL import Image

from . import options
from .constants import HeifCompressionFormat
from .misc import (
    MODE_INFO,
    CtxEncode,
    MimCImage,
    _exif_from_pillow,
    _get_bytes,
    _get_primary_index,
    _pil_to_supported_mode,
    _retrieve_exif,
    _retrieve_xmp,
    _rotate_pil,
    _xmp_from_pillow,
    get_file_mimetype,
    set_orientation,
)


class HeifImage:
    """Class represents one image in a :py:class:`~pillow_heif.HeifFile`"""

    size: tuple
    """Width and height of the image."""

    mode: str
    """A string which defines the type and depth of a pixel in the image:
    `Pillow Modes <https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes>`_

    For currently supported modes by Pillow-Heif see :ref:`image-modes`."""

    def __init__(self, c_image):
        self.size, self.mode = c_image.size_mode
        _metadata: List[dict] = c_image.metadata
        _exif = _retrieve_exif(_metadata)
        _xmp = _retrieve_xmp(_metadata)
        self.info = {
            "primary": bool(c_image.primary),
            "bit_depth": int(c_image.bit_depth),
            "exif": _exif,
            "xmp": _xmp,
            "metadata": _metadata,
            "thumbnails": [i for i in c_image.thumbnails if i is not None] if options.THUMBNAILS else [],
        }
        _color_profile = c_image.color_profile
        if _color_profile:
            if _color_profile["type"] in ("rICC", "prof"):
                self.info["icc_profile"] = _color_profile["data"]
                self.info["icc_profile_type"] = _color_profile["type"]
            else:
                self.info["nclx_profile"] = _color_profile["data"]
        self._c_image = c_image
        self._data = None

    def __repr__(self):
        _bytes = f"{len(self.data)} bytes" if self._data or isinstance(self._c_image, MimCImage) else "no"
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {_bytes} image data and {len(self.info.get('thumbnails', []))} thumbnails>"
        )

    @property
    def __array_interface__(self):
        """Numpy array interface support"""

        shape = (self.size[1], self.size[0])
        if MODE_INFO[self.mode][0] > 1:
            shape += (MODE_INFO[self.mode][0],)
        typestr = "|u1" if self.mode.find(";16") == -1 else "<u2"
        return {"shape": shape, "typestr": typestr, "version": 3, "data": self.data}

    @property
    def data(self):
        """Decodes image and returns image data from ``libheif``. See :ref:`image_data`

        .. note:: Actual size of data returned by ``data`` can be bigger than ``width * height * pixel size``.

        :returns: ``bytes`` of the decoded image from ``libheif``."""

        if not self._data:
            self._data = self._c_image.data
        return self._data

    @property
    def stride(self):
        return self._c_image.stride

    @property
    def has_alpha(self):
        """``True`` for images with ``alpha`` channel, ``False`` otherwise.

        :returns: "True" or "False" """

        return self.mode.split(sep=";")[0][-1] in ("A", "a")

    @property
    def premultiplied_alpha(self):
        """``True`` for images with ``premultiplied alpha`` channel, ``False`` otherwise.

        :returns: "True" or "False" """

        return self.mode.split(sep=";")[0][-1] == "a"

    @premultiplied_alpha.setter
    def premultiplied_alpha(self, value: bool):
        if self.has_alpha:
            self.mode = self.mode.replace("A" if value else "a", "a" if value else "A")

    def to_pillow(self) -> Image.Image:
        """Helper method to create :py:class:`PIL.Image.Image`

        :returns: :py:class:`PIL.Image.Image` class created from this image/thumbnail."""

        image = Image.frombytes(
            self.mode,  # noqa
            self.size,
            bytes(self.data),
            "raw",
            self.mode,
            self.stride,
        )
        image.info = self.info.copy()
        image.info["original_orientation"] = set_orientation(image.info)
        return image


class HeifFile:
    """This class represents the :py:class:`~pillow_heif.HeifImage` classes container.

    To create :py:class:`~pillow_heif.HeifFile` object, use the appropriate factory functions.

    * :py:func:`~pillow_heif.open_heif`
    * :py:func:`~pillow_heif.from_pillow`
    * :py:func:`~pillow_heif.from_bytes`

    .. note:: To get an empty container to fill up later, create a class with no parameters."""

    def __init__(self, fp=None, convert_hdr_to_8bit=True, bgr_mode=False, postprocess=True):
        if bgr_mode and not postprocess:
            raise ValueError("BGR mode does not work when post-processing is disabled.")

        if hasattr(fp, "seek"):
            fp.seek(0, SEEK_SET)
        if fp is None:
            self.fp_bytes = b""
            images = []
        else:
            self.fp_bytes = _get_bytes(fp)
            images = load_file(self.fp_bytes, options.DECODE_THREADS, convert_hdr_to_8bit, bgr_mode, postprocess)
        self._images: List[HeifImage] = [HeifImage(i) for i in images if i is not None]
        self.mimetype = get_file_mimetype(self.fp_bytes)
        self.primary_index = 0
        for index, _ in enumerate(self._images):
            if _.info.get("primary", False):
                self.primary_index = index

    @property
    def size(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.size` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].size

    @property
    def mode(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.mode` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].mode

    @property
    def has_alpha(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.has_alpha` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].has_alpha

    @property
    def premultiplied_alpha(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.premultiplied_alpha` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].premultiplied_alpha

    @premultiplied_alpha.setter
    def premultiplied_alpha(self, value: bool):
        self._images[self.primary_index].premultiplied_alpha = value

    @property
    def data(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.data` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].data

    @property
    def stride(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.stride` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].stride

    @property
    def info(self):
        """Points to ``info`` dict of the primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self._images[self.primary_index].info

    def to_pillow(self) -> Image.Image:
        """Helper method to create :py:class:`PIL.Image.Image`

        :returns: :py:class:`PIL.Image.Image` class created from the primary image."""

        return self._images[self.primary_index].to_pillow()

    def save(self, fp, **kwargs) -> None:
        """Saves image(s) under the given fp.

        Keyword options can be used to provide additional instructions to the writer.
        If a writer does not recognise an option, it is silently ignored.

        Supported options:
            ``save_all`` - boolean. Should all images from ``HeiFile`` be saved.
            (default = ``True``)

            ``append_images`` - do the same as in Pillow. Accepts list of ``HeifImage``

            .. note:: Appended images always will have ``info["primary"]=False``

            ``quality`` - see :py:attr:`~pillow_heif.options.QUALITY`

            ``enc_params`` - dictionary with key:value to pass to :ref:`x265 <hevc-encoder>` encoder.

            ``exif`` - override primary image's EXIF with specified.
            Accepts ``None``, ``bytes`` or ``PIL.Image.Exif`` class.

            ``xmp`` - override primary image's XMP with specified. Accepts ``None`` or ``bytes``.

            ``primary_index`` - ignore ``info["primary"]`` and set `PrimaryImage` by index.

            ``chroma`` - custom subsampling value. Possible values: ``444``, ``422`` or ``420`` (``x265`` default).

            ``format`` - string with encoder format name. Possible values: ``HEIF`` (default) or ``AVIF``.

        :param fp: A filename (string), pathlib.Path object or file object.

        :returns: None
        :raises: :py:exc:`~pillow_heif.HeifError` or :py:exc:`ValueError`"""

        _encode_images(self._images, fp, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} with {len(self)} images: {[str(i) for i in self]}>"

    def __len__(self):
        return len(self._images)

    def __iter__(self):
        for _ in self._images:
            yield _

    def __getitem__(self, index):
        if index < 0 or index >= len(self._images):
            raise IndexError(f"invalid image index: {index}")
        return self._images[index]

    def __delitem__(self, key):
        if key < 0 or key >= len(self._images):
            raise IndexError(f"invalid image index: {key}")
        del self._images[key]

    def add_frombytes(self, mode: str, size: tuple, data, **kwargs):
        """Adds image from bytes to container.

        .. note:: Supports ``stride`` value if needed.

        :param mode: `BGR(A);16`, `L;16`, `I;16L`, `RGB(A);12`, `L;12`, `RGB(A);10`, `L;10`, `RGB(A)`, `BGR(A)`, `L`
        :param size: tuple with ``width`` and ``height`` of image.
        :param data: bytes object with raw image data.

        :returns: :py:class:`~pillow_heif.HeifImage` object that was appended to HeifFile."""

        added_image = HeifImage(MimCImage(mode, size, data, **kwargs))
        self._images.append(added_image)
        return added_image

    def add_from_heif(self, image: HeifImage):
        """Add image to the container.

        :param image: ``HeifImage`` class to get images from."""

        added_image = self.add_frombytes(
            image.mode,
            image.size,
            image.data,
            stride=image.stride,
        )
        added_image.info = deepcopy(image.info)
        added_image.info.pop("primary", None)
        return added_image

    def add_from_pillow(self, image: Image.Image):
        if image.size[0] <= 0 or image.size[1] <= 0:
            raise ValueError("Empty images are not supported.")
        _info = image.info.copy()
        _info["exif"] = _exif_from_pillow(image)
        _info["xmp"] = _xmp_from_pillow(image)
        original_orientation = set_orientation(_info)
        _img = _pil_to_supported_mode(image)
        if original_orientation is not None and original_orientation != 1:
            _img = _rotate_pil(_img, original_orientation)
        added_image = self.add_frombytes(
            _img.mode,
            _img.size,
            _img.tobytes(),
        )
        for key in ["bit_depth", "thumbnails", "icc_profile", "icc_profile_type"]:
            if key in image.info:
                added_image.info[key] = image.info[key]
        for key in ["nclx_profile", "metadata"]:
            if key in image.info:
                added_image.info[key] = deepcopy(image.info[key])
        added_image.info["exif"] = _exif_from_pillow(image)
        added_image.info["xmp"] = _xmp_from_pillow(image)
        return added_image

    @property
    def __array_interface__(self):
        """Returns the primary image as a numpy array."""

        return self._images[self.primary_index].__array_interface__


def is_supported(fp) -> bool:
    """Checks if the given `fp` object contains a supported file type.

    :param fp: A filename (string), pathlib.Path object or a file object.
        The file object must implement ``file.read``, ``file.seek``, and ``file.tell`` methods,
        and be opened in binary mode.

    :returns: A boolean indicating if object can be opened."""

    __data = _get_bytes(fp, 12)
    if __data[4:8] != b"ftyp":
        return False
    return get_file_mimetype(__data) != ""


def open_heif(fp, convert_hdr_to_8bit=True, bgr_mode=False, postprocess=True) -> HeifFile:
    return HeifFile(fp, convert_hdr_to_8bit, bgr_mode, postprocess)


def read_heif(fp, convert_hdr_to_8bit=True, bgr_mode=False, postprocess=True) -> HeifFile:
    ret = open_heif(fp, convert_hdr_to_8bit, bgr_mode, postprocess)
    for img in ret:
        _ = img.data
    return ret


def encode(mode: str, size: tuple, data, fp, **kwargs) -> None:
    """Creates :py:class:`~pillow_heif.HeifFile` from bytes.

    :param mode: `BGR(A);16`, `RGB(A);16`, `L;16`, `I;16L`, `RGB(A)`, `BGR(A)`, `L`
    :param size: tuple with ``width`` and ``height`` of image.
    :param data: bytes object with raw image data.

    :returns: An :py:class:`~pillow_heif.HeifFile` object."""

    _encode_images([HeifImage(MimCImage(mode, size, data, **kwargs))], fp, **kwargs)


def _encode_images(images: List[HeifImage], fp, **kwargs) -> None:
    compression = kwargs.get("format", "HEIF")
    compression_format = HeifCompressionFormat.AV1 if compression == "AVIF" else HeifCompressionFormat.HEVC
    if not lib_info[compression]:
        raise RuntimeError(f"No {compression} encoder found.")
    images_to_save: List[HeifImage] = images + kwargs.get("append_images", [])
    if not kwargs.get("save_all", True):
        images_to_save = images_to_save[:1]
    if not images_to_save:
        raise ValueError("Cannot write file with no images as HEIF.")
    primary_index = _get_primary_index(images_to_save, kwargs.get("primary_index", None))
    ctx_write = CtxEncode(compression_format, **kwargs)
    for i, img in enumerate(images_to_save):
        _info = img.info.copy()
        _info["primary"] = False
        if i == primary_index:
            _info.update(**kwargs)
            _info["primary"] = True
        ctx_write.add_image(img.size, img.mode, img.data, **_info)
    ctx_write.save(fp)


def from_pillow(pil_image: Image.Image) -> HeifFile:
    """Creates :py:class:`~pillow_heif.HeifFile` from a Pillow Image.

    :param pil_image: Pillow :external:py:class:`~PIL.Image.Image` class.

    :returns: An :py:class:`~pillow_heif.HeifFile` object."""

    _ = HeifFile()
    _.add_from_pillow(pil_image)
    return _


def from_bytes(mode: str, size: tuple, data, **kwargs) -> HeifFile:
    """Creates :py:class:`~pillow_heif.HeifFile` from bytes.

    .. note:: Supports ``stride`` value if needed.

    :param mode: `BGR(A);16`, `L;16`, `I;16L`, `RGB(A);12`, `L;12`, `RGB(A);10`, `L;10`, `RGB(A)`, `BGR(A)`, `L`
    :param size: tuple with ``width`` and ``height`` of image.
    :param data: bytes object with raw image data.

    :returns: An :py:class:`~pillow_heif.HeifFile` object."""

    _ = HeifFile()
    _.add_frombytes(mode, size, data, **kwargs)
    return _
