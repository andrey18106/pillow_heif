"""
Callback functions and classes for libheif `heif_context_read_from_reader` and `heif_context_write`.
"""

import builtins
from io import SEEK_END, SEEK_SET, BytesIO
from pathlib import Path
from typing import List, Tuple

from _pillow_heif_cffi import ffi, lib

from ._options import options
from .constants import HeifCompressionFormat
from .error import check_libheif_error
from .misc import _get_bytes, get_file_mimetype


class LibHeifCtx:
    """LibHeif reader context"""

    def __init__(self, fp, to_8bit: bool = False):
        self._fp_close_after = False
        self.to_8bit = to_8bit
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        if options().ctx_in_memory:
            self.fp = None
            self.c_userdata = None
            if hasattr(fp, "seek"):
                fp.seek(0, SEEK_SET)
            self.reader = _get_bytes(fp)
            error = lib.heif_context_read_from_memory_without_copy(self.ctx, self.reader, len(self.reader), ffi.NULL)
        else:
            self.fp = self._get_fp(fp)
            self.fp.seek(0, SEEK_SET)
            self.c_userdata = ffi.new_handle(self.fp)
            self.reader = self._get_libheif_reader()
            error = lib.heif_context_read_from_reader(self.ctx, self.reader, self.c_userdata, ffi.NULL)
        check_libheif_error(error)

    def get_main_img_id(self) -> int:
        p_main_image_id = ffi.new("heif_item_id *")
        check_libheif_error(lib.heif_context_get_primary_image_ID(self.ctx, p_main_image_id))
        return p_main_image_id[0]

    def get_top_images_ids(self) -> list:
        top_img_count = lib.heif_context_get_number_of_top_level_images(self.ctx)
        top_img_ids = ffi.new("heif_item_id[]", top_img_count)
        top_img_count = lib.heif_context_get_list_of_top_level_image_IDs(self.ctx, top_img_ids, top_img_count)
        return [top_img_ids[i] for i in range(top_img_count)]

    def get_mimetype(self) -> str:
        mimetype = ""
        if isinstance(self.reader, bytes):
            mimetype = get_file_mimetype(self.reader)
        elif self.fp:
            old_position = self.fp.tell()
            self.fp.seek(0, SEEK_SET)
            mimetype = get_file_mimetype(self.fp)
            self.fp.seek(old_position, SEEK_SET)
        return mimetype

    def __del__(self):
        if self._fp_close_after and self.fp and hasattr(self.fp, "close"):
            self.fp.close()
        self.fp = None

    def _get_fp(self, fp):
        if hasattr(fp, "read") and hasattr(fp, "tell") and hasattr(fp, "seek"):
            return fp
        self._fp_close_after = True
        if isinstance(fp, (str, Path)):
            return builtins.open(fp, "rb")
        return BytesIO(fp)

    @staticmethod
    def _get_libheif_reader():
        libheif_reader = ffi.new("struct heif_reader *")
        libheif_reader.reader_api_version = 1
        libheif_reader.get_position = lib.callback_tell
        libheif_reader.read = lib.callback_read
        libheif_reader.seek = lib.callback_seek
        libheif_reader.wait_for_file_size = lib.callback_wait_for_file_size
        return libheif_reader


class LibHeifCtxWrite:
    """LibHeif writer context"""

    def __init__(self, compression_format: int = HeifCompressionFormat.HEVC):
        self.ctx = ffi.gc(lib.heif_context_alloc(), lib.heif_context_free)
        p_encoder = ffi.new("struct heif_encoder **")
        error = lib.heif_context_get_encoder_for_format(self.ctx, compression_format, p_encoder)
        check_libheif_error(error)
        self.encoder = ffi.gc(p_encoder[0], lib.heif_encoder_release)
        # lib.heif_encoder_set_logging_level(self.encoder, 4)

    def set_encoder_parameters(self, enc_params: List[Tuple[str, str]], quality: int = None):
        if quality is not None:
            if quality == -1:
                check_libheif_error(lib.heif_encoder_set_lossless(self.encoder, True))
            else:
                check_libheif_error(lib.heif_encoder_set_lossy_quality(self.encoder, quality))
        for param in enc_params:
            check_libheif_error(
                lib.heif_encoder_set_parameter(self.encoder, param[0].encode("ascii"), param[1].encode("ascii"))
            )

    def write(self, fp):
        __fp = self._get_fp(fp)
        c_userdata = ffi.new_handle(__fp)
        error = lib.heif_context_write(self.ctx, self._get_heif_writer(), c_userdata)
        if isinstance(fp, (str, Path)):
            __fp.close()
        check_libheif_error(error)

    @staticmethod
    def _get_fp(fp):
        if isinstance(fp, (str, Path)):
            return builtins.open(fp, "wb")
        if hasattr(fp, "write"):
            return fp
        raise TypeError("`fp` must be a path to file or and object with `write` method.")

    @staticmethod
    def _get_heif_writer():
        heif_writer = ffi.new("struct heif_writer *")
        heif_writer.writer_api_version = 1
        heif_writer.write = lib.callback_write
        return heif_writer


@ffi.def_extern()
def callback_tell(userdata):
    fp = ffi.from_handle(userdata)
    return fp.tell() if fp and not fp.closed else 0


@ffi.def_extern()
def callback_seek(position, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        fp.seek(position)
    return 0


@ffi.def_extern()
def callback_read(data, size, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        read_data = fp.read(size)
        ffi.memmove(data, read_data, len(read_data))
    return 0


@ffi.def_extern()
def callback_write(_ctx, data, size, userdata):
    fp = ffi.from_handle(userdata)
    if fp and not fp.closed:
        fp.write(ffi.buffer(data, size=size))
    return [0, 0, ffi.NULL]


@ffi.def_extern()
def callback_wait_for_file_size(target_size, userdata):
    fp = ffi.from_handle(userdata)
    fp_size = 0
    if fp and not fp.closed:
        fp_current = fp.tell()
        fp_size = fp.seek(0, SEEK_END)
        fp.seek(fp_current, SEEK_SET)
    return 2 if target_size > fp_size else 0
