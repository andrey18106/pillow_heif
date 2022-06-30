"""
Undocumented private functions for other code to look better.
"""

from math import ceil
from typing import Union

from _pillow_heif_cffi import ffi, lib

from ._libheif_ctx import LibHeifCtxWrite
from .constants import HeifChroma, HeifColorProfileType, HeifColorspace
from .error import check_libheif_error

FFI_DRY_ALLOC = ffi.new_allocator(should_clear_after_alloc=False)


# from dataclasses import dataclass
# @dataclass                # Avalaible from Python 3.7
class HeifCtxAsDict:  # noqa # pylint: disable=too-few-public-methods
    """Representation of one image"""

    def __init__(self, mode: str, size: tuple, data, **kwargs):
        stride = kwargs.get("stride", None)
        if stride is None:
            stride = get_pure_stride(mode, size[0])
        self.mode = mode
        self.size = size
        self.data = data
        self.stride = stride
        self.additional_info = kwargs.get("add_info", {})


def get_pure_stride(mode: str, width: int):
    return width * MODE_INFO[mode][0] * ceil(MODE_INFO[mode][1] / 8)


def convert_i16_to_i10(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    lib.convert_i16_to_i10(p_src, source_stride, p_dest, dest_stride, height, stride_elements)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def convert_bgr16_to_rgb10(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 2] >> 6
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] >> 6
            dest_row[i * 3 + 2] = source_row[i * 3 + 0] >> 6


def convert_bgra16_to_rgba10(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 2] >> 6
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] >> 6
            dest_row[i * 4 + 2] = source_row[i * 4 + 0] >> 6
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] >> 6


def convert_rgb16_to_rgb10(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 0] >> 6
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] >> 6
            dest_row[i * 3 + 2] = source_row[i * 3 + 2] >> 6


def convert_rgba16_to_rgba10(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 0] >> 6
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] >> 6
            dest_row[i * 4 + 2] = source_row[i * 4 + 2] >> 6
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] >> 6


def convert_rgba12_to_rgba16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 0] << 4
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] << 4
            dest_row[i * 4 + 2] = source_row[i * 4 + 2] << 4
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] << 4


def convert_rgba12_to_bgra16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 2] << 4
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] << 4
            dest_row[i * 4 + 2] = source_row[i * 4 + 0] << 4
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] << 4


def convert_rgb12_to_rgb16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 0] << 4
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] << 4
            dest_row[i * 3 + 2] = source_row[i * 3 + 2] << 4


def convert_rgb12_to_bgr16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 2] << 4
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] << 4
            dest_row[i * 3 + 2] = source_row[i * 3 + 0] << 4


def convert_rgba10_to_rgba16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 0] << 6
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] << 6
            dest_row[i * 4 + 2] = source_row[i * 4 + 2] << 6
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] << 6


def convert_rgba10_to_bgra16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 4)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 4 + 0] = source_row[i * 4 + 2] << 6
            dest_row[i * 4 + 1] = source_row[i * 4 + 1] << 6
            dest_row[i * 4 + 2] = source_row[i * 4 + 0] << 6
            dest_row[i * 4 + 3] = source_row[i * 4 + 3] << 6


def convert_rgb10_to_rgb16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 0] << 6
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] << 6
            dest_row[i * 3 + 2] = source_row[i * 3 + 2] << 6


def convert_rgb10_to_bgr16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_source = ffi.from_buffer("uint16_t*", src_data)
    source_stride = int(source_stride / 2)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = min(source_stride, dest_stride)
    stride_elements = int(stride_elements / 3)
    for i_row in range(height):
        source_row = p_source + source_stride * i_row
        dest_row = p_dest + dest_stride * i_row
        for i in range(stride_elements):
            dest_row[i * 3 + 0] = source_row[i * 3 + 2] << 6
            dest_row[i * 3 + 1] = source_row[i * 3 + 1] << 6
            dest_row[i * 3 + 2] = source_row[i * 3 + 0] << 6


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def convert_rgba_to_rgba16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = int(min(source_stride, dest_stride) / 4)
    lib.convert_rgba_to_rgba16(p_src, source_stride, p_dest, dest_stride, height, stride_elements)


def convert_rgba_to_bgra16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = int(min(source_stride, dest_stride) / 4)
    lib.convert_rgba_to_bgra16(p_src, source_stride, p_dest, dest_stride, height, stride_elements)


def convert_rgb_to_rgb16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = int(min(source_stride, dest_stride) / 3)
    lib.convert_rgb_to_rgb16(p_src, source_stride, p_dest, dest_stride, height, stride_elements)


