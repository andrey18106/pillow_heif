#!/usr/bin/env python
"""Script to build wheel"""
from os import getenv
from sys import platform

from setuptools import Extension, setup

from libheif import build_helpers


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file, encoding="utf-8") as f:
        exec(compile(f.read(), version_file, "exec"))  # pylint: disable=exec-used
    return locals()["__version__"]


if not getenv("PRE_COMMIT", None):
    include_dirs, library_dirs = build_helpers.get_include_lib_dirs()

    setup(
        version=get_version(),
        ext_modules=[
            Extension(
                name="_pillow_heif",
                sources=["pillow_heif/_pillow_heif.c"],
                include_dirs=include_dirs,
                library_dirs=library_dirs,
                libraries=["libheif"] if platform.lower() == "win32" else ["heif"],
                extra_compile_args=["/d2FH4-"] if platform.lower() == "win32" else [],
            )
        ],
    )
else:
    setup(version=get_version())
