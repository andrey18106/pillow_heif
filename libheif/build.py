# In future this file will be removed, after completely moving out from `cffi` usage.

import sys
from os import getenv
from re import sub

from cffi import FFI

from libheif import build_helpers

ffi = FFI()
with open("libheif/public_api.h", "r", encoding="utf-8") as f:
    libheif_definitions = f.read()
    if getenv("READTHEDOCS", "False") == "True":
        # As ReadTheDocs has pre-installed libheif.so and we do not have root privileges to uninstall it
        # remove lines from `public_api.h` with `REMOVE_FOR_RTD` string.
        libheif_definitions = sub(r".*REMOVE_FOR_RTD\n?", "", libheif_definitions)
    ffi.cdef(libheif_definitions)

ffi.cdef(
    """
    extern "Python" struct heif_error callback_write(struct heif_context*, const void*, size_t, void*);
"""
)

with open("pillow_heif/helpers.h", "r", encoding="utf-8") as f:
    ffi.cdef(f.read())

include_dirs, library_dirs = build_helpers.get_include_lib_dirs()

ffi.set_source(
    "_pillow_heif_cffi",
    r"""
    #include "libheif/public_api.h"
    #include "pillow_heif/helpers.c"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["libheif"] if sys.platform.lower() == "win32" else ["heif"],
    extra_compile_args=["/d2FH4-"] if sys.platform.lower() == "win32" else [],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