def convert_rgb_to_bgr16(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    p_dest = ffi.cast("uint16_t*", dest_data)
    dest_stride = int(dest_stride / 2)
    stride_elements = int(min(source_stride, dest_stride) / 3)
    lib.convert_rgb_to_bgr16(p_src, source_stride, p_dest, dest_stride, height, stride_elements)


def convert_between_bgra_and_rgba(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    stride_elements = int(min(source_stride, dest_stride) / 4)
    lib.convert_bgra_rgba(p_src, source_stride, dest_data, dest_stride, height, stride_elements)


def convert_between_bgr_and_rgb(dest_data, src_data, dest_stride: int, source_stride: int, height: int):
    p_src = ffi.from_buffer("uint8_t*", src_data)
    stride_elements = int(min(source_stride, dest_stride) / 3)
    lib.convert_bgr_rgb(p_src, source_stride, dest_data, dest_stride, height, stride_elements)


MODE_CONVERT = {
    # source_mode: {target_mode: convert_function,}
    "BGRA;16": {"RGBA;10": convert_bgra16_to_rgba10},
    "BGR;16": {"RGB;10": convert_bgr16_to_rgb10},
    "RGBA;16": {"RGBA;10": convert_rgba16_to_rgba10},
    "RGB;16": {"RGB;10": convert_rgb16_to_rgb10},
    "L;16": {"L;10": convert_i16_to_i10},
    "I;16": {"L;10": convert_i16_to_i10},
    "I;16L": {"L;10": convert_i16_to_i10},
    "RGBA;12": {"RGBA;16": convert_rgba12_to_rgba16, "BGRA;16": convert_rgba12_to_bgra16},
    "RGB;12": {"RGB;16": convert_rgb12_to_rgb16, "BGR;16": convert_rgb12_to_bgr16},
    "RGBA;10": {"RGBA;16": convert_rgba10_to_rgba16, "BGRA;16": convert_rgba10_to_bgra16},
    "RGB;10": {"RGB;16": convert_rgb10_to_rgb16, "BGR;16": convert_rgb10_to_bgr16},
    "BGRA": {"RGBA": convert_between_bgra_and_rgba},
    "BGR": {"RGB": convert_between_bgr_and_rgb},
    "RGBA": {
        "BGRA": convert_between_bgra_and_rgba,
        "RGBA;16": convert_rgba_to_rgba16,
        "BGRA;16": convert_rgba_to_bgra16,
    },
    "RGB": {"BGR": convert_between_bgr_and_rgb, "RGB;16": convert_rgb_to_rgb16, "BGR;16": convert_rgb_to_bgr16},
}


MODE_INFO = {
    # name -> (channels, bits per pixel channel, colorspace, chroma, mode_for_saving, numpy_typestr)
    "BGRA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, "RGBA;10", "<u2"),
    "BGR;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, "RGB;10", "<u2"),
    "RGBA;16": (4, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, "RGBA;10", "<u2"),
    "RGB;16": (3, 16, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, "RGB;10", "<u2"),
    "L;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, "L;10", "<u2"),
    "I;16": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, "L;10", "<u2"),
    "I;16L": (1, 16, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, "L;10", "<u2"),
    "RGBA;12": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGB;12": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, None, "<u2"),
    "RGBA;12B": (4, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGB;12B": (3, 12, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_BE, None, ">u2"),
    "L;12": (1, 12, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "<u2"),
    "RGBA;10": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_LE, None, "<u2"),
    "RGB;10": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_LE, None, "<u2"),
    "RGBA;10B": (4, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBBAA_BE, None, ">u2"),
    "RGB;10B": (3, 10, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RRGGBB_BE, None, ">u2"),
    "L;10": (1, 10, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "<u2"),
    "RGBA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, None, "|u1"),
    "RGB": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB, None, "|u1"),
    "BGRA": (4, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGBA, "RGBA", "|u1"),
    "BGR": (3, 8, HeifColorspace.RGB, HeifChroma.INTERLEAVED_RGB, "RGB", "|u1"),
    "L": (1, 8, HeifColorspace.MONOCHROME, HeifChroma.MONOCHROME, None, "|u1"),
    "": (0, 0, HeifColorspace.UNDEFINED, HeifChroma.UNDEFINED, None, ""),
}


