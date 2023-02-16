# This is temporary a temporary solution, in future this code will be moved to `setup.py`

import sys
from os import environ, getenv, path
from pathlib import Path
from shutil import copy
from subprocess import DEVNULL, PIPE, run
from warnings import warn

from libheif import linux_build_libs


def get_include_lib_dirs():
    include_dirs = ["/usr/local/include", "/usr/include"]
    library_dirs = ["/usr/local/lib", "/usr/lib64", "/usr/lib", "/lib"]

    print(environ)
    if sys.platform.lower() == "darwin":
        include_path_prefix = getenv("HOMEBREW_PREFIX")
        if not include_path_prefix:
            _result = run(["brew", "--prefix"], stderr=DEVNULL, stdout=PIPE, check=False)
            if not _result.returncode and _result.stdout is not None:
                include_path_prefix = _result.stdout.decode("utf-8").rstrip("\n")
        if not include_path_prefix:
            include_path_prefix = "/opt/local"
    elif sys.platform.lower() == "win32":
        include_path_prefix = getenv("MSYS2_PREFIX")
        if include_path_prefix is None:
            include_path_prefix = "C:\\msys64\\mingw64"
            warn(f"MSYS2_PREFIX environment variable is not set. Assuming `MSYS2_PREFIX={include_path_prefix}`")
    else:
        include_path_prefix = linux_build_libs.build_libs()

    # Need to include "lib" directory to find "heif" library.
    include_path_prefix_lib = path.join(include_path_prefix, "lib")
    if include_path_prefix_lib not in library_dirs:
        library_dirs.append(include_path_prefix_lib)

    # MSYS2: rename "libheif.dll.a" to "libheif.lib"
    if sys.platform.lower() == "win32":
        lib_export_file = Path(path.join(include_path_prefix_lib, "libheif.dll.a"))
        if lib_export_file.is_file():
            copy(lib_export_file, path.join(include_path_prefix_lib, "libheif.lib"))
        else:
            warn("If you build this with MSYS2, you should not see this warning.")

    # Adds project root to `include` path
    include_dirs.append(path.dirname(path.dirname(path.abspath(__file__))))
    return include_dirs, library_dirs
