"""
Enums from LibHeif that are used.
"""

from enum import IntEnum


class HeifChroma(IntEnum):
    """Chroma subsampling definitions."""

    UNDEFINED = 99
    """Undefined chroma."""
    MONOCHROME = 0
    """Mono chroma."""
    CHROMA_420 = 1
    """``Cb`` and ``Cr`` are each subsampled at a factor of 2 both horizontally and vertically."""
    CHROMA_422 = 2
    """The two chroma components are sampled at half the horizontal sample rate of luma."""
    CHROMA_444 = 3
    """Each of the three Y'CbCr components has the same sample rate."""
    INTERLEAVED_RGB = 10
    """Simple interleaved RGB."""
    INTERLEAVED_RGBA = 11
    """Interleaved RGB with Alpha channel."""
    INTERLEAVED_RRGGBB_BE = 12
    """10 bit RGB BE."""
    INTERLEAVED_RRGGBBAA_BE = 13
    """10 bit RGB BE with Alpha channel."""
    INTERLEAVED_RRGGBB_LE = 14
    """10 bit RGB LE."""
    INTERLEAVED_RRGGBBAA_LE = 15
    """10 bit RGB LE with Alpha channel."""


class HeifColorspace(IntEnum):
    """Colorspace format of the image."""

    UNDEFINED = 99
    """Undefined colorspace."""
    YCBCR = 0
    """https://en.wikipedia.org/wiki/YCbCr"""
    RGB = 1
    """RGB colorspace."""
    MONOCHROME = 2
    """Monochrome colorspace."""


class HeifCompressionFormat(IntEnum):
    """Possible LibHeif compression formats."""

    UNDEFINED = 0
    """The compression format is not defined."""
    HEVC = 1
    """The compression format is HEVC."""
    AVC = 2
    """The compression format is AVC."""
    JPEG = 3
    """The compression format is JPEG."""
    AV1 = 4
    """The compression format is AV1."""
    VVC = 5
    """The compression format is VVC."""
    EVC = 6
    """The compression format is EVC."""
    JPEG2000 = 7
    """The compression format is JPEG200 ISO/IEC 15444-16:2021"""
