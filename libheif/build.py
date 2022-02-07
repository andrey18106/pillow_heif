from os import getenv, path
from sys import platform
from subprocess import run, DEVNULL, PIPE
from cffi import FFI

ffibuilder = FFI()


with open("libheif/heif.h", "r", encoding="utf-8") as f:
    ffibuilder.cdef(f.read())


include_dirs = ["/usr/local/include", "/usr/include", "/opt/local/include"]
library_dirs = ["/usr/local/lib", "/usr/lib", "/lib", "/opt/local/lib"]

if platform.lower() == "darwin":
    homebrew_prefix = getenv("HOMEBREW_PREFIX")
    if not homebrew_prefix:
        _result = run(["brew", "--prefix"], stderr=DEVNULL, stdout=PIPE, check=False)
        if not _result.returncode and _result.stdout is not None:
            homebrew_prefix = _result.stdout.decode("utf-8").rstrip("\n")
    if homebrew_prefix:
        homebrew_include = path.join(homebrew_prefix, "include")
        if homebrew_include not in include_dirs:
            include_dirs.append(homebrew_include)
        homebrew_library = path.join(homebrew_prefix, "lib")
        if homebrew_library not in library_dirs:
            library_dirs.append(homebrew_library)
if platform.lower() == "win32":
    libheif_path = getenv("PH_LIBHEIF_PATH")
    if libheif_path:
        a = path.join(libheif_path, "include")
        if a not in include_dirs:
            print(f"Adding {a}")
            include_dirs.append(a)
        a = path.join(libheif_path, "lib")
        if a not in library_dirs:
            print(f"Adding {a}")
            library_dirs.append(a)
if platform.lower() in ("darwin", "win32"):
    project_root = path.dirname(path.dirname(path.abspath(__file__)))
    include_dirs.append(project_root)


ffibuilder.set_source(
    "pillow_heif._libheif",
    """
     #include "libheif/heif.h"
    """,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["heif"],
    extra_compile_args=["/d2FH4-"] if platform.lower() == "win32" else [],
    extra_link_args=["/VERBOSE:LIB"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