def read_color_profile(handle) -> dict:
    profile_type = lib.heif_image_handle_get_color_profile_type(handle)
    if profile_type == HeifColorProfileType.NOT_PRESENT:
        return {}
    if profile_type == HeifColorProfileType.NCLX:
        _type = "nclx"
        pp_data = ffi.new("struct heif_color_profile_nclx **")
        data_length = ffi.sizeof("struct heif_color_profile_nclx")
        error = lib.heif_image_handle_get_nclx_color_profile(handle, pp_data)
        p_data = pp_data[0]
        ffi.release(pp_data)
    else:
        _type = "prof" if profile_type == HeifColorProfileType.PROF else "rICC"
        data_length = lib.heif_image_handle_get_raw_color_profile_size(handle)
        if data_length == 0:
            return {"type": _type, "data": b""}
        p_data = ffi.new("char[]", data_length)
        error = lib.heif_image_handle_get_raw_color_profile(handle, p_data)
    check_libheif_error(error)
    data_buffer = ffi.buffer(p_data, data_length)
    return {"type": _type, "data": bytes(data_buffer)}


def set_color_profile(heif_img, info: dict) -> None:
    __icc_profile = info.get("icc_profile", None)
    if __icc_profile is not None:
        _prof_type = info.get("icc_profile_type", "prof").encode("ascii")
        error = lib.heif_image_set_raw_color_profile(
            heif_img, _prof_type, info["icc_profile"], len(info["icc_profile"])
        )
        check_libheif_error(error)
    elif info.get("nclx_profile", None):
        error = lib.heif_image_set_nclx_color_profile(
            heif_img,
            ffi.cast("const struct heif_color_profile_nclx*", ffi.from_buffer(info["nclx_profile"])),
        )
        check_libheif_error(error)


def retrieve_exif(metadata: list):
    _result = None
    _purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "Exif":
            _purge.append(i)
            if not _result and md_block["data"] and md_block["data"][0:4] == b"Exif":
                _result = md_block["data"]
    for i in reversed(_purge):
        del metadata[i]
    return _result


def set_exif(ctx: LibHeifCtxWrite, heif_img_handle, exif: Union[bytes, None]) -> None:
    if exif is not None:
        error = lib.heif_context_add_exif_metadata(ctx.ctx, heif_img_handle, exif, len(exif))
        check_libheif_error(error)


def retrieve_xmp(metadata: list):
    _result = None
    _purge = []
    for i, md_block in enumerate(metadata):
        if md_block["type"] == "mime":
            _purge.append(i)
            if not _result:
                _result = md_block["data"]
    for i in reversed(_purge):
        del metadata[i]
    return _result


def set_xmp(ctx: LibHeifCtxWrite, heif_img_handle, xmp: Union[bytes, None]) -> None:
    if xmp is not None:
        error = lib.heif_context_add_XMP_metadata(ctx.ctx, heif_img_handle, xmp, len(xmp))
        check_libheif_error(error)


def read_metadata(handle) -> list:
    block_count = lib.heif_image_handle_get_number_of_metadata_blocks(handle, ffi.NULL)
    if block_count == 0:
        return []
    metadata = []
    blocks_ids = ffi.new("heif_item_id[]", block_count)
    lib.heif_image_handle_get_list_of_metadata_block_IDs(handle, ffi.NULL, blocks_ids, block_count)
    for block_id in blocks_ids:
        metadata_type = lib.heif_image_handle_get_metadata_type(handle, block_id)
        decoded_data_type = ffi.string(metadata_type).decode()
        content_type = ffi.string(lib.heif_image_handle_get_metadata_content_type(handle, block_id))
        data_length = lib.heif_image_handle_get_metadata_size(handle, block_id)
        if data_length > 0:
            p_data = ffi.new("char[]", data_length)
            error = lib.heif_image_handle_get_metadata(handle, block_id, p_data)
            check_libheif_error(error)
            data_buffer = ffi.buffer(p_data, data_length)
            data = bytes(data_buffer)
            if decoded_data_type == "Exif":
                data = data[4:]  # skip TIFF header, first 4 bytes
            metadata.append(
                {"type": decoded_data_type, "data": data, "metadata_type": metadata_type, "content_type": content_type}
            )
    return metadata


def set_metadata(ctx: LibHeifCtxWrite, heif_img_handle, info: dict) -> None:
    for metadata in info["metadata"]:
        error = lib.heif_context_add_generic_metadata(
            ctx.ctx,
            heif_img_handle,
            metadata["data"],
            len(metadata["data"]),
            metadata["metadata_type"],
            metadata["content_type"],
        )
        check_libheif_error(error)
