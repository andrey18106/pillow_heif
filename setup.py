#!/usr/bin/env python
"""Script to build wheel"""
import sys
from os import environ, getenv, path
from pathlib import Path
from re import finditer
from shutil import copy
from subprocess import check_output
from typing import List
from warnings import warn

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from libheif import linux_build_libs


def get_version():
    version_file = "pillow_heif/_version.py"
    with open(version_file, encoding="utf-8") as f:
        exec(compile(f.read(), version_file, "exec"))  # pylint: disable=exec-used
    return locals()["__version__"]


class PillowHeifBuildExt(build_ext):
    """This class is based on the Pillow setup method as I understand it (I'm a noob at this)"""

    def build_extensions(self):  # pylint: disable=too-many-branches
        if getenv("PRE_COMMIT"):
            return

        include_dirs = []
        library_dirs = []

        # respect CFLAGS/CPPFLAGS/LDFLAGS (taken from Pillow)
        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in environ:
                for match in finditer(r"-I([^\s]+)", environ[k]):
                    self._add_directory(include_dirs, match.group(1))
                for match in finditer(r"-L([^\s]+)", environ[k]):
                    self._add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables(taken from Pillow):
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in environ:
                for d in environ[k].split(path.pathsep):
                    self._add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):  # taken from Pillow
            if k in environ:
                for d in environ[k].split(path.pathsep):
                    self._add_directory(library_dirs, d)

        self._add_directory(include_dirs, path.join(sys.prefix, "include"))
        self._add_directory(library_dirs, path.join(sys.prefix, "lib"))

        if sys.platform.lower() == "win32":
            # Currently only MSYS2 is supported for Windows systems. Do a PR if you need support for anything else.
            include_path_prefix = getenv("LIBHEIF_PATH_PREFIX")
            if include_path_prefix is None:
                include_path_prefix = "C:\\msys64\\mingw64"
                warn(f"MSYS2_PREFIX environment variable is not set. Assuming `MSYS2_PREFIX={include_path_prefix}`")

            if not path.isdir(include_path_prefix):
                raise ValueError("MSYS2 not found and `LIBHEIF_PATH_PREFIX` is not set or is invalid.")

            library_dir = path.join(include_path_prefix, "lib")
            # self._add_directory(include_dirs, path.join(include_path_prefix, "include"))
            self._add_directory(library_dirs, library_dir)
            lib_export_file = Path(path.join(library_dir, "libheif.dll.a"))
            if lib_export_file.is_file():
                copy(lib_export_file, path.join(library_dir, "libheif.lib"))
            else:
                warn("If you build this with MSYS2, you should not see this warning.")

            self._update_extension(
                "_pillow_heif", ["libheif"], extra_compile_args=["/d2FH4-", "/WX"], extra_link_args=["/WX"]
            )
        elif sys.platform.lower() == "darwin":
            # if Homebrew is installed, use its lib and include directories
            try:
                homebrew_prefix = check_output(["brew", "--prefix"]).strip().decode("latin1")
            except Exception:  # noqa # pylint: disable=broad-except
                # Homebrew not installed
                homebrew_prefix = None
            if homebrew_prefix:
                # add Homebrew's include and lib directories
                self._add_directory(library_dirs, path.join(homebrew_prefix, "lib"))
                self._add_directory(include_dirs, path.join(homebrew_prefix, "include"))

            # fink installation directories
            self._add_directory(library_dirs, "/sw/lib")
            self._add_directory(include_dirs, "/sw/include")
            # darwin ports installation directories
            self._add_directory(library_dirs, "/opt/local/lib")
            self._add_directory(include_dirs, "/opt/local/include")

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-Ofast", "-Werror"])
        else:  # let's assume it's some kind of linux
            include_path_prefix = linux_build_libs.build_libs()  # this need a rework in the future
            self._add_directory(library_dirs, path.join(include_path_prefix, "lib"))
            self._add_directory(include_dirs, path.join(include_path_prefix, "include"))

            self._update_extension("_pillow_heif", ["heif"], extra_compile_args=["-Ofast", "-Werror"])

        # Here opposite what Pillow do in their code, we DO NOT WANT to take priority over default directories.
        self.compiler.library_dirs = self.compiler.library_dirs + library_dirs
        self.compiler.include_dirs = self.compiler.include_dirs + include_dirs

        self.compiler.include_dirs.append(path.dirname(path.abspath(__file__)))

        super().build_extensions()

    def _update_extension(self, name, libraries, extra_compile_args=None, extra_link_args=None):
        for extension in self.extensions:
            if extension.name == name:
                extension.libraries += libraries
                if extra_compile_args is not None:
                    extension.extra_compile_args += extra_compile_args
                if extra_link_args is not None:
                    extension.extra_link_args += extra_link_args

    @staticmethod
    def _add_directory(paths: List, subdir):
        if subdir:
            subdir = path.realpath(subdir)
            if path.isdir(subdir) and subdir not in paths:
                paths.append(subdir)


setup(
    version=get_version(),
    cmdclass={"build_ext": PillowHeifBuildExt},
    ext_modules=[Extension("_pillow_heif", ["pillow_heif/_pillow_heif.c"])],
)
